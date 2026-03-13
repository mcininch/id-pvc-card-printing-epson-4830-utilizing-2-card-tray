# ID PVC Card Printing - Epson 4830 with 2-Card Tray — **Pro Edition**

Python-based solution for printing professional ID cards using Adobe Photoshop CS5, Epson 4830 printer, and 2-card plastic tray.

> ✅ **You already have the Pro Edition (v2.0).** No upgrade needed.

## Features (Pro Edition)
- Read card data from Excel files using EPPlus/openpyxl
- Proper alignment for 2-card tray (Amazon)
- Adobe color profile support for accurate colors
- Automated batch printing
- Alignment guides and testing
- GUI preview with Photoshop Bridge
- Unlimited card printing

## Hardware Requirements
- Epson 4830 Printer (brand new)
- 2-card plastic tray (Amazon)
- PVC cards (CR80 standard: 3.375" x 2.125")

## Software Requirements
- Python 3.8+
- Adobe Photoshop CS5
- Required Python packages (see requirements.txt)

## Setup
1. Install Python dependencies: `pip install -r requirements.txt`
2. Configure Epson 4830 printer settings
3. Set up Adobe color profiles
4. Calibrate card alignment

## Project Structure
- `card_printer.py` - Main printing script
- `alignment_test.py` - Alignment calibration tool
- `excel_reader.py` - Read card data from Excel
- `config.json` - Printer and alignment settings
- `requirements.txt` - Python dependencies

## Usage
See individual script files for detailed usage instructions.