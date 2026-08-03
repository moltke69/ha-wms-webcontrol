# WMS WebControl (Basic) – Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

Diese Custom Component ermöglicht die lokale Steuerung von Warema Markisen (und anderen WMS-Geräten) über das klassische **Warema WMS Webcontrol** (ohne "Pro") in Home Assistant.

Da das WMS Webcontrol keine offizielle API bietet, nutzt diese Integration die internen XML-Protokolle, die auch von der Weboberfläche des Geräts verwendet werden, um Befehle zu senden und den Status abzufragen.

## Features

*  **Kein YAML notwendig**: Die komplette Einrichtung erfolgt modern und komfortabel über die Home Assistant Benutzeroberfläche (Config Flow).
*  **Auto-Discovery**: Du musst nur die IP-Adresse eingeben. Die Integration durchsucht das Webcontrol automatisch nach allen Räumen und Kanälen und übernimmt die originalen Gerätenamen!
*  **Volle Kontrolle**: Unterstützt das Öffnen, Schließen, Stoppen während der Fahrt sowie das Anfahren einer exakten prozentualen Position.
*  **100% Lokal**: Alle Befehle werden direkt im eigenen Netzwerk an das Webcontrol gesendet. Keine Cloud erforderlich!
*  **Echtzeit-Feedback**: Holt sich vor jeder Statusaktualisierung frische Daten (Wake-Up-Befehl), damit die Position in Home Assistant immer stimmt.

## Voraussetzungen

* Ein funktionierendes **Warema WMS Webcontrol** (die ältere Version, oft als kleiner schwarzer Kasten realisiert ist).
* Die IP-Adresse des WMS Webcontrol muss bekannt und am besten statisch im Router vergeben sein.

## Installation

Die einfachste Methode ist die Installation über [HACS](https://hacs.xyz/) (Home Assistant Community Store).

1. Öffne **HACS** in Home Assistant.
2. Klicke auf **Integrationen**.
3. Klicke oben rechts auf die drei Punkte (`...`) und wähle **Benutzerdefinierte Repositories**.
4. Füge die URL dieses Repositories ein: `https://github.com/moltke69/ha-wms-webcontrol`
5. Wähle als Kategorie **Integration** und klicke auf *Hinzufügen*.
6. Suche nun in HACS nach *Warema WMS Webcontrol*, klicke darauf und wähle **Herunterladen**.
7. **Starte Home Assistant neu.**

*(Alternativ: Lade das Repository als ZIP herunter und kopiere den Ordner `custom_components/warema_webcontrol` manuell in Dein Home Assistant Verzeichnis.)*

## Konfiguration

Nachdem die Integration installiert und Home Assistant neu gestartet wurde, ist die Einrichtung ein Kinderspiel:

1. Gehe in Home Assistant zu **Einstellungen** -> **Integration**.
2. Klicke unten rechts auf **Integration hinzufügen**.
3. Suche nach **Warema WMS Webcontrol** und wähle sie aus.
4. Gib die **IP-Adresse** Deines Webcontrols ein (z.B. `192.168.1.50`).
5. Klicke auf *Absenden*.

Lehn Dich zurück! Die Integration scannt nun alle Räume und fügt Deine Markisen automatisch als "Cover" (Abdeckungen) zu Deinem Home Assistant hinzu.

## Fehlerbehebung (Troubleshooting)

* **Die Markise reagiert nur manchmal:** Das System verwendet fortlaufende Sequenznummern, um Befehle zu authentifizieren. Die Integration kümmert sich automatisch darum. Falls trotzdem Befehle verschluckt werden, prüfe, ob das Webcontrol eine stabile WLAN/LAN-Verbindung hat.
* **Die Position stimmt nicht:** Warema nutzt intern eine Logik von 0-200, während Home Assistant mit 0-100% rechnet (0% = geschlossen/ausgefahren, 100% = offen/eingefahren). Die Integration rechnet dies automatisch um.

## Hinweis zur Code-Erstellung

Das Reverse Engineering des WMS-Protokolls (das Abfangen der Hex- und XML-Strings) wurde manuell durchgeführt. Für die anschließende Übersetzung in eine funktionsfähige Home Assistant Integration (Python, Config Flow, async-Logik)
wurde KI-Unterstützung (LLM) genutzt. Der Code wurde anschließend ausführlich lokal getestet.


---
*Disclaimer: Dies ist ein inoffizielles Community-Projekt. Es steht in keiner Verbindung zur WAREMA Renkhoff SE.*

