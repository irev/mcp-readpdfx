#!/usr/bin/env python3
"""
Create Simple PDF Test File
"""

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    
    def create_test_pdf():
        filename = "test_sample.pdf"
        c = canvas.Canvas(filename, pagesize=letter)
        
        # Add some text
        c.drawString(100, 750, "Test PDF for LM Studio OCR MCP Server")
        c.drawString(100, 730, "This is a sample PDF with text content.")
        c.drawString(100, 710, "Language: English and Indonesian")
        c.drawString(100, 690, "Bahasa: Bahasa Inggris dan Indonesia")
        
        c.showPage()
        c.save()
        
        print(f"✅ Created test PDF: {filename}")
        return filename
    
    if __name__ == "__main__":
        create_test_pdf()
        
except ImportError:
    print("⚠️ reportlab not installed. Creating simple text file instead...")
    
    filename = "test_sample.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("Test file for LM Studio OCR MCP Server\n")
        f.write("This is a sample text file.\n")
        f.write("Language: English and Indonesian\n")
        f.write("Bahasa: Bahasa Inggris dan Indonesia\n")
    
    print(f"✅ Created test text file: {filename}")