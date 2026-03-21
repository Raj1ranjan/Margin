# Margin - PDF Manipulation Tool

A modern, user-friendly PDF manipulation application built with PyQt6. Perform common PDF operations through an intuitive natural language interface.

## Features

### Core Operations
- **Extract Pages**: Extract specific pages or page ranges from PDFs
- **Delete Pages**: Remove unwanted pages from PDFs
- **Merge PDFs**: Combine multiple PDFs into one document
- **Insert Pages**: Insert pages from one PDF into another
- **Compress PDFs**: Reduce PDF file size with quality options (low/medium/high)

### User Interface
- **Dark Theme**: Modern, eye-friendly dark interface
- **Visual PDF Viewer**: Zoom and navigate through PDF pages
- **Drag & Drop**: Import PDFs by dragging files into the application
- **Rich File Metadata**: View file size and page count for each PDF
- **Progress Feedback**: Real-time progress indicators for long operations
- **Keyboard Shortcuts**: Efficient navigation and operation triggering

### Advanced Features
- **Natural Language Commands**: Type commands like "extract pages 1-5" or "merge PDFs"
- **Async Processing**: Non-blocking operations for large files
- **Comprehensive Logging**: Detailed operation logs for debugging
- **Input Validation**: Prevents invalid operations with helpful error messages
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Installation

### Prerequisites
- Python 3.8 or higher
- Ghostscript (for PDF compression)

### Install Ghostscript
```bash
# Linux (Ubuntu/Debian)
sudo apt-get install ghostscript

# macOS
brew install ghostscript

# Windows
# Download from: https://www.ghostscript.com/
```

### Setup
```bash
# Clone or download the project
cd margin

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Usage

### Basic Workflow
1. **Import PDFs**: Click "Import PDFs" or drag files into the sidebar
2. **Select Files**: Click to select individual files, Ctrl+Click for multiple
3. **Enter Commands**: Type natural language commands in the command bar
4. **Execute**: Press Enter or Ctrl+Enter to run operations
5. **View Results**: Generated PDFs appear in the results section

### Example Commands
```
extract pages 1-5
extract pages 1, 3, 7
delete pages 10-15
merge
insert page 3 of first pdf into second pdf at page 5
compress high
```

### Keyboard Shortcuts
- `Ctrl+O`: Open file dialog
- `Ctrl+Z`: Undo last operation
- `Ctrl+Enter`: Execute command
- `Delete`: Remove selected files
- `F1`: Show help

## Architecture

### Project Structure
```
margin/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── assets/
│   └── styles/
│       └── dark_theme.qss  # UI styling
├── core/
│   ├── command_parser.py   # Natural language parsing
│   └── executor.py         # Operation execution
├── services/
│   ├── pdf_service.py      # Core PDF operations
│   └── pdf_compressor.py   # Compression service
├── ui/
│   ├── main_window.py      # Main application window
│   ├── sidebar.py          # File management sidebar
│   ├── dialogs.py          # Dialog boxes
│   ├── workers.py          # Async operation workers
│   └── components/
│       ├── pdf_viewer.py   # PDF viewing component
│       └── file_item.py    # File list items
├── models/
│   └── state_manager.py    # Application state
└── utils/
    └── logger.py           # Logging utilities
```

### Key Components
- **Command Parser**: Regex-based natural language processing
- **Async Workers**: Thread-based operation execution
- **State Manager**: Undo/redo functionality
- **PDF Services**: PyPDF2 and PyMuPDF integration
- **UI Components**: Modular PyQt6 interface

## Development

### Running Tests
```bash
# No tests implemented yet
# TODO: Add unit tests for core functionality
```

### Building for Distribution
```bash
# Create executable (requires PyInstaller)
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source. See LICENSE file for details.

## Troubleshooting

### Common Issues

**"Ghostscript not found"**
- Install Ghostscript as described in the installation section
- Ensure it's in your system PATH

**"No module named 'PyQt6'"**
- Install dependencies: `pip install -r requirements.txt`
- Ensure you're using the correct Python version

**UI doesn't start**
- Check that you're in a graphical environment
- Try running with `python main.py` from the project directory

**Operations fail silently**
- Check the `logs/` directory for error details
- Ensure PDF files are not corrupted or password-protected

### Getting Help
- Check the in-app help (F1 key)
- Review the logs in the `logs/` directory
- Open an issue on the project repository

## Changelog

### Version 1.0.0
- Initial release with core PDF operations
- Dark theme UI with drag-and-drop support
- Natural language command interface
- Async processing for better performance
- Comprehensive logging and error handling