# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PID-Tag Puller is a PDF analysis tool designed to read Piping and Instrumentation Diagrams (P&IDs) and extract equipment tags for export. The application analyzes P&ID PDF files and identifies tags for:
- Equipment
- Instruments
- Valves
- Actuated valves

The extracted tags are exported to a CSV file with all tags listed in a single column.

## Application Architecture

### Core Components

1. **PDF Processing Module**: Handles reading and parsing P&ID PDF files, extracting text and potentially graphical elements
2. **Tag Extraction Engine**: Identifies and extracts various tag types from the parsed P&ID content using pattern matching or OCR
3. **User Interface**: GUI for file selection (input PDF) and directory selection (output CSV location)
4. **CSV Export Module**: Formats and writes extracted tags to a single-column CSV file

### Tag Pattern Recognition

Based on the reference P&ID (ST0008_P1011-1_3_WIP.pdf), the following tag patterns should be extracted:

**Equipment Tags:**
- Pumps: `STORM_P####-#` format (e.g., STORM_P1001-1, STORM_P1011-1, STORM_P1012-1)
- Pumps (alternate): `P####` format (e.g., P1021, P1031, P1041, P1051)
- Rock Traps: `ROCK TRAP #` format (e.g., ROCK TRAP 1, ROCK TRAP 2)
- Vendor packages and equipment: Various alphanumeric codes (KD1, KD2, etc.)
- Other equipment: Pattern matching for alphanumeric identifiers with hyphens or underscores

**Valve Tags:**
- Primary pattern: `VLV####` (e.g., VLV1001, VLV2041, VLV2043)
- Valves may appear with or without associated instrument tags
- Both manual and automated valves use the VLV prefix

**Instrument Tags:**
- Format: `XX-XX-XX-####` (e.g., QD-1E-84-1101, QD-1E-84-1102)
- Complex alphanumeric codes with hyphens as separators
- May include location and function identifiers

**Actuated Valve Tags:**
- Valves with associated control symbols or actuator indicators
- Often identified by nearby instrument tags or control connections
- May share the VLV#### numbering scheme

**Extraction Considerations:**
- Tags are embedded within the PDF, likely as selectable text
- Drawing number (ST0008), sheet number (P1011-1), and revision (3) should NOT be extracted as tags
- Page metadata like "SHEET No." and "DRAWING STATUS" should be filtered out
- Legend items (EXISTING LAUNDER, WATER CANNON, etc.) are descriptive text, not tags
- Note references (NOTE 1, NOTE 2, etc.) should be excluded

## Tech Stack

**Language:** Python 3.9+ (uses `from __future__ import annotations` for type hints)
**PDF Processing:**
- pdfplumber - Clean API for extracting selectable text from PDFs
- PyMuPDF (fitz) - Renders PDF pages as images for OCR
**OCR (Optical Character Recognition):**
- pytesseract - Python wrapper for Tesseract OCR
- Tesseract 5.x - OCR engine (installed via Homebrew on macOS: `brew install tesseract`)
- Pillow - Image processing for OCR pipeline
**GUI Framework:** CustomTkinter - Modern, lightweight GUI with dark/light themes
**Pattern Matching:** re (built-in) - Standard Python regex for tag identification
**CSV Export:** csv (built-in) - Native Python CSV handling
**Testing:** pytest - Standard Python testing framework
**Code Quality:** ruff - Fast Python linter and formatter
**Packaging:** PyInstaller - Create standalone executables

### Project Structure
```
src/
├── gui/              # GUI components (CustomTkinter)
│   ├── main_window.py
│   └── widgets.py
├── pdf_processor/    # PDF text extraction (pdfplumber)
│   └── extractor.py
├── tag_extractor/    # Pattern matching & tag identification
│   ├── patterns.py   # Regex patterns for different tag types
│   └── extractor.py
└── csv_exporter/     # CSV generation
    └── exporter.py
```

## Development Commands

### Setup
```bash
# Install Tesseract OCR (macOS)
brew install tesseract

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Activate virtual environment first
source venv/bin/activate

# Run the application
python src/main.py
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_tag_extractor.py
```

### Linting/Formatting
```bash
# Format code
ruff format .

# Lint code
ruff check .

# Fix auto-fixable issues
ruff check --fix .
```

### Building Executable
```bash
# Create standalone executable
pyinstaller --onefile --windowed src/main.py
```

## Key Considerations

### PDF Processing Challenges
- **Image-Based P&IDs:** The reference P&ID (ST0008_P1011-1_3_WIP.pdf) has tags embedded in an image, NOT as selectable text
- **Hybrid Approach:** The application first attempts standard text extraction, then falls back to OCR if minimal text is found (< 200 characters)
- **OCR Considerations:**
  - Tesseract OCR is configured for sparse text (PSM 11) to handle engineering diagrams
  - Pages are rendered at 2x resolution (144 DPI) for better OCR accuracy
  - OCR may produce some errors (e.g., "VLVXX61" instead of actual numbers, "0" vs "O")
  - Processing time is longer for OCR compared to text extraction
