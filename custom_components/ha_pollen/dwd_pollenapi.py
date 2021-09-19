
import sys
import logging
import json
from datetime import timedelta
from datetime import datetime

from homeassistant.util import Throttle
from homeassistant.components.rest.sensor import RestData

_LOGGER = logging.getLogger(__name__)

BASE_URL = 'https://opendata.dwd.de/climate_environment/health/alerts/s31fg.json'
UPDATE_INTERVAL = timedelta(minutes=15)

# Constants for Sensor attribute names
SENSOR_KEY_REGION_NAME = 'region_name'
SENSOR_KEY_PARTREGION_NAME = 'partregion_name'

# Constants for REST JSON Keys
KEY_LAST_UPDATE = 'last_update'
KEY_CONTENT = 'content'
KEY_PARTREGION_ID = 'partregion_id'
KEY_REGION_NAME = 'region_name'
KEY_PARTREGION_NAME = 'partregion_name'
KEY_POLLEN_DATA = 'Pollen'

# Mapping for API values (i.e API value can be '1-2')
VALUE_MAPPING_HOMEASSISTANT = {'-1': None, '0': 0, '0-1': 1, '1': 2, '1-2': 3, '2': 4, '2-3': 5, '3': 6}

class DwdPollenApi:
    def __init__(self, partregion_id, pollens):
        self._rest = RestData('GET', BASE_URL, None, None, None, True)
        self._partregion_id = partregion_id
        self._pollens = pollens
        self.last_update = None
        self.data = {}
        self._state = None
        self.update()

    @Throttle(UPDATE_INTERVAL)
    def update(self):
        # Use Home Assistant Rest sensor to fetch data
        self._rest.update()

        result = json.loads(self._rest.data)

        self.last_update = datetime.strptime(result[KEY_LAST_UPDATE], '%Y-%m-%d %H:%M Uhr')

        # Iterate all regions
        for partregion in result[KEY_CONTENT]:
            current_partregion = partregion[KEY_PARTREGION_ID]
            # Fetch data for selected partregion
            if current_partregion == self._partregion_id:
                self.data[current_partregion] = {}
                self.data[current_partregion][SENSOR_KEY_REGION_NAME] = partregion[KEY_REGION_NAME]
                self.data[current_partregion][SENSOR_KEY_PARTREGION_NAME] = partregion[KEY_PARTREGION_NAME]


                self.data[current_partregion]['pollen'] = {}

                # Iterate over all pollens to fetch
                for pollen in partregion[KEY_POLLEN_DATA]:
                    pollenname = pollen
                    pollen_data = partregion[KEY_POLLEN_DATA][pollenname]

                    # For now, only fetch today's values for selected pollens
                    if str(pollenname).lower() in self._pollens:
                        self.data[current_partregion]['pollen'][str(pollenname).lower()] = VALUE_MAPPING_HOMEASSISTANT[pollen_data['today']]
                        self._state = VALUE_MAPPING_HOMEASSISTANT[pollen_data['today']]



