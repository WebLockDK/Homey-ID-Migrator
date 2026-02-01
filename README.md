# Homey ID Migrator
  Tool to clone the identity of Homey SHS to a Homey Pro 202x backup

## How-To use Homey-ID-Migrator:
  Read the full guide at https://homey.guide/migrering-af-homey-pro-data-til-homey-shs
  (written in Danish so please use Google Translate or similar)

## Build Homey-ID-Migrator tool yourself (Windows):
### Prerequisites:
    winget install Python.Python.3.11
    pip install pyinstaller
    pip install colorama

### Build:
    pyinstaller --onefile --name "Homey.guide - Homey ID Migrator" --icon="icon.ico" --add-data "icon.ico;." --version-file="version_info.txt" homey_migrator_v3.py
