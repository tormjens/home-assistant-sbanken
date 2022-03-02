"""Constants for the SBanken integration."""

from homeassistant.exceptions import HomeAssistantError


DOMAIN = "sbanken"
TITLE = "Sbanken"
CONF_CLIENT_ID = "client_id"
CONF_SECRET = "secret"
CONF_NUMBER_OF_TRANSACTIONS = "numberOfTransactions"
ATTR_AVAILABLE = "available"
ATTR_BALANCE = "balance"
ATTR_ACCOUNT_NUMBER = "account_number"
ATTR_NAME = "name"
ATTR_ACCOUNT_TYPE = "account_type"
ATTR_ACCOUNT_LIMIT = "credit_limit"
ATTR_ACCOUNT_ID = "account_id"
ATTR_LAST_UPDATE = "last_update"
ATTR_TRANSACTIONS = "transactions"
ATTR_PAYMENTS = "payments"
ATTR_STANDING_ORDERS = "standing_orders"


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
