"""
Alignment Test Tool for 2-Card Tray
Prints alignment guides to calibrate card positioning
"""

import json
from PIL import Image, ImageDraw, ImageFont
import win32print
import win32ui
from PIL import ImageWin


def load_config():
    """Load configuration from config.json"""
    with open('config.json', 'r') as f:
        return json.load(f)


def create_alignment_test_image(card_width_px, card_height_px):
    """
    Create alignment test pattern with:
    - Corner marks
    - Center crosshair
    - Measurement grid
    - Border outline
    """
    # Create white background
    img = Image.new('RGB', (card_width_px, card_height_px), 'white')
    draw = ImageDraw.Draw(img)
    
    # Draw border (5px thick red line)
    border_color = 'red'
    border_width = 5
    draw.rectangle(
        [(0, 0), (card_width_px-1, card_height_px-1)],
        outline=border_color,
        width=border_width
    )
    
    # Draw corner marks (20px lines)
    corner_length = 20
    corner_color = 'blue'
    corner_width = 3
    
    # Top-left
    draw.line([(0, 0), (corner_length, 0)], fill=corner_color, width=corner_width)
    draw.line([(0, 0), (0, corner_length)], fill=corner_color, width=corner_width)
    
    # Top-right
    draw.line([(card_width_px-corner_length, 0), (card_width_px, 0)], fill=corner_color, width=corner_width)
    draw.line([(card_width_px-1, 0), (card_width_px-1, corner_length)], fill=corner_color, width=corner_width)
    
    # Bottom-left
    draw.line([(0, card_height_px-1), (corner_length, card_height_px-1)], fill=corner_color, width=corner_width)
    draw.line([(0, card_height_px-corner_length), (0, card_height_px)], fill=corner_color, width=corner_width)
    
    # Bottom-right
    draw.line([(card_width_px-corner_length, card_height_px-1), (card_width_px, card_height_px-1)], fill=corner_color, width=corner_width)
    draw.line([(card_width_px-1, card_height_px-corner_length), (card_width_px-1, card_height_px)], fill=corner_color, width=corner_width)
    
    # Draw center crosshair
    center_x = card_width_px // 2
    center_y = card_height_px // 2
    crosshair_length = 30
    crosshair_color = 'green'
    crosshair_width = 2
    
    draw.line([(center_x - crosshair_length, center_y), (center_x + crosshair_length, center_y)], 
              fill=crosshair_color, width=crosshair_width)
    draw.line([(center_x, center_y - crosshair_length), (center_x, center_y + crosshair_length)], 
              fill=crosshair_color, width=crosshair_width)
    
    # Add text labels
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    draw.text((center_x - 100, center_y + 40), "ALIGNMENT TEST", fill='black', font=font)
    draw.text((20, 40), "Card 1/2", fill='black', font=font)
    
    return img


def create_dual_card_test_pattern(config):
    """Create test pattern for both cards in the 2-card tray"""
    dpi = config['photoshop']['resolution_dpi']
    card_width_inches = config['printer']['card_width_inches']
    card_height_inches = config['printer']['card_height_inches']
    
    # Convert to pixels
    card_width_px = int(card_width_inches * dpi)
    card_height_px = int(card_height_inches * dpi)
    
    # Get tray spacing
    spacing_mm = config['tray']['spacing_between_cards_mm']
    spacing_px = int((spacing_mm / 25.4) * dpi)  # Convert mm to pixels

    # Tray depression compensation: accounts for the physical indentation in the
    # 2-card plastic tray where cards sit, which can shift the effective print area.
    depression_comp_x_px = int((config['tray'].get('tray_depression_compensation_x_mm', 0) / 25.4) * dpi)
    depression_comp_y_px = int((config['tray'].get('tray_depression_compensation_y_mm', 0) / 25.4) * dpi)

    # Create full image for 2 cards side by side
    total_width = (card_width_px * 2) + spacing_px
    total_height = card_height_px
    
    full_image = Image.new('RGB', (total_width, total_height), 'white')
    
    # Create alignment test for each card
    card1_img = create_alignment_test_image(card_width_px, card_height_px)
    card2_img = create_alignment_test_image(card_width_px, card_height_px)
    
    # Paste cards onto full image, applying depression compensation
    full_image.paste(card1_img, (depression_comp_x_px, depression_comp_y_px))
    full_image.paste(card2_img, (card_width_px + spacing_px + depression_comp_x_px, depression_comp_y_px))
    
    return full_image


def print_alignment_test(config):
    """Print the alignment test pattern to Epson 4830"""
    printer_name = config['printer']['name']
    
    # Create test pattern
    print("Creating alignment test pattern...")
    test_image = create_dual_card_test_pattern(config)
    
    # Save a preview
    test_image.save('alignment_test_preview.png')
    print("Preview saved as: alignment_test_preview.png")
    
    # Print to Epson 4830
    print(f"Printing to: {printer_name}")
    
    hdc = win32ui.CreateDC()
    hdc.CreatePrinterDC(printer_name)
    
    printable_area = hdc.GetDeviceCaps(8), hdc.GetDeviceCaps(10)  # HORZRES, VERTRES
    printer_size = hdc.GetDeviceCaps(110), hdc.GetDeviceCaps(111)  # PHYSICALWIDTH, PHYSICALHEIGHT
    
    hdc.StartDoc("Alignment Test")
    hdc.StartPage()
    
    dib = ImageWin.Dib(test_image)
    dib.draw(hdc.GetHandleOutput(), (0, 0, printable_area[0], printable_area[1]))
    
    hdc.EndPage()
    hdc.EndDoc()
    hdc.DeleteDC()
    
    print("Alignment test printed successfully!")
    print("\nInstructions:")
    print("1. Check if borders align with card edges")
    print("2. Verify corner marks are at card corners")
    print("3. Adjust 'alignment' values in config.json if needed")
    print("4. Run this test again after adjustments")


if __name__ == "__main__":
    print("=" * 60)
    print("2-Card Tray Alignment Test Tool")
    print("=" * 60)
    
    config = load_config()
    print_alignment_test(config)
    
    print("\n" + "=" * 60)
    print("Test complete!")