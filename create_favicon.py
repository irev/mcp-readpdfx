#!/usr/bin/env python3
"""
Create favicon.ico from logo.png
"""

from PIL import Image
import os

def create_favicon():
    """Convert logo.png to favicon.ico with multiple sizes"""
    
    # Check if logo.png exists
    if not os.path.exists("logo.png"):
        print("❌ logo.png not found!")
        return False
    
    try:
        # Open the logo image
        logo = Image.open("logo.png")
        
        # Convert to RGBA if necessary
        if logo.mode != 'RGBA':
            logo = logo.convert('RGBA')
        
        # Create different sizes for favicon
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
        favicon_images = []
        
        for size in sizes:
            resized = logo.resize(size, Image.Resampling.LANCZOS)
            favicon_images.append(resized)
        
        # Save as favicon.ico
        favicon_images[0].save(
            "favicon.ico",
            format='ICO',
            sizes=[(img.width, img.height) for img in favicon_images],
            append_images=favicon_images[1:]
        )
        
        print("✅ favicon.ico created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating favicon: {e}")
        return False

if __name__ == "__main__":
    create_favicon()