"""
Sbanken accounts sensor 

For more details about this platform, please refer to the documentation at
https://github.com/toringer/home-assistant-sbanken

"""

import asyncio
import logging
import datetime
import voluptuous as vol

from random import randrange

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import track_time_interval
from homeassistant.components.sensor import (PLATFORM_SCHEMA, DOMAIN)
from homeassistant.const import (CONF_SCAN_INTERVAL)


REQUIREMENTS = ['oauthlib==3.0.2', 'requests-oauthlib==1.2.0']


_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = datetime.timedelta(minutes=20)

ATTR_AVAILABLE = 'available'
ATTR_BALANCE = 'balance'
ATTR_ACCOUNT_NUMBER = 'account_number'
ATTR_NAME = 'name'
ATTR_ACCOUNT_TYPE = 'account_type'
ATTR_ACCOUNT_LIMIT = 'credit_limit'
ATTR_ACCOUNT_ID = 'account_id'

ATTR_AMOUNT = 'amount'
ATTR_FROM_ACCOUNT = 'from_account'
ATTR_TO_ACCOUNT = 'to_account'
ATTR_MESSAGE = 'message'

SERVICE_SCHEMA = vol.Schema({
    vol.Required(ATTR_FROM_ACCOUNT): cv.string,
    vol.Required(ATTR_TO_ACCOUNT): cv.string,
    vol.Required(ATTR_AMOUNT): vol.Coerce(float),
    vol.Required(ATTR_MESSAGE): cv.string,
})


CONF_CUSTOMER_ID = 'customer_id'
CONF_CLIENT_ID = 'client_id'
CONF_SECRET = 'secret'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_CUSTOMER_ID): cv.string,
    vol.Optional(CONF_CLIENT_ID): cv.string,
    vol.Optional(CONF_SECRET): cv.string,
    vol.Optional(CONF_SCAN_INTERVAL, default=SCAN_INTERVAL): cv.time_period,
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""

    _LOGGER.info("Setting up Sbanken Sensor Platform.")

    api = SbankenApi(config.get(CONF_CUSTOMER_ID), config.get(CONF_CLIENT_ID), config.get(CONF_SECRET))
    session = api.create_session()
    accounts = api.get_accounts(session)

    sensors = []
    for account in accounts:
        sensors.append(SbankenSensor(account, config, api))

    add_devices(sensors)


    def handleTransfer(service):
        _LOGGER.info("handleTransfer")
        amount = float(service.data.get(ATTR_AMOUNT))
        from_account = service.data.get(ATTR_FROM_ACCOUNT)
        to_account = service.data.get(ATTR_TO_ACCOUNT)
        message = service.data.get(ATTR_MESSAGE)

        session = api.create_session()
        api.transfer(session, from_account, to_account, amount, message)

        """Update accounts"""
        for sensor in sensors:
            sensor.update()

    hass.services.register(DOMAIN, "transfer", handleTransfer, schema=SERVICE_SCHEMA)
    return True
    
    
class SbankenSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, account, config, api):
        """Initialize the sensor."""
        self.config = config
        self.api = api
        self._account = account
        self._state = account['available']

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return self._account['accountNumber']

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._account['name'] + ' (' + self._account['accountNumber'] + ')'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return 'kr'

    @property
    def should_poll(self):
        """Camera should poll periodically."""
        return True

    @property    
    def icon(self):
        """Icon to use in the frontend, if any."""
        return 'mdi:cash'

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return {
            ATTR_ACCOUNT_ID: self._account['accountId'], 
            ATTR_AVAILABLE: self._account['available'], 
            ATTR_BALANCE: self._account['balance'], 
            ATTR_ACCOUNT_NUMBER: self._account['accountNumber'], 
            ATTR_NAME: self._account['name'], 
            ATTR_ACCOUNT_TYPE: self._account['accountType'], 
            ATTR_ACCOUNT_LIMIT: self._account['creditLimit']
            }


    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        session = self.api.create_session()
        account = self.api.get_account(session, self._account['accountId'])
        self._account = account
        self._state = account['available']
        self.schedule_update_ha_state()

class SbankenApi(object):
    """Get the latest data and update the states."""

    def __init__(self, customer_id, client_id, secret):
        """Initialize the data object."""

        self.customer_id = customer_id
        self.client_id = client_id
        self.secret = secret
        self.session = self.create_session()

    
    def create_session(self):

        from requests_oauthlib import OAuth2Session
        from oauthlib.oauth2 import BackendApplicationClient
        import urllib.parse
        
        oauth2_client = BackendApplicationClient(client_id=urllib.parse.quote(self.client_id))
        session = OAuth2Session(client=oauth2_client)
        session.fetch_token(
            token_url='https://auth.sbanken.no/identityserver/connect/token',
            client_id=urllib.parse.quote(self.client_id),
            client_secret=urllib.parse.quote(self.secret)
        )
        return session


    def get_customer_information(self, session):
        response = session.get(
            "https://api.sbanken.no/exec.customers/api/v1/Customers/",
            headers={'customerId': self.customer_id}
        ).json()

        if not response["isError"]:
            return response["item"]
        else:
            raise RuntimeError("{} {}".format(response["errorType"], response["errorMessage"]))



    def get_accounts(self, session):
        response = session.get(
            "https://api.sbanken.no/exec.bank/api/v1/Accounts/",
            headers={'customerId': self.customer_id}
        ).json()

        if not response["isError"]:
            return response["items"]
        else:
            raise RuntimeError("{} {}".format(response["errorType"], response["errorMessage"]))

    def get_account(self, session, accountId):
        response = session.get(
            "https://api.sbanken.no/exec.bank/api/v1/Accounts/{}".format(accountId),
            headers={'customerId': self.customer_id}
        ).json()

        if not response["isError"]:
            return response['item']
        else:
            raise RuntimeError("{} {}".format(response["errorType"], response["errorMessage"]))


    def transfer(self, session, from_account_id, to_account_id, amount, message):
        import json

        payload = {'fromAccountId': from_account_id,
            'toAccountId': to_account_id,
            'message': message + " (HA)",
            'amount': amount}

        response = session.post(
            "https://api.sbanken.no/exec.bank/api/v1/Transfers/", data=json.dumps(payload), headers={'customerId': self.customer_id, 'Content-type': 'application/json'}
        ).json()
        
        if response["isError"]:
            raise RuntimeError("{} {}".format(response["errorType"], response["errorMessage"]))
