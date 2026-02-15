# PID-Tag Puller

A desktop application for extracting equipment tags from Piping and Instrumentation Diagrams (P&IDs) in PDF format.

## Features

- Extract equipment, valve, instrument, and actuated valve tags from P&ID PDFs
- Modern GUI for easy file selection and operation
- Export results to CSV format with single column output
- Support for various P&ID tag naming conventions

## Installation

### Prerequisites
- Python 3.11 or higher

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd PID-Tag-Puller

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Activate virtual environment
source venv/bin/activate

# Run the application
python src/main.py
```

1. Click "Select PDF" to choose your P&ID file
2. Click "Select Output Directory" to choose where to save the CSV
3. Click "Extract Tags" to process the PDF
4. Review the extracted tags and export to CSV

## Development

See [CLAUDE.md](CLAUDE.md) for detailed development guidance.

### Running Tests
```bash
pytest
```

### Code Quality
```bash
ruff check .
ruff format .
```

## License

[To be determined]
