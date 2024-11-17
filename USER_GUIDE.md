# LARK Casebook Editor User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Basic Navigation](#basic-navigation)
3. [File Management](#file-management)
4. [Editor Features](#editor-features)
5. [Search and Replace](#search-and-replace)
6. [Keyboard Shortcuts](#keyboard-shortcuts)
7. [Export and Import](#export-and-import)

## Getting Started

### Installation
1. Ensure Python 3.12 or higher is installed
2. Install required packages: `pip install -r requirements.txt`
3. Run the editor: `python main.py`

### Interface Overview
- File tree on the left
- Editor area on the right
- Toolbar at the top
- Status bar at the bottom
- Quick action bar (activated with Ctrl+P)

## Basic Navigation

### File Tree
- Click folders to expand/collapse
- Double-click files to open
- Right-click for context menu
- Files are color-coded by type

### Tabs
- Click to switch between files
- Middle-click or click 'x' to close
- Drag to reorder
- Asterisk (*) indicates unsaved changes

## File Management

### Opening Files
1. Use File → Open (Ctrl+O)
2. Double-click in file tree
3. Quick Open (Ctrl+P):
   - Press Ctrl+P
   - Start typing filename
   - Use arrow keys to navigate results
   - Press Enter to open selected file
   - Results update in real-time
   - Shows relative paths
   - ESC to close

### Recent Files
- Access from File → Recent Files
- Last 10 files are remembered
- Click to reopen

## Editor Features

### Syntax Highlighting
- Automatic language detection
- Dark theme with consistent colors:
  * Keywords: Pink (#F92672)
  * Strings: Yellow (#E6DB74)
  * Comments: Grayish blue (#6272A4)
  * Numbers: Purple (#AE81FF)
  * Functions: Green (#A6E22E)
  * Classes: Light blue (#66D9EF)

### Code Editing
- Line numbers
- Current line highlighting
- Undo/Redo (Ctrl+Z/Ctrl+Y)
- Cut/Copy/Paste
- Auto-indentation
- Multiple cursors

### View Options
- Zoom in/out (Ctrl+/Ctrl-)
- Mouse wheel zoom (Ctrl+Scroll)
- Word wrap toggle
- Show/hide line numbers

## Search and Replace

### Quick File Search (Ctrl+P)
- Real-time search as you type
- Shows relative file paths
- Keyboard navigation:
  * Up/Down arrows to move selection
  * Enter to open selected file
  * Esc to close
- Results limited to 50 for performance
- Double-click to open file

### Find in Files (Ctrl+F)
- Search in current file or all files
- Regular expression support
- Case sensitivity toggle
- Whole word matching
- Results preview with context
- Search history
- Navigate results with Up/Down

### Replace (Ctrl+H)
- Replace in current file or all files
- Preview changes before applying
- Regular expression support
- Case sensitivity toggle
- Whole word matching
- Replace history
- Undo support for replacements

## Export and Import

### Project Export/Import
- To export your project:
  1. Go to `File → Export/Import → Export Project...`
  2. The project will be exported as a ZIP file with timestamp
  3. Progress will be shown during export
  4. You'll be notified when export is complete

- To import a project:
  1. Go to `File → Export/Import → Import Project...`
  2. Select the project ZIP file
  3. Choose the target directory
  4. Option to open the imported project will be offered

### Settings Export/Import
- To export settings:
  1. Go to `File → Export/Import → Export Settings...`
  2. Choose where to save the settings JSON file
  3. All current settings will be exported

- To import settings:
  1. Go to `File → Export/Import → Import Settings...`
  2. Select the settings JSON file
  3. Settings will be imported
  4. Some changes may require restart

### File Export
- To export current file:
  1. Go to `File → Export/Import → Export Current File As...`
  2. Choose from available formats:
     * Plain Text (.txt)
     * HTML with syntax highlighting
     * Markdown (.md)
     * PDF (coming soon)
  3. Select save location
  4. Progress will be shown for large files

### Notes
- Exports are non-blocking (UI remains responsive)
- Failed exports are automatically cleaned up
- Export operations can be cancelled
- Progress is shown for long operations

## Keyboard Shortcuts

### File Operations
- Ctrl+N: New file
- Ctrl+O: Open file
- Ctrl+S: Save
- Ctrl+Shift+S: Save as
- Ctrl+P: Quick open
- Ctrl+W: Close tab
- Ctrl+Q: Quit

### Editing
- Ctrl+Z: Undo
- Ctrl+Y: Redo
- Ctrl+X: Cut
- Ctrl+C: Copy
- Ctrl+V: Paste
- Ctrl+A: Select all

### Search
- Ctrl+P: Quick file search
- Ctrl+F: Find
- Ctrl+H: Replace
- F3: Find next
- Shift+F3: Find previous
- Esc: Close search

### View
- Ctrl+Plus: Zoom in
- Ctrl+Minus: Zoom out
- Ctrl+0: Reset zoom
- F11: Toggle full screen

### Navigation
- Ctrl+Tab: Next tab
- Ctrl+Shift+Tab: Previous tab
- Alt+Left: Go back
- Alt+Right: Go forward
