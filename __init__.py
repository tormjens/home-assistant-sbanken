"""
Sbanken Sensor Platform

  - platform: sbanken
    customer_id: 01010112345
    client_id: token
    secret: secret
"""

import asyncio
import logging
import datetime
import voluptuous as vol

from random import randrange

from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import track_time_interval
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (CONF_SCAN_INTERVAL)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = datetime.timedelta(minutes=30)

CONF_CUSTOMER_ID = 'customer_id'
CONF_CLIENT_ID = 'client_id'
CONF_SECRET = 'secret'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_CLIENT_ID): cv.string,
    vol.Optional(CONF_SECRET): cv.string,
    vol.Optional(CONF_SCAN_INTERVAL, default=SCAN_INTERVAL): cv.time_period,
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""
    _LOGGER.debug("Setting up Sbanken Sensor Platform.")

    api = SbankenApi(config.get(CONF_CUSTOMER_ID), config.get(CONF_CLIENT_ID), config.get(CONF_SECRET))

    accounts = api.get_accounts()

    sensors = []
    for account in accounts:
        sensors.append(SbankenSensor(account, config, api))

    add_devices(sensors)

    return True
    
    
class SbankenSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, account, config, api):
        """Initialize the sensor."""
        self.config = config
        self.api = api
        self._account = account
        self._state = account['balance']

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

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        account = self.api.get_account(self._account['accountNumber'])
        self._account = account
        self._state = account['balance']
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
        oauth2_client = BackendApplicationClient(client_id=self.client_id)
        session = OAuth2Session(client=oauth2_client)
        session.fetch_token(
            token_url='https://api.sbanken.no/identityserver/connect/token',
            client_id=self.client_id,
            client_secret=self.secret
        )
        return session


    def get_customer_information(self):
        response = self.session.get(
            "https://api.sbanken.no/customers/api/v1/Customers/{}".format(self.customer_id)
        ).json()

        if not response["isError"]:
            return response["item"]
        else:
            raise RuntimeError("{} {}".format(response["errorType"], response["errorMessage"]))


    def get_accounts(self):
        response = self.session.get(
            "https://api.sbanken.no/bank/api/v1/Accounts/{}".format(self.customer_id)
        ).json()

        if not response["isError"]:
            return response["items"]
        else:
            raise RuntimeError("{} {}".format(response["errorType"], response["errorMessage"]))

    def get_account(self, accountnumber):
        response = self.session.get(
            "https://api.sbanken.no/bank/api/v1/Accounts/{}/{}".format(self.customer_id, accountnumber)
        ).json()

        if not response["isError"]:
            return response['item']
        else:
            raise RuntimeError("{} {}".format(response["errorType"], response["errorMessage"]))
