import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_HOST

class WaremaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Verwaltet den Setup-Prozess in der UI."""
    VERSION = 1
    
    async def async_step_user(self, user_input=None):
        """Erster Schritt: Benutzer gibt IP-Adresse ein."""
        errors = {}
        
        if user_input is not None:
            # Hier speichern wir die eingegebene IP
            return self.async_create_entry(
                title=f"Warema Webcontrol ({user_input[CONF_HOST]})",
                data=user_input
            )
            
        # Das Eingabefeld definieren
        data_schema = vol.Schema({
            vol.Required(CONF_HOST): str,
        })
        
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors
        )

