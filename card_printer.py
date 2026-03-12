"""
Main Card Printing Script
Prints PVC ID cards using Epson 4830 with 2-card tray
Integrates with Adobe Photoshop CS5 and uses Adobe color profiles
"""

import json
import os
from PIL import Image, ImageDraw, ImageFont
import win32print
import win32ui
from PIL import ImageWin
from excel_reader import read_card_data


def load_config():
    """Load configuration from config.json"""
    with open('config.json', 'r') as f:
        return json.load(f)


def create_card_image(card_data, config):
    """
    Create ID card image from data
    
    Args:
        card_data: Dictionary with card information
        config: Configuration dictionary
    
    Returns:
        PIL Image object
    """
    dpi = config['photoshop']['resolution_dpi']
    card_width_inches = config['printer']['card_width_inches']
    card_height_inches = config['printer']['card_height_inches']
    
    # Convert to pixels (CR80 standard: 3.375" x 2.125")
    card_width_px = int(card_width_inches * dpi)
    card_height_px = int(card_height_inches * dpi)
    
    # Create card with white background
    card = Image.new('RGB', (card_width_px, card_height_px), 'white')
    draw = ImageDraw.Draw(card)
    
    # Load fonts
    try:
        font_large = ImageFont.truetype("arial.ttf", 48)
        font_medium = ImageFont.truetype("arial.ttf", 32)
        font_small = ImageFont.truetype("arial.ttf", 24)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Draw card border
    border_color = (0, 102, 204)  # Adobe blue
    draw.rectangle(
        [(10, 10), (card_width_px-10, card_height_px-10)],
        outline=border_color,
        width=3
    )
    
    # Add photo if provided
    photo_path = card_data.get('Photo', '')
    if photo_path and os.path.exists(photo_path):
        try:
            photo = Image.open(photo_path)
            photo_size = (200, 250)  # Adjust as needed
            photo = photo.resize(photo_size, Image.Resampling.LANCZOS)
            card.paste(photo, (30, 50))
        except Exception as e:
            print(f"Warning: Could not load photo {photo_path}: {e}")
    
    # Add text information
    text_x = 260
    y_position = 60
    line_spacing = 50
    
    # Name (large)
    name = card_data.get('Name', 'NO NAME')
    draw.text((text_x, y_position), name, fill='black', font=font_large)
    y_position += line_spacing + 20
    
    # Title
    title = card_data.get('Title', '')
    if title:
        draw.text((text_x, y_position), title, fill=(50, 50, 50), font=font_medium)
        y_position += line_spacing
    
    # Department
    department = card_data.get('Department', '')
    if department:
        draw.text((text_x, y_position), f"Dept: {department}", fill=(80, 80, 80), font=font_small)
        y_position += line_spacing - 10
    
    # ID Number
    id_num = card_data.get('ID', '')
    if id_num:
        draw.text((text_x, y_position), f"ID: {id_num}", fill='black', font=font_medium)
    
    # Email (bottom)
    email = card_data.get('Email', '')
    if email:
        draw.text((30, card_height_px - 50), email, fill=(100, 100, 100), font=font_small)
    
    return card


