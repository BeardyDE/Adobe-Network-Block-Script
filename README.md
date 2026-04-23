# Adobe-Network-Block-Script
Ein kleines Python-Skript, das alle Adobe-Programme vom Internet trennt — ohne sie zu deinstallieren. Es nutzt die Windows-Firewall (über PowerShell), um für jede gefundene Adobe-Executable eine Sperrregel einzurichten.


## Was es macht

- **Suchen** — durchsucht gängige Installationsorte (`Programme`, `AppData` usw.) nach Adobe-Executables
- **Blockieren** — erstellt eingehende + ausgehende Firewallregeln für jede gefundene `.exe`
- **Bestehende anpassen** — setzt bereits vorhandene Adobe-Firewallregeln auf „Blockieren"
- **Nicht-destruktiv** — die Programme bleiben installiert, nur der Netzwerkzugriff wird unterbunden

## Verwendung

```bash
# Als Administrator ausführen
python block_adobe.py
```

## Wozu?

Adobe-Programme kommunizieren im Hintergrund regelmäßig mit Adobes Servern — für Lizenzprüfungen, Telemetrie, automatische Updates und Creative-Cloud-Sync. Wer seine installierten Programme lieber offline nutzt oder schlicht nicht möchte, dass sie nach Hause telefonieren, dem nimmt dieses Skript die mühsame manuelle Einrichtung von Firewallregeln ab.

## Voraussetzungen

- Windows 10 / 11
- Python 3.10+
- Administratorrechte (PowerShell-Firewallbefehle erfordern sie)

> **Hinweis:** Dieses Skript deinstalliert nichts und umgeht keinen Kopierschutz. Es erstellt lediglich Windows-Firewallregeln. Wer diese Regeln wieder entfernt (über die Windows Defender Firewall), stellt den Internetzugriff für alle Adobe-Programme vollständig wieder her.
