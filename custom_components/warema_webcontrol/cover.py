import logging
import time
import aiohttp
import asyncio
import xml.etree.ElementTree as ET

from homeassistant.components.cover import (
    CoverEntity,
    ATTR_POSITION,
    CoverEntityFeature
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_HOST

_LOGGER = logging.getLogger(__name__)

_GLOBAL_SEQ = 0

def get_next_sequence() -> str:
    global _GLOBAL_SEQ
    _GLOBAL_SEQ = (_GLOBAL_SEQ + 1) % 256
    return f"{_GLOBAL_SEQ:02x}"

async def send_protocol_command(host: str, payload_hex: str) -> str | None:
    seq = get_next_sequence()
    length_hex = f"{len(payload_hex) // 2:02x}"
    protocol_str = f"90{seq}{length_hex}{payload_hex}"
    timestamp = int(time.time() * 1000)
    
    url = f"http://{host}/protocol.xml?protocol={protocol_str}&_={timestamp}"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    return await response.text()
        except Exception as e:
            _LOGGER.error("Verbindungsfehler: %s", e)
    return None

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Setup via UI (ersetzt async_setup_platform)"""
    host = entry.data[CONF_HOST]
    entities = []
    
    _LOGGER.info("Starte Auto-Discovery auf %s", host)
    
    for room_idx in range(10):
        room_hex = f"{room_idx:02x}"
        xml_room = await send_protocol_command(host, f"03{room_hex}")
        
        if not xml_room:
            continue
            
        try:
            root_room = ET.fromstring(xml_room)
            raumname_elem = root_room.find("raumname")
            
            if raumname_elem is None or not raumname_elem.text:
                break
                
            for channel_idx in range(20):
                channel_hex = f"{channel_idx:02x}"
                xml_channel = await send_protocol_command(host, f"47{room_hex}{channel_hex}")
                
                if not xml_channel:
                    continue
                    
                root_channel = ET.fromstring(xml_channel)
                kanalname_elem = root_channel.find("kanalname")
                
                if kanalname_elem is None or not kanalname_elem.text:
                    break
                    
                kanalname = kanalname_elem.text
                entities.append(WaremaAwning(host, room_hex, channel_hex, kanalname))
                
        except ET.ParseError:
            _LOGGER.error("Fehler beim Parsen XML Raum %s", room_hex)
            
    async_add_entities(entities, update_before_add=True)


class WaremaAwning(CoverEntity):
    def __init__(self, host, room_id, channel_id, name):
        self._host = host
        self._room_id = room_id 
        self._channel_id = channel_id 
        self._name = name
        self._current_position = 100 
        
        # WICHTIG: Erlaubt das Verwalten der Entität in der UI
        self._attr_unique_id = f"warema_{host}_{room_id}_{channel_id}"
        
        self._attr_supported_features = (
            CoverEntityFeature.OPEN | 
            CoverEntityFeature.CLOSE | 
            CoverEntityFeature.SET_POSITION |
            CoverEntityFeature.STOP
        )

    @property
    def name(self):
        return self._name

    @property
    def current_cover_position(self):
        return self._current_position

    @property
    def is_closed(self):
        return self._current_position == 0

    async def _send(self, payload_hex: str) -> str | None:
        return await send_protocol_command(self._host, payload_hex)

    async def async_set_cover_position(self, **kwargs):
        ha_position = kwargs.get(ATTR_POSITION)
        if ha_position is None:
            return
            
        warema_percent = 100 - ha_position
        warema_raw = int(warema_percent * 2)
        position_hex = f"{warema_raw:02x}"
        
        payload = f"21{self._room_id}{self._channel_id}03{position_hex}ffffff"
        await self._send(payload)
        
        self._current_position = ha_position
        self.async_write_ha_state()

    async def async_open_cover(self, **kwargs):
        await self.async_set_cover_position(position=100)

    async def async_close_cover(self, **kwargs):
        await self.async_set_cover_position(position=0)

    async def async_stop_cover(self, **kwargs):
        payload = f"21{self._room_id}{self._channel_id}01ffffffff"
        await self._send(payload)
        await asyncio.sleep(1)
        await self.async_update()
        self.async_write_ha_state()

    async def async_update(self):
        payload_wakeup = f"23{self._room_id}{self._channel_id}"
        await self._send(payload_wakeup)
        
        await asyncio.sleep(1.0) 

        payload_status = f"31{self._room_id}{self._channel_id}01"
        xml_response = await self._send(payload_status)
        
        if xml_response:
            try:
                root = ET.fromstring(xml_response)
                pos_element = root.find("position")
                
                if pos_element is not None:
                    warema_raw = int(pos_element.text)
                    warema_percent = warema_raw / 2
                    ha_position = int(100 - warema_percent)
                    self._current_position = ha_position
            except ET.ParseError:
                pass