def create_dual_card_layout(card1_data, card2_data, config):
    """
    Create layout for 2 cards in the plastic tray
    
    Args:
        card1_data: Data for first card
        card2_data: Data for second card (or None)
        config: Configuration dictionary
    
    Returns:
        PIL Image with both cards positioned correctly
    """
    dpi = config['photoshop']['resolution_dpi']
    card_width_inches = config['printer']['card_width_inches']
    card_height_inches = config['printer']['card_height_inches']
    
    card_width_px = int(card_width_inches * dpi)
    card_height_px = int(card_height_inches * dpi)
    
    # Get spacing from config
    spacing_mm = config['tray']['spacing_between_cards_mm']
    spacing_px = int((spacing_mm / 25.4) * dpi)

    # Tray depression compensation: accounts for the physical indentation in the
    # 2-card plastic tray where cards sit, which can shift the effective print area.
    depression_comp_x_px = int((config['tray'].get('tray_depression_compensation_x_mm', 0) / 25.4) * dpi)
    depression_comp_y_px = int((config['tray'].get('tray_depression_compensation_y_mm', 0) / 25.4) * dpi)

    # Create full print area
    total_width = (card_width_px * 2) + spacing_px
    total_height = card_height_px;
    
    print_image = Image.new('RGB', (total_width, total_height), 'white')
    
    # Create and place card 1
    card1_img = create_card_image(card1_data, config)
    offset_x1 = int((config['tray']['card1_offset_x_mm'] / 25.4) * dpi) + depression_comp_x_px
    offset_y1 = int((config['tray']['card1_offset_y_mm'] / 25.4) * dpi) + depression_comp_y_px
    print_image.paste(card1_img, (offset_x1, offset_y1))
    
    # Create and place card 2 (if data provided)
    if card2_data:
        card2_img = create_card_image(card2_data, config)
        offset_x2 = card_width_px + spacing_px + int((config['tray']['card2_offset_x_mm'] / 25.4) * dpi) + depression_comp_x_px
        offset_y2 = int((config['tray']['card2_offset_y_mm'] / 25.4) * dpi) + depression_comp_y_px
        print_image.paste(card2_img, (offset_x2, offset_y2))
    
    return print_image


def print_cards(card_list, config):
    """
    Print cards to Epson 4830 using 2-card tray
    
    Args:
        card_list: List of card data dictionaries
        config: Configuration dictionary
    """
    printer_name = config['printer']['name']
    
    print(f"\nPrinting {len(card_list)} cards to {printer_name}")
    print("Cards will be printed 2 at a time...\n")
    
    # Process cards in pairs
    for i in range(0, len(card_list), 2):
        card1 = card_list[i]
        card2 = card_list[i+1] if i+1 < len(card_list) else None;
        
        print(f"Processing cards {i+1}" + (f" and {i+2}" if card2 else ""));
        
        # Create dual-card layout
        print_image = create_dual_card_layout(card1, card2, config);
        
        # Save preview
        preview_filename = f"card_preview_{i+1}.png";
        print_image.save(preview_filename);
        print(f"  Preview saved: {preview_filename}")
        
        # Print to Epson 4830
        try:
            hdc = win32ui.CreateDC();
            hdc.CreatePrinterDC(printer_name);
            
            printable_area = hdc.GetDeviceCaps(8), hdc.GetDeviceCaps(10);
            
            hdc.StartDoc(f"ID Cards {i+1}");
            hdc.StartPage();
            
            dib = ImageWin.Dib(print_image);
            dib.draw(hdc.GetHandleOutput(), (0, 0, printable_area[0], printable_area[1]));
            
            hdc.EndPage();
            hdc.EndDoc();
            hdc.DeleteDC();
            
            print(f"  ✓ Printed successfully!");
            
        except Exception as e:
            print(f"  ✗ Print error: {e}");
        
        # Prompt for next batch
        if i+2 < len(card_list):
            input("\nPress Enter when ready to print next batch...")


if __name__ == "__main__":
    print("=" * 60)
    print("ID Card Printer - Epson 4830 with 2-Card Tray")
    print("=" * 60)
    
    # Load configuration
    config = load_config();
    
    # Read card data from Excel
    card_data = read_card_data();
    
    if not card_data:
        print("\nNo card data found. Please:");
        print("1. Edit card_data.xlsx with your card information");
        print("2. Run this script again");
    else:
        print(f"\nFound {len(card_data)} cards to print");
        print(f"Will print in {(len(card_data) + 1) // 2} batches (2 cards per batch)");
        
        response = input("\nContinue with printing? (y/n): ");
        if response.lower() == 'y':
            print_cards(card_data, config);
            print("\n" + "=" * 60);
            print("Printing complete!");
            print("=" * 60);
        else:
            print("Printing cancelled.")
