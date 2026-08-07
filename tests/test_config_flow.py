from unittest.mock import patch

from homeassistant import config_entries, data_entry_flow

from custom_components.warema_webcontrol.const import CONF_HOST, DOMAIN


async def test_successful_config_flow(hass):
    """Testet den erfolgreichen Durchlauf der Konfiguration über die UI."""
    # 1. Konfigurations-Dialog (UI) aufrufen
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    # Prüfen, ob das Eingabeformular angezeigt wird
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"

    # 2. Benutzereingabe simulieren und Setup mocken (abfangen)
    # Wir blockieren hier den echten async_setup_entry Aufruf, da wir nur den Flow testen
    with patch(
        "custom_components.warema_webcontrol.async_setup_entry",
        return_value=True,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={
                CONF_HOST: "192.168.1.50",
            },
        )

    # 3. Prüfen, ob der Eintrag erfolgreich erstellt wurde
    assert result2["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result2["title"] == "192.168.1.50"
    assert result2["data"] == {CONF_HOST: "192.168.1.50"}
