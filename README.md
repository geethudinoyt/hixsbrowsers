# Modern Web Browser

A fully-featured, modern web browser built with PyQt5 and PyQtWebEngine.

## Features

### Core Functionality
- **Tabbed Browsing**: Multiple tabs with close, move, and switch functionality
- **Navigation**: Back, Forward, Reload, Stop, and Home buttons
- **Smart URL Bar**: Automatically detects URLs vs search queries
- **Search Integration**: Google search built into the address bar
- **Progress Indicator**: Loading progress bar and status updates

### Advanced Features
- **Keyboard Shortcuts**: Full keyboard navigation support
- **File Operations**: Open local HTML files, save web pages
- **Zoom Controls**: Zoom in/out and reset functionality
- **Full Screen Mode**: Immersive browsing experience
- **Modern UI**: Clean, professional interface with hover effects
- **Context Menu**: Comprehensive menu system
- **History Management**: View and clear browsing history

### Keyboard Shortcuts

#### Navigation
- `Alt + ←` : Back
- `Alt + →` : Forward  
- `F5` : Reload
- `Esc` : Stop loading
- `Alt + Home` : Go to home page

#### Tab Management
- `Ctrl + T` : New tab
- `Ctrl + W` : Close current tab
- `Ctrl + Tab` : Next tab
- `Ctrl + Shift + Tab` : Previous tab

#### File Operations
- `Ctrl + O` : Open file
- `Ctrl + S` : Save page

#### View Controls
- `Ctrl + F` : Find in page
- `Ctrl + +` : Zoom in
- `Ctrl + -` : Zoom out
- `Ctrl + 0` : Reset zoom
- `F11` : Toggle full screen

## Installation

### Prerequisites
- Python 3.6 or higher
- pip package manager

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Manual Installation
```bash
pip install PyQt5==5.15.9
pip install PyQtWebEngine==5.15.5
```

## Usage

### Run the Browser
```bash
python browser.py
```

### Basic Usage
1. **Navigate**: Enter URLs or search queries in the address bar
2. **Tabs**: Use the `+` button or `Ctrl+T` to create new tabs
3. **Menu**: Click the `⋮` button for additional options
4. **Shortcuts**: Use keyboard shortcuts for faster navigation

### Tips
- The address bar automatically detects if you're entering a URL or search query
- Right-click functionality is available through the menu button
- Tabs can be rearranged by dragging
- The browser supports local file browsing

## Technical Details

### Architecture
- **Main Window**: `ModernWebBrowser` class manages the UI and overall functionality
- **Tab Management**: Each tab is a `BrowserTab` instance with enhanced web engine settings
- **Styling**: CSS-like styling system for modern appearance
- **Signal/Slot**: Qt's signal-slot mechanism for event handling

### Dependencies
- **PyQt5**: GUI framework and core widgets
- **PyQtWebEngine**: Web rendering engine based on Chromium

### Browser Features Enabled
- JavaScript execution
- Plugin support
- Local storage
- WebGL rendering
- Modern web standards

## Troubleshooting

### Common Issues

#### "ModuleNotFoundError: No module named 'PyQt5'"
```bash
pip install PyQt5 PyQtWebEngine
```

#### Browser doesn't load pages
- Check internet connection
- Ensure PyQtWebEngine is properly installed
- Try running as administrator on Windows

#### Performance issues
- Close unused tabs
- Clear browsing history
- Restart the browser

### Platform-Specific Notes

#### Windows
- May require Visual C++ redistributable
- Run as administrator for file access

#### macOS
- May need to allow network access in System Preferences
- Use `python3` instead of `python` if needed

#### Linux
- Install additional system packages if needed:
```bash
# Ubuntu/Debian
sudo apt-get install python3-pyqt5 python3-pyqt5.qtwebengine

# Fedora
sudo dnf install python3-qt5 python3-qt5-webengine
```

## Development

### Code Structure
```
browser.py          # Main application file
requirements.txt    # Python dependencies
README.md          # Documentation
```

### Extending the Browser
- Add new menu items in the `show_menu()` method
- Implement new features by connecting to browser signals
- Customize styling by modifying the stylesheet
- Add new keyboard shortcuts in `create_shortcuts()`

## License

This project is provided as-is for educational and personal use.

## Contributing

Feel free to submit issues and enhancement requests!
