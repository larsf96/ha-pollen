# -*- coding: utf-8 -*-
from homeassistant.components.sensor import PLATFORM_SCHEMA

from homeassistant.const import (
    STATE_UNKNOWN)
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    ATTR_ATTRIBUTION)
import voluptuous as vol
from .dwd_pollenapi import DwdPollenApi
import logging

DEFAULT_NAME = "ha-pollen"

DEFAULT_INCLUDE_POLLEN = ['birke', 'graeser', 'esche', 'erle', 'hasel', 'beifuss', 'ambrosia', 'roggen']
DEFAULT_INCLUDE_DAYS = ['today', 'tomorrow', 'dayafter_tomorrow']

CONF_REGION_IDS = 'region_ids'
CONF_INCLUDE_POLLEN = 'include_pollen'
CONF_INCLUDE_DAYS = 'include_days'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_REGION_IDS): cv.string,
    vol.Optional(CONF_INCLUDE_POLLEN, default=DEFAULT_INCLUDE_POLLEN): cv.ensure_list,
    vol.Optional(CONF_INCLUDE_DAYS, default=DEFAULT_INCLUDE_DAYS): cv.ensure_list,
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    name = config.get(DEFAULT_NAME)
    region_ids = config.get(CONF_REGION_IDS)
    include_pollen = config.get(DEFAULT_INCLUDE_POLLEN)
    #include_days = config.get(DEFAULT_INCLUDE_DAYS)

    add_entities([PollenSensorDE(DEFAULT_NAME, region_ids, include_pollen)], True)


_LOGGER = logging.getLogger(__name__)

class PollenSensorDE:
    def __init__(self, name, region_ids, include_pollen):
        self._name = name
        self._region_ids = region_ids
        self._include_pollen = include_pollen
        self._api = DwdPollenApi(region_ids, include_pollen)

        self._state = STATE_UNKNOWN
        self._attributes = None

        self.update()
    
    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._api._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return None

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        api_data = self._api.data
        return {
            ATTR_ATTRIBUTION: 'Test provider',
            'region_name': self._api.data[self._region_ids]['region_name']
        }
        
    
    def update(self):
        """ Fetch new state data from API"""
        self._api.update()
