# Adobe-Network-Block-Script

Ein kleines Python-Skript, das alle Adobe-Programme vom Internet trennt — ohne sie zu deinstallieren. Es nutzt die Windows-Firewall (über PowerShell), um für jede gefundene Adobe-Executable eine Sperrregel einzurichten.

---

## Was es macht

- **Suchen** — durchsucht gängige Installationsorte nach Adobe-Executables
- **Blockieren** — erstellt eingehende + ausgehende Firewallregeln für jede gefundene `.exe`
- **Bestehende anpassen** — setzt bereits vorhandene Adobe-Firewallregeln auf „Blockieren"
- **Nicht-destruktiv** — die Programme bleiben installiert, nur der Netzwerkzugriff wird unterbunden

---

## Erkannte Programme

Das Skript erkennt Executables anhand folgender Begriffe im Dateipfad:

| Keyword | Beschreibung |
|---|---|
| `adobe` | Alle Adobe-Programme allgemein |
| `photoshop` | Adobe Photoshop |
| `creative cloud` | Adobe Creative Cloud |
| `ccxprocess` | Creative Cloud Hintergrundprozess |
| `core sync` | Creative Cloud Synchronisationsdienst |

---

## Gescannte Ordner

Das Skript durchsucht automatisch folgende Verzeichnisse:

| Pfad | Beschreibung |
|---|---|
| `C:\Program Files` | Standard-Installationsordner (64-Bit) |
| `C:\Program Files (x86)` | Standard-Installationsordner (32-Bit) |
| `%LOCALAPPDATA%` | Benutzerspezifische lokale App-Daten |
| `%APPDATA%` | Benutzerspezifische Roaming-App-Daten |

Zusätzlich werden diese Ordner immer direkt vollständig durchsucht, unabhängig vom Scan-Ergebnis:

| Pfad | Beschreibung |
|---|---|
| `C:\Program Files\Adobe\Adobe Photoshop 2026` | Photoshop 2026 Installationsordner |
| `C:\Program Files\Adobe\Adobe Creative Cloud Experience` | Creative Cloud Experience |

---

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
