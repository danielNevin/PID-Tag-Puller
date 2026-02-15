"""Quick test script to verify tag extraction works."""

import sys
sys.path.insert(0, 'src')

from pathlib import Path
from pdf_processor.extractor import PDFExtractor
from tag_extractor.extractor import TagExtractor

# Test with the reference P&ID
test_pdf = Path("Test_Material/ST0008_P1011-1_3_WIP.pdf")

if not test_pdf.exists():
    print(f"Error: Test PDF not found at {test_pdf}")
    sys.exit(1)

print("Testing PID-Tag Puller extraction...")
print(f"PDF: {test_pdf}")
print("-" * 60)

# Extract text from PDF
print("\n1. Extracting text from PDF...")
pdf_extractor = PDFExtractor(test_pdf)
text = pdf_extractor.extract_text()
print(f"   ✓ Extracted {len(text)} characters from {pdf_extractor.get_page_count()} page(s)")

# Extract tags
print("\n2. Identifying tags...")
tag_extractor = TagExtractor(text)
tags = tag_extractor.extract_all_tags(deduplicate=True)
summary = tag_extractor.get_summary()

print(f"   ✓ Found {summary['total_unique']} unique tags")
print(f"   - Pumps: {summary['pumps']}")
print(f"   - Valves: {summary['valves']}")
print(f"   - Instruments: {summary['instruments']}")
print(f"   - Equipment: {summary['equipment']}")
print(f"   - Other: {summary['other']}")

# Show sample tags
print("\n3. Sample tags (first 20):")
for i, tag in enumerate(tags[:20], 1):
    print(f"   {i:2}. {tag}")

if len(tags) > 20:
    print(f"   ... and {len(tags) - 20} more tags")

print("\n✓ Extraction test completed successfully!")
