import asyncio
import logging
import time
import xml.etree.ElementTree as ET

import aiohttp
from homeassistant.components.cover import (
    ATTR_POSITION,
    CoverDeviceClass,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_HOST, DOMAIN

_LOGGER = logging.getLogger(__name__)

_GLOBAL_SEQ = 0

COVER_MAPPING = {
    0: CoverDeviceClass.BLIND,      # Raffstore
    1: CoverDeviceClass.BLIND,      # Jalousie innen
    2: CoverDeviceClass.SHUTTER,    # Rollladen
    3: CoverDeviceClass.AWNING,     # Markise
    4: CoverDeviceClass.AWNING,     # Markise 1 Volant
    5: CoverDeviceClass.AWNING,     # Markise int. Wind
    6: CoverDeviceClass.AWNING,     # Markise 1 Volant int. Wind
    7: CoverDeviceClass.AWNING,     # Wintergarten Markise
    8: CoverDeviceClass.AWNING,     # Fassaden Markise
    9: CoverDeviceClass.AWNING,     # Fallarm Markise
    10: CoverDeviceClass.AWNING,    # Senkrecht Markise
    11: CoverDeviceClass.AWNING,    # Markisolette
    12: CoverDeviceClass.SHADE,     # Faltstore innen
    13: CoverDeviceClass.SHADE,     # Rollo innen
    14: CoverDeviceClass.BLIND,     # Vertikal-Jalousie innen
    15: CoverDeviceClass.WINDOW,    # Fenster
    21: CoverDeviceClass.AWNING,    # Volant
    22: CoverDeviceClass.AWNING,    # Markise 2 Volant
    23: CoverDeviceClass.AWNING,    # Markise 2 Volant int. Wind
    24: CoverDeviceClass.AWNING,    # Sonnensegel
    25: CoverDeviceClass.AWNING,    # Pergolamarkise
}

def get_next_sequence() -> str:
    global _GLOBAL_SEQ
    _GLOBAL_SEQ += 1
    if _GLOBAL_SEQ >= 254:
        _GLOBAL_SEQ = 1
    return f"{_GLOBAL_SEQ:02x}"


async def send_protocol_command(host: str, payload_hex: str) -> str | None:
    seq = get_next_sequence()
    length_hex = f"{len(payload_hex) // 2:02x}"
    protocol_str = f"90{seq}{length_hex}{payload_hex}"
    timestamp = int(time.time() * 1000)

    url = f"http://{host}/protocol.xml?protocol={protocol_str}&_={timestamp}"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    return await response.text()
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            _LOGGER.error("Communication error: %s", e)
    return None


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Setup via UI (ersetzt async_setup_platform)"""
    host = entry.data[CONF_HOST]
    entities = []

    _LOGGER.info("Start auto discovery on %s", host)

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
                xml_channel = await send_protocol_command(
                    host, f"47{room_hex}{channel_hex}"
                )

                if not xml_channel:
                    continue

                root_channel = ET.fromstring(xml_channel)
                kanalname_elem = root_channel.find("kanalname")
                produkttyp_elem = root_channel.find("produkttyp")

                if kanalname_elem is None or not kanalname_elem.text:
                    break

                kanalname = kanalname_elem.text
                produkttyp = (
                    int(produkttyp_elem.text)
                    if produkttyp_elem is not None and produkttyp_elem.text is not None
                    else None
                )

                if produkttyp in COVER_MAPPING:
                    entities.append(
                        WaremaAwning(
                            host, room_hex, channel_hex, kanalname, produkttyp, "main"
                        )
                    )

                if produkttyp in (4, 6):
                    entities.append(
                        WaremaAwning(
                            host,
                            room_hex,
                            channel_hex,
                            kanalname,
                            produkttyp,
                            "volant",
                        )
                    )

                if produkttyp in (22, 23):
                    entities.append(
                        WaremaAwning(host, room_hex, channel_hex, kanalname, produkttyp, "volant_1")
                    )
                    entities.append(
                        WaremaAwning(host, room_hex, channel_hex, kanalname, produkttyp, "volant_2")
                    )

        except ET.ParseError:
            _LOGGER.error("ERROR while parsing of XML room %s", room_hex)

    async_add_entities(entities, update_before_add=True)


class WaremaAwning(CoverEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "volant"

    def __init__(self, host, room_id, channel_id, name, produkttyp, cover_type="main"):
        self._host = host
        self._room_id = room_id
        self._channel_id = channel_id
        self._name = name
        self._cover_type = cover_type
        self._current_position = 100

        self._attr_unique_id = f"warema_{host}_{room_id}_{channel_id}_{cover_type}"
        self._attr_device_class = COVER_MAPPING.get(produkttyp, CoverDeviceClass.SHADE)

        if cover_type.startswith("volant"):
            self._attr_has_entity_name = True
            self._attr_translation_key = "volant"
            self._attr_name = None
        else:
            self._attr_has_entity_name = False
            self._name = name

        self._attr_supported_features = (
            CoverEntityFeature.OPEN
            | CoverEntityFeature.CLOSE
            | CoverEntityFeature.SET_POSITION
            | CoverEntityFeature.STOP
        )

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"warema_{host}_{room_id}_{channel_id}")},
            name=name,
            manufacturer="Warema",
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

        if self._cover_type == "main":
            payload = f"21{self._room_id}{self._channel_id}03{position_hex}ffffff"
        elif self._cover_type in ("volant", "volant_1"):
            payload = f"21{self._room_id}{self._channel_id}03ffff{position_hex}ff"
        elif self._cover_type == "volant_2":
            payload = f"21{self._room_id}{self._channel_id}03ffffff{position_hex}"

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

                if self._cover_type == "main":
                    tag_name = "position"
                elif self._cover_type == "volant_2":
                    tag_name = "positionvolant2"
                else:
                    tag_name = "positionvolant1"

                pos_element = root.find(tag_name)

                if (
                    pos_element is not None
                    and pos_element.text is not None
                    and pos_element.text != "255"
                ):
                    warema_raw = int(pos_element.text)
                    warema_percent = warema_raw / 2
                    ha_position = int(100 - warema_percent)
                    self._current_position = ha_position
            except ET.ParseError:
                pass
