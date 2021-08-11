import logging
from dateutil.relativedelta import relativedelta
from homeassistant.helpers.entity import Entity
from homeassistant.helpers import config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from datetime import datetime, timedelta
from edata.helpers import ReportHelper, PLATFORMS, ATTRIBUTES

# HA variables
_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=30)
FRIENDLY_NAME = 'edata'
DOMAIN = 'edata'

# Custom configuration entries
CONF_CUPS = 'cups'
CONF_PROVIDER = 'provider'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_PROVIDER): cv.string,
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(CONF_CUPS): cv.string,
    }
)

async def async_setup_platform(hass, config, add_entities, discovery_info=None):
    entities = []
    edata = ReportHelper (config[CONF_PROVIDER], config[CONF_USERNAME], config[CONF_PASSWORD], config[CONF_CUPS])
    entities.append(EdsSensor(edata, name=f'edata_{config[CONF_CUPS][-4:]}'))
    add_entities(entities)

class EdsSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, edata, state='cups', name='edata'):
        """Initialize the sensor."""
        self._state = None
        self._attributes = {}
        self.edata = edata
        self.state_label = state
        self._name = name

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Return the icon to be used for this entity."""
        return "mdi:flash" 

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return ''

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    async def async_update(self):
        """Fetch new state data for the sensor."""
        try:
            date_ref = datetime (
                datetime.today ().year, 
                datetime.today ().month, 1, 0, 0, 0
            )
            self.edata.async_update ()
        except Exception as e:
            _LOGGER.error (e)
        # update attrs
        for attr in self.edata.attributes:
            self._attributes[attr] = f"{self._get_attr_value(attr) if self._get_attr_value(attr) is not None else '-'} {ATTRIBUTES[attr] if ATTRIBUTES[attr] is not None else ''}"
            
        # update state
        self._state = self._get_attr_value('cups')

    def _get_attr_value (self, attr):
        try:
            return self.edata.attributes[attr]
        except Exception:
            return None

    