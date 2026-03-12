# Setup and Testing Guide for ID Card Printer

## Quick Start

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Your Printer
Edit `config.json` and update the printer name to match your Epson 4830:
```json
"printer": {
  "name": "EPSON Stylus Photo R4830"
}
```

To find your exact printer name on Windows:
- Open Control Panel → Devices and Printers
- Right-click your Epson 4830 → Printer Properties
- Copy the exact name shown

### 3. Test Alignment First!

**IMPORTANT:** Before printing actual cards, test the alignment:

```bash
python alignment_test.py
```

This will:
- Print a test pattern with borders and crosshairs
- Show you if cards align properly in the 2-card tray
- Save a preview as `alignment_test_preview.png`

**Check the printed test:**
- Do the red borders match the card edges?
- Are the corner marks at the actual corners?
- Are both cards positioned correctly in the tray?

**If alignment is off**, adjust these values in `config.json`:
```json
"tray": {
  "card1_offset_x_mm": 0,    // Adjust left/right for card 1
  "card1_offset_y_mm": 0,    // Adjust up/down for card 1
  "card2_offset_x_mm": 90,   // Adjust left/right for card 2
  "card2_offset_y_mm": 0,    // Adjust up/down for card 2
  "spacing_between_cards_mm": 5,  // Space between the 2 cards
  "tray_depression_compensation_x_mm": 0,  // X compensation for physical tray depression
  "tray_depression_compensation_y_mm": 0   // Y compensation for physical tray depression
}
```

The `tray_depression_compensation_x_mm` and `tray_depression_compensation_y_mm` values compensate
for the physical indentation (depression) in the 2-card plastic tray where the PVC cards sit. If
your cards consistently print slightly offset in the same direction, adjust these values (positive
moves right/down, negative moves left/up) before tuning the individual card offsets.

Run `alignment_test.py` again after adjustments.

### 4. Create Sample Excel Data

```bash
python excel_reader.py
```

This creates `card_data.xlsx` with sample data. Edit this file with your actual card information:

| Name | ID | Department | Photo | Title | Email |
|------|-----|-----------|-------|-------|-------|
| John Doe | 001 | Sales | photos/john.jpg | Manager | john@example.com |

### 5. Test Card Printing

Once alignment is good and Excel data is ready:

```bash
python card_printer.py
```

This will:
- Read card data from Excel
- Generate preview images for each batch
- Print 2 cards at a time to your Epson 4830
- Pause between batches

## Troubleshooting

### "Printer not found" error
- Check printer name in `config.json` matches exactly
- Make sure Epson 4830 is powered on and set as ready
- Verify printer drivers are installed

### Cards don't align properly
- Run `alignment_test.py` multiple times
- Adjust offset values in `config.json` by 1-2mm at a time
- Make sure tray is fully seated in printer

### Excel file errors
- Make sure Excel file is closed when running scripts
- Check that column headers match: Name, ID, Department, Photo, Title, Email
- Verify sheet name is "Cards" (or update in config.json)

### Colors look wrong
- Update Adobe color profile in `config.json`:
  ```json
  "photoshop": {
    "color_profile": "Adobe RGB (1998)"
  }
  ```
- Make sure Epson 4830 color management is set to "ICM" in printer properties

### Photo images not loading
- Create a `photos/` folder in the project directory
- Put your photo files there
- Reference them in Excel as: `photos/filename.jpg`

## Next Steps

1. **Run alignment test** - Get the positioning perfect first
2. **Create your Excel data** - Add real cardholder information
3. **Add photos** - Place photo files in `photos/` folder
4. **Print test cards** - Print 2-4 cards to verify everything works
5. **Batch print** - Run the full set when ready

## Tips

- **Always test alignment** with blank cards first
- **Print 2 at a time** - The tray holds 2 cards
- **Check card orientation** - Make sure cards are face-up in tray
- **Use high-quality PVC cards** - CR80 standard size (3.375" x 2.125")
- **Keep Epson 4830 drivers updated** for best results
