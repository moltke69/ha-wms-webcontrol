import logging
import xml.etree.ElementTree as ET

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_HOST, DOMAIN
from .cover import send_protocol_command

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    host = entry.data[CONF_HOST]
    entities = []

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
                bedientyp_elem = root_channel.find("bedientyp")

                if kanalname_elem is None or not kanalname_elem.text:
                    break

                bedientyp = (
                    int(bedientyp_elem.text)
                    if bedientyp_elem is not None and bedientyp_elem.text is not None
                    else None
                )
                produkttyp = (
                    int(produkttyp_elem.text)
                    if produkttyp_elem is not None and produkttyp_elem.text is not None
                    else None
                )

                if produkttyp in (3, 4, 5, 6) and bedientyp == 4:
                    kanalname = kanalname_elem.text
                    entities.append(
                        WaremaWaveButton(host, room_hex, channel_hex, kanalname)
                    )

        except ET.ParseError:
            pass

    async_add_entities(entities)


class WaremaWaveButton(ButtonEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "wave"

    def __init__(self, host, room_id, channel_id, name):
        self._host = host
        self._room_id = room_id
        self._channel_id = channel_id

        self._attr_name = f"{name} Winken"
        self._attr_unique_id = f"warema_{host}_{room_id}_{channel_id}_wave"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"warema_{host}_{room_id}_{channel_id}")}
        )

    async def async_press(self) -> None:
        payload = f"25{self._room_id}{self._channel_id}"
        await send_protocol_command(self._host, payload)
