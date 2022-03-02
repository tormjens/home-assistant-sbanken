"""The SBanken integration."""
from __future__ import annotations
import logging
import voluptuous as vol
from .sbankenApi import SbankenApi
from .services import async_setup_services
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from .const import DOMAIN, CONF_CLIENT_ID, CONF_SECRET, CONF_NUMBER_OF_TRANSACTIONS

_LOGGER = logging.getLogger(__name__)
PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Sbanken from a config entry."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    options = entry.options
    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    hass.data[DOMAIN]["listener"] = entry.add_update_listener(update_listener)
    await async_setup_services(
        hass, entry.options.get(CONF_CLIENT_ID), entry.options.get(CONF_SECRET)
    )
    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update."""
    _LOGGER.info(f"Reloading entry... {entry.options}")
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN]["listener"]()
    return unload_ok
