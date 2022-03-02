"""Sbanken accounts sensor."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .sbankenApi import SbankenApi
from homeassistant.helpers.entity import Entity
from datetime import datetime, timedelta
from .const import (
    CONF_CLIENT_ID,
    CONF_NUMBER_OF_TRANSACTIONS,
    CONF_SECRET,
    DOMAIN,
    ATTR_ACCOUNT_ID,
    ATTR_ACCOUNT_LIMIT,
    ATTR_ACCOUNT_NUMBER,
    ATTR_ACCOUNT_TYPE,
    ATTR_AVAILABLE,
    ATTR_BALANCE,
    ATTR_LAST_UPDATE,
    ATTR_NAME,
    ATTR_PAYMENTS,
    ATTR_STANDING_ORDERS,
    ATTR_TRANSACTIONS,
)

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=300)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Setup sensor platform."""
    api = SbankenApi()
    session = await hass.async_add_executor_job(
        api.create_session,
        entry.options.get(CONF_CLIENT_ID),
        entry.options.get(CONF_SECRET),
    )
    accounts = await hass.async_add_executor_job(api.get_accounts, session)
    sensors = [
        SbankenAccountSensor(
            account,
            api,
            entry.options,
            hass,
        )
        for account in accounts
    ]
    async_add_entities(sensors, update_before_add=True)


class SbankenAccountSensor(Entity):
    """Representation of a Sensor."""

    def __init__(
        self,
        account,
        api: SbankenApi,
        options,
        hass: HomeAssistant,
    ) -> None:
        """Initialize the sensor."""
        self.api = api
        self.number_of_transactions = options.get(CONF_NUMBER_OF_TRANSACTIONS)
        self.client_id = options.get(CONF_CLIENT_ID)
        self.secret = options.get(CONF_SECRET)
        self.hass = hass
        self._account = account
        self._transactions = []
        self._payments = []
        self._standing_orders = []
        self._state = account["available"]
        self._attr_state_class = "monetary"

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return self._account["accountNumber"]

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._account["name"] + " (" + self._account["accountNumber"] + ")"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "NOK"

    @property
    def should_poll(self):
        """Should poll periodically."""
        return True

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return "mdi:cash"

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            ATTR_ACCOUNT_ID: self._account["accountId"],
            ATTR_AVAILABLE: self._account["available"],
            ATTR_BALANCE: self._account["balance"],
            ATTR_ACCOUNT_NUMBER: self._account["accountNumber"],
            ATTR_NAME: self._account["name"],
            ATTR_ACCOUNT_TYPE: self._account["accountType"],
            ATTR_ACCOUNT_LIMIT: self._account["creditLimit"],
            ATTR_LAST_UPDATE: datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            ATTR_TRANSACTIONS: self._transactions,
            ATTR_PAYMENTS: self._payments,
            ATTR_STANDING_ORDERS: self._standing_orders,
        }

    async def async_update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        session = await self.hass.async_add_executor_job(
            self.api.create_session,
            self.client_id,
            self.secret,
        )
        account = await self.hass.async_add_executor_job(
            self.api.get_account, session, self._account["accountId"]
        )
        transactions = await self.hass.async_add_executor_job(
            self.api.get_transactions,
            session,
            self._account["accountId"],
            self.number_of_transactions,
        )
        payments = await self.hass.async_add_executor_job(
            self.api.get_payments,
            session,
            self._account["accountId"],
            self.number_of_transactions,
        )

        standing_orders = await self.hass.async_add_executor_job(
            self.api.get_standingOrders, session, self._account["accountId"]
        )

        self._transactions = transactions
        self._payments = payments
        self._account = account
        self._standing_orders = standing_orders
        self._state = account["available"]
        _LOGGER.info("Updating Sbanken Sensors")
