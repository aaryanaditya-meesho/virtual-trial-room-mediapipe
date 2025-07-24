#!/usr/bin/env python3
"""
Generate beautiful clothing images for the virtual try-on catalog
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

def create_gradient(width, height, color1, color2, direction='vertical'):
    """Create a gradient background"""
    base = Image.new('RGB', (width, height), color1)
    top = Image.new('RGB', (width, height), color2)
    
    if direction == 'vertical':
        for y in range(height):
            alpha = int(255 * (y / height))
            mask = Image.new('L', (width, height), alpha)
            base.paste(top, (0, 0), mask)
    else:  # horizontal
        for x in range(width):
            alpha = int(255 * (x / width))
            mask = Image.new('L', (width, height), alpha)
            base.paste(top, (0, 0), mask)
    
    return base

def create_shirt_image(color1, color2, name, pattern='solid'):
    """Create a shirt image"""
    width, height = 300, 400
    
    if pattern == 'gradient':
        img = create_gradient(width, height, color1, color2)
    else:
        img = Image.new('RGB', (width, height), color1)
    
    draw = ImageDraw.Draw(img)
    
    # Draw shirt shape
    # Shoulders
    draw.rectangle([80, 50, 220, 70], fill=color2 if pattern == 'solid' else None, outline='white', width=2)
    
    # Body
    draw.rectangle([90, 70, 210, 350], fill=None, outline='white', width=3)
    
    # Sleeves
    draw.ellipse([20, 60, 100, 140], fill=None, outline='white', width=2)
    draw.ellipse([200, 60, 280, 140], fill=None, outline='white', width=2)
    
    # Collar
    draw.polygon([(140, 50), (160, 50), (155, 80), (145, 80)], fill=None, outline='white', width=2)
    
    # Add some style details
    if pattern == 'striped':
        for i in range(5, height-5, 20):
            draw.line([(90, i), (210, i)], fill='white', width=2)
    
    return img

def create_salwar_image(color1, color2, name):
    """Create a salwar suit image"""
    width, height = 300, 400
    img = create_gradient(width, height, color1, color2, 'vertical')
    draw = ImageDraw.Draw(img)
    
    # Draw salwar suit shape
    # Kameez (top)
    draw.rectangle([70, 30, 230, 220], fill=None, outline='gold', width=3)
    
    # Sleeves
    draw.ellipse([20, 40, 80, 120], fill=None, outline='gold', width=2)
    draw.ellipse([220, 40, 280, 120], fill=None, outline='gold', width=2)
    
    # Neckline
    draw.arc([130, 30, 170, 70], 0, 180, fill='gold', width=3)
    
    # Salwar (bottom)
    draw.rectangle([90, 220, 210, 380], fill=None, outline='gold', width=2)
    
    # Dupatta (scarf)
    draw.arc([50, 20, 250, 120], 0, 180, fill='gold', width=2)
    
    # Decorative patterns
    for i in range(3):
        y = 80 + i * 40
        draw.line([(80, y), (220, y)], fill='gold', width=1)
        for x in range(90, 210, 20):
            draw.circle((x, y), 3, fill='gold')
    
    return img

def create_kurta_image(color1, color2, name):
    """Create a kurta image"""
    width, height = 300, 400
    img = create_gradient(width, height, color1, color2, 'horizontal')
    draw = ImageDraw.Draw(img)
    
    # Draw kurta shape
    # Main body
    draw.rectangle([80, 40, 220, 360], fill=None, outline='white', width=3)
    
    # Sleeves
    draw.rectangle([30, 60, 80, 180], fill=None, outline='white', width=2)
    draw.rectangle([220, 60, 270, 180], fill=None, outline='white', width=2)
    
    # Collar (Mandarin style)
    draw.rectangle([140, 40, 160, 80], fill=None, outline='white', width=2)
    
    # Side slits
    draw.line([(80, 280), (80, 360)], fill='white', width=3)
    draw.line([(220, 280), (220, 360)], fill='white', width=3)
    
    # Decorative buttons
    for i in range(5):
        y = 90 + i * 30
        draw.circle((150, y), 4, fill='white', outline='white')
    
    # Traditional patterns
    for i in range(2):
        y = 120 + i * 80
        draw.rectangle([100, y, 200, y+20], fill=None, outline='white', width=1)
    
    return img

def create_saree_image(color1, color2, name):
    """Create a saree image"""
    width, height = 300, 400
    img = create_gradient(width, height, color1, color2, 'vertical')
    draw = ImageDraw.Draw(img)
    
    # Draw saree draping
    # Blouse
    draw.rectangle([80, 30, 220, 130], fill=None, outline='gold', width=3)
    
    # Saree drape over shoulder
    draw.polygon([(60, 40), (100, 20), (200, 40), (240, 60), (220, 130), (80, 130)], 
                fill=None, outline='gold', width=2)
    
    # Saree pleats
    for i in range(6):
        x = 80 + i * 23
        draw.line([(x, 130), (x + 10, 380)], fill='gold', width=2)
    
    # Pallu (decorative end)
    draw.polygon([(180, 20), (280, 60), (260, 160), (200, 130)], fill=None, outline='gold', width=2)
    
    # Border designs
    draw.line([(70, 130), (230, 130)], fill='gold', width=4)
    draw.line([(80, 380), (210, 380)], fill='gold', width=4)
    
    # Traditional motifs
    for i in range(3):
        for j in range(2):
            x, y = 100 + j * 60, 200 + i * 60
            draw.polygon([(x, y), (x+10, y-10), (x+20, y), (x+10, y+10)], fill='gold')
    
    return img

def main():
    """Generate all clothing images"""
    print("🎨 Creating beautiful clothing images...")
    
    # Define clothing items with colors
    shirts = [
        ("white_formal.png", (240, 240, 250), (220, 220, 240), "White Formal Shirt", "solid"),
        ("black_tshirt.png", (30, 30, 40), (50, 50, 60), "Black T-Shirt", "gradient"),
        ("navy_polo.png", (25, 42, 86), (52, 73, 129), "Navy Polo Shirt", "solid"),
        ("pink_casual.png", (255, 182, 193), (255, 160, 180), "Pink Casual Shirt", "gradient"),
        ("checkered_blue.png", (70, 130, 180), (100, 160, 210), "Blue Checkered Shirt", "striped"),
    ]
    
    salwar_suits = [
        ("royal_blue_salwar.png", (65, 105, 225), (100, 149, 237), "Royal Blue Salwar Suit"),
        ("emerald_salwar.png", (50, 205, 50), (34, 139, 34), "Emerald Green Salwar"),
        ("burgundy_salwar.png", (128, 0, 32), (165, 42, 42), "Burgundy Silk Salwar"),
        ("golden_salwar.png", (255, 215, 0), (218, 165, 32), "Golden Salwar Suit"),
        ("lavender_salwar.png", (230, 230, 250), (221, 160, 221), "Lavender Salwar"),
    ]
    
    kurtas = [
        ("cream_kurta.png", (255, 253, 208), (245, 245, 220), "Cream Cotton Kurta"),
        ("maroon_kurta.png", (128, 0, 0), (165, 42, 42), "Maroon Silk Kurta"),
        ("olive_kurta.png", (128, 128, 0), (154, 205, 50), "Olive Green Kurta"),
        ("sky_kurta.png", (135, 206, 235), (176, 224, 230), "Sky Blue Kurta"),
    ]
    
    sarees = [
        ("red_silk_saree.png", (220, 20, 60), (255, 69, 0), "Red Silk Saree"),
        ("teal_saree.png", (0, 128, 128), (72, 209, 204), "Teal Georgette Saree"),
        ("purple_saree.png", (128, 0, 128), (186, 85, 211), "Purple Banarasi Saree"),
        ("peach_saree.png", (255, 218, 185), (255, 160, 122), "Peach Cotton Saree"),
        ("wine_saree.png", (114, 47, 55), (165, 42, 42), "Wine Colored Saree"),
        ("mint_saree.png", (152, 255, 152), (144, 238, 144), "Mint Green Saree"),
    ]
    
    # Create shirt images
    for filename, color1, color2, name, pattern in shirts:
        img = create_shirt_image(color1, color2, name, pattern)
        img.save(filename)
        print(f"✅ Created {filename}")
    
    # Create salwar suit images
    for filename, color1, color2, name in salwar_suits:
        img = create_salwar_image(color1, color2, name)
        img.save(filename)
        print(f"✅ Created {filename}")
    
    # Create kurta images
    for filename, color1, color2, name in kurtas:
        img = create_kurta_image(color1, color2, name)
        img.save(filename)
        print(f"✅ Created {filename}")
    
    # Create saree images
    for filename, color1, color2, name in sarees:
        img = create_saree_image(color1, color2, name)
        img.save(filename)
        print(f"✅ Created {filename}")
    
    print("🎉 All clothing images created successfully!")

if __name__ == "__main__":
    main() 