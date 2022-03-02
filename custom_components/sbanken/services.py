""" easee services."""
import logging

import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.util import dt
from .sbankenApi import SbankenApi
from .const import DOMAIN, ATTR_ACCOUNT_ID

_LOGGER = logging.getLogger(__name__)

# ACCESS_LEVEL = "access_level"
# CHARGER_ID = "charger_id"
# CIRCUIT_ID = "circuit_id"
# ATTR_CHARGEPLAN_START_DATETIME = "start_datetime"
# ATTR_CHARGEPLAN_STOP_DATETIME = "stop_datetime"
# ATTR_CHARGEPLAN_REPEAT = "repeat"
# ATTR_SET_CURRENT = "current"
# ATTR_SET_CURRENTP1 = "currentP1"
# ATTR_SET_CURRENTP2 = "currentP2"
# ATTR_SET_CURRENTP3 = "currentP3"
# ATTR_COST_PER_KWH = "cost_per_kwh"
# ATTR_COST_CURRENCY = "currency_id"
# ATTR_COST_VAT = "vat"
# ATTR_ENABLE = "enable"
ATTR_AMOUNT = "amount"
ATTR_FROM_ACCOUNT_ENTITY = "from_account_entity"
ATTR_TO_ACCOUNT_ENTITY = "to_account_entity"
ATTR_MESSAGE = "message"


SERVICE_TRANSFER_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_FROM_ACCOUNT_ENTITY): cv.string,
        vol.Required(ATTR_TO_ACCOUNT_ENTITY): cv.string,
        vol.Required(ATTR_AMOUNT): vol.Coerce(float),
        vol.Required(ATTR_MESSAGE): cv.string,
    }
)


SERVICE_MAP = {
    "transfer": {
        "handler": "transfer_service",
        "function_call": "transfer",
        "schema": SERVICE_TRANSFER_SCHEMA,
    },
}


async def async_setup_services(hass: HomeAssistant, client_id: str, secret: str):
    """Setup services for Sbanken."""

    async def transfer_service(call):
        """Execute a service to Sbanken."""
        _LOGGER.info(f"Handle transfers: {str(call.data)}")

        from_account_entity = call.data.get(ATTR_FROM_ACCOUNT_ENTITY)
        to_account_entity = call.data.get(ATTR_TO_ACCOUNT_ENTITY)
        amount = call.data.get(ATTR_AMOUNT)
        message = call.data.get(ATTR_MESSAGE)

        if ATTR_ACCOUNT_ID not in hass.states.get(from_account_entity).attributes:
            raise HomeAssistantError(
                f"Could not find account id for entity {from_account_entity}"
            )
        from_account_id = hass.states.get(from_account_entity).attributes[
            ATTR_ACCOUNT_ID
        ]

        if ATTR_ACCOUNT_ID not in hass.states.get(to_account_entity).attributes:
            raise HomeAssistantError(
                f"Could not find account id for entity {to_account_entity}"
            )
        to_account_id = hass.states.get(to_account_entity).attributes[ATTR_ACCOUNT_ID]

        api = SbankenApi()
        session = await hass.async_add_executor_job(
            api.create_session, client_id, secret
        )
        transfer = await hass.async_add_executor_job(
            api.transfer, session, from_account_id, to_account_id, amount, message
        )

        return transfer
        # enable = call.data.get(ATTR_ENABLE, None)

        # _LOGGER.debug("execute_service: %s %s", str(call.service), str(call.data))

        # # Possibly move to use entity id later
        # charger = next((c for c in chargers if c.id == charger_id), None)
        # if charger:
        #     function_name = SERVICE_MAP[call.service]
        #     function_call = getattr(charger, function_name["function_call"])
        #     try:
        #         if enable is not None:
        #             return await function_call(enable)
        #         else:
        #             return await function_call()
        #     except Exception:
        #         _LOGGER.error(
        #             "Failed to execute service: %s with data %s",
        #             str(call.service),
        #             str(call.data),
        #         )
        #         return

        # _LOGGER.error("Could not find charger %s", charger_id)
        # raise HomeAssistantError("Could not find charger {}".format(charger_id))

        # """Execute a service to set access level on a charger"""
        # charger_id = call.data.get(CHARGER_ID)
        # access_level = call.data.get(ACCESS_LEVEL)

        # _LOGGER.debug("execute_service: %s %s", str(call.service), str(call.data))

        # charger = next((c for c in chargers if c.id == charger_id), None)
        # if charger:
        #     function_name = SERVICE_MAP[call.service]
        #     function_call = getattr(charger, function_name["function_call"])
        #     try:
        #         return await function_call(access_level)
        #     except Exception:
        #         _LOGGER.error(
        #             "Failed to execute service: %s with data %s",
        #             str(call.service),
        #             str(call.data),
        #         )
        #         return

    for service in SERVICE_MAP:
        data = SERVICE_MAP[service]
        handler = locals()[data["handler"]]
        hass.services.async_register(DOMAIN, service, handler, schema=data["schema"])
