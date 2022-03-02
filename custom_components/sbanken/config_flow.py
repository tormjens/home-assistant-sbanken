"""Config flow for Sbanken integration."""
from __future__ import annotations
import logging
import voluptuous as vol
from typing import Any
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.core import callback
from .sbankenApi import SbankenApi
from .const import (
    DOMAIN,
    CONF_CLIENT_ID,
    CONF_NUMBER_OF_TRANSACTIONS,
    CONF_SECRET,
    TITLE,
    CannotConnect,
    InvalidAuth,
)


_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_CLIENT_ID): str,
        vol.Required(CONF_SECRET): str,
        vol.Required(CONF_NUMBER_OF_TRANSACTIONS, default=10): int,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""

    api = SbankenApi()
    session = await hass.async_add_executor_job(
        api.create_session, data[CONF_CLIENT_ID], data[CONF_SECRET]
    )
    if not session.authorized:
        raise InvalidAuth

    return {"title": TITLE}


@config_entries.HANDLERS.register(DOMAIN)
class SbankenConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Sbanken."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(
                title=info["title"],
                data=user_input,
                options=user_input,
            )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return SbankenOptionsFlowHandler(config_entry)


class SbankenOptionsFlowHandler(config_entries.OptionsFlow):
    """Sbanken config flow options handler."""

    def __init__(self, config_entry):
        self.options = config_entry.options
        self.data = config_entry.data

    async def async_step_init(self, _user_input=None):
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""
        errors = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(
                            CONF_CLIENT_ID,
                            default=user_input[CONF_CLIENT_ID],
                        ): str,
                        vol.Required(
                            CONF_SECRET,
                            default=user_input[CONF_SECRET],
                        ): str,
                        vol.Required(
                            CONF_NUMBER_OF_TRANSACTIONS,
                            default=user_input[CONF_NUMBER_OF_TRANSACTIONS],
                        ): int,
                    }
                ),
                errors=errors,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_CLIENT_ID,
                        default=self.options.get(CONF_CLIENT_ID),
                    ): str,
                    vol.Required(
                        CONF_SECRET,
                        default=self.options.get(CONF_SECRET),
                    ): str,
                    vol.Required(
                        CONF_NUMBER_OF_TRANSACTIONS,
                        default=self.options.get(CONF_NUMBER_OF_TRANSACTIONS),
                    ): int,
                }
            ),
        )