- Text may be rotated (90°, 270°) to align with vertical pipes or equipment
- Drawing contains dense areas where tags may overlap with process graphics
- Title block, notes section, and legend contain text that should NOT be extracted as tags

### Tag Extraction Accuracy
- **False Positive Filtering:** Exclude common non-tag elements:
  - Drawing identifiers: ST#### pattern
  - Sheet numbers: P####-# pattern when standalone
  - Note references: "NOTE #" pattern
  - Grid coordinates: Single letters (A-G) and numbers (1-12) at page borders
  - Title block content: Company names, project titles, dates
  - Legend items: Descriptive text like "EXISTING", "PROPOSED", "WATER CANNON"
  - Dimensional text and flow direction indicators

- **Validation Rules:**
  - VLV tags must be followed by digits (VLV####)
  - Equipment tags often contain hyphens (STORM_P####-#)
  - Instrument tags have specific hyphen-separated format (XX-XX-XX-####)
  - Tags are typically uppercase

- **Duplicate Handling:**
  - Same tag may appear multiple times on the drawing (e.g., STORM_P1001-1 appears at multiple connection points)
  - Decision needed: Report all instances or deduplicate to unique tags only

- **Context-Based Validation:**
  - Tags typically appear near or within equipment symbols, valve symbols, or instrument bubbles
  - Isolated text in title blocks, notes, or margins is likely not a tag

### Output Format
- CSV file with single column containing all extracted tags
- Header row: "Tag" (or configurable/optional)
- Tag ordering: Consider sorting alphabetically or by tag type for easier review
- Duplicate handling strategy should be documented and consistent
- Example output format:
  ```
  Tag
  P1021
  P1031
  P1041
  ROCK TRAP 1
  ROCK TRAP 2
  STORM_P1001-1
  STORM_P1011-1
  VLV1001
  VLV1002
  VLV2041
  ```

### User Experience
- Provide clear feedback on extraction progress for large PDF files
- Display count of extracted tags before export (e.g., "Found 47 unique tags")
- Show breakdown by tag type if possible (e.g., "12 valves, 8 pumps, 15 instruments")
- Handle errors gracefully:
  - Corrupted or password-protected PDFs
  - No tags found (empty result)
  - Write permission issues for output directory
  - Invalid PDF format or non-P&ID documents
- Consider preview functionality showing first 10-20 extracted tags before export

## Test Material

**Reference P&ID:** `Test_Material/ST0008_P1011-1_3_WIP.pdf`
- **Project:** Malabar Package 3 - Fairfield WRRF Upgrade - Water Resource Recovery Facility
- **Drawing:** ST0008 - Process and Instrumentation Diagram
- **Sheet:** P1011-1 (Existing and Proposed)
- **Content:** Water resource recovery system with pumps, valves, rock traps, vendor packages
- **Tag Density:** High - contains numerous equipment, valve, and instrument tags
- **Use Case:** Ideal for testing extraction accuracy, false positive filtering, and duplicate handling

**Expected Performance Criteria:**
- Successfully extract all VLV#### tags (dozens present)
- Identify all pump tags (STORM_P####-# and P#### formats)
- Capture instrument tags with complex hyphenated format
- Extract equipment tags like ROCK TRAP #
- Exclude drawing number (ST0008), sheet number (P1011-1), and metadata
- Handle repeated instances of same tag (e.g., STORM_P1001-1 appears multiple times)

**Current Performance (v0.1.0):**
- Extracting ~30 unique tags from reference P&ID
- Successfully identifies: Valves, Pumps, Equipment, Generic tags (XXX####)
- OCR uses dual-pass approach (PSM 6 + PSM 11)
- **Known Limitations:**
  - May miss some tags due to OCR accuracy limitations
  - Instrument circles with split text (top/bottom) not specifically targeted
  - Pattern matching may need refinement for project-specific tag conventions
  - OCR performance depends on PDF image quality and text clarity

## Known Issues & Future Improvements

### Tag Extraction Refinement Needed
The current tag extraction implementation provides a solid foundation but requires further development:

1. **OCR Accuracy**:
   - Consider image preprocessing (contrast enhancement, noise reduction)
   - Experiment with different Tesseract configurations
   - May need higher resolution rendering (3x or 4x) for small text

2. **Pattern Recognition**:
   - Current patterns may not cover all project-specific tag conventions
   - Need validation against multiple P&ID drawings from same project
   - May require adjustments for different engineering firms' standards

3. **Instrument Circle Detection**:
   - Current approach extracts all text; doesn't specifically target circles
   - Could use OpenCV for shape detection to identify instrument bubbles
   - Would enable proper top/bottom text splitting for circle-enclosed tags

4. **False Positive Filtering**:
   - Exclusion patterns may need expansion based on real-world usage
   - Consider adding confidence scoring for extracted tags
   - May need manual review/correction workflow for borderline cases

5. **Performance Optimization**:
   - Dual OCR pass increases processing time
   - Could parallelize OCR operations for multi-page PDFs
   - Consider caching OCR results for repeated processing
