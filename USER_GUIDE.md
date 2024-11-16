# Casebook Editor User Guide

## Getting Started

### Installation

1. Install Python 3.12 or higher from [python.org](https://python.org)
2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Editor

```bash
python main.py
```

## Interface Overview

### Main Window
The editor window is divided into several sections:
- Left: File tree for project navigation
- Center: Editor tabs for open files
- Right: Minimap for code overview
- Bottom: Status bar showing file info and cursor position
- Top: Menu bar and toolbar with common actions

### File Tree
- Shows all files in the current project directory
- Double-click a file to open it
- Right-click for context menu:
  * Open file
  * Rename file
  * Delete file

### Editor Tabs
- Shows all open files
- Drag tabs to reorder
- Right-click for tab options:
  * Save
  * Save As
  * Close
  * Close All

### Minimap
- Shows zoomed-out view of code
- Highlights current viewport position
- Click or drag to navigate
- Updates in real-time as you type
- Adjusts to editor theme colors

### Status Bar
Shows information about the current file:
- File name
- Cursor position (line and column)
- File encoding
- Line ending type
- Current scene name

### Toolbar
Quick access to common actions:
- New file
- Open file
- Save file
- Undo/Redo
- Zoom controls

## File Management

### Creating New Files
1. Click "New" in toolbar or press Ctrl+N
2. Start typing your content
3. Save with Ctrl+S when ready

### Opening Files
Multiple ways to open files:
1. Click "Open" in toolbar or press Ctrl+O
2. Double-click file in file tree
3. Use Quick Open (Ctrl+P) to search and open files
4. Select from Recent Files menu

### Quick Open (Ctrl+P)
1. Press Ctrl+P to open the dialog
2. Type part of the filename
3. Use arrow keys to select
4. Press Enter to open selected file

### Saving Files
- Save (Ctrl+S): Save current file
- Save As (Ctrl+Shift+S): Save with new name
- Auto-save: Files are automatically saved every minute

### File Change Detection
If a file is modified outside the editor:
1. You'll be notified of external changes
2. Choose to reload the file or keep your version
3. Auto-save helps prevent conflicts

## Editing Features

### Basic Editing
- Cut: Ctrl+X
- Copy: Ctrl+C
- Paste: Ctrl+V
- Undo: Ctrl+Z
- Redo: Ctrl+Y or Ctrl+Shift+Z

### Navigation
- Arrow keys: Move cursor
- Home/End: Start/end of line
- Ctrl+Home/End: Start/end of file
- Ctrl+Left/Right: Move by words
- Click minimap: Jump to position

### Selection
- Shift+Arrow: Extend selection
- Ctrl+A: Select all
- Double-click: Select word
- Triple-click: Select line

### Multiple Cursors
- Ctrl+D: Add cursor at next occurrence of selected text
- If no text is selected, selects word under cursor
- Type to edit at all cursor positions
- Backspace works at all cursor positions
- Cursors are automatically updated as you edit
- Click elsewhere to clear additional cursors

### Code Folding
- Click the [+]/[-] symbols in the margin to fold/unfold
- Folding works on:
  * Scene blocks
  * Function blocks
  * Control structures (if/else, while)
- Folded code shows a summary line
- Folding state is preserved while editing

### Auto-Closing Brackets
- Opening bracket/quote automatically adds closing one:
  * { → {}
  * " → ""
  * ' → ''
- Cursor is placed between the pair
- Works with multiple cursors

### Indent Guides
- Vertical lines show indentation levels
- Makes nested blocks easier to read
- Color matches editor theme
- Updates as you type

### Error/Warning Indicators
- Red circle: Syntax error
- Yellow circle: Warning
- Hover to see details
- Click to jump to problem
- Updates as you type

### View Options
- Zoom: Use toolbar controls or Ctrl+Mouse Wheel
  * Range: 50% to 200%
  * Default: 100%
- Word Wrap: Lines wrap at window edge
- Minimap: Code overview on right side
  * Shows zoomed-out view
  * Highlights current section
  * Click to navigate
  * Real-time updates

## Language Features

### Scene Detection
The editor automatically detects and tracks scenes:
- Current scene shown in status bar
- Scene names highlighted in code
- Quick navigation between scenes (coming soon)

### Syntax Highlighting
Different colors for:
- Keywords (Deep Pink)
- Strings (Khaki)
- Scene elements (Medium Purple)
- Actions (Medium Turquoise)
- Character names (Yellow Green)
- Comments (Light Cyan)

### Auto-Indentation
- Press Enter: Maintains current indentation
- Opening brace: Increases indentation
- Closing brace: Decreases indentation

## Project Management

### Project Structure
Recommended project organization:
```
your-project/
├── scenes/
│   ├── intro.case
│   ├── chapter1.case
│   └── ending.case
├── characters/
│   └── definitions.case
├── functions/
│   └── common.case
└── main.case
```

### Working with Multiple Files
1. Use the file tree to navigate
2. Open related files in tabs
3. Drag tabs to arrange them
4. Use Quick Open (Ctrl+P) to switch files
5. Use minimap for quick navigation

### Recent Files
- Last 10 opened files remembered
- Access from File > Recent Files
- Clear list from the same menu

## Keyboard Shortcuts

### File Operations
- New File: Ctrl+N
- Open File: Ctrl+O
- Quick Open: Ctrl+P
- Save: Ctrl+S
- Save As: Ctrl+Shift+S
- Close Tab: Ctrl+W

### Editing
- Undo: Ctrl+Z
- Redo: Ctrl+Y or Ctrl+Shift+Z
- Cut: Ctrl+X
- Copy: Ctrl+C
- Paste: Ctrl+V
- Select All: Ctrl+A
- Add Cursor: Ctrl+D

### View
- Zoom In: Ctrl++
- Zoom Out: Ctrl+-
- Reset Zoom: Ctrl+0

## Tips and Tricks

### Efficient Navigation
1. Use Quick Open (Ctrl+P) for fast file switching
2. Use the file tree for project overview
3. Keep related files in tabs
4. Use minimap for quick scrolling
5. Use code folding for better overview

### Multiple Cursors
1. Select a word and press Ctrl+D
2. Keep pressing Ctrl+D to add more cursors
3. Edit at all cursor positions simultaneously
4. Great for renaming variables or making similar changes
5. Click anywhere to clear cursors

### Code Organization
1. Use code folding to focus on specific sections
2. Follow consistent indentation
3. Group related scenes in folders
4. Use meaningful scene names
5. Keep functions organized

### Auto-save
- Files save automatically every minute
- Modified files show * in tab name
- Manual save with Ctrl+S still recommended

### File Organization
1. Group related files in directories
2. Use consistent naming conventions
3. Keep main story flow in separate files

## Troubleshooting

### Common Issues

1. File won't open
   - Check file permissions
   - Verify file exists
   - Check for file lock by other programs

2. Changes not saving
   - Check disk space
   - Verify write permissions
   - Try Save As to new location

3. External file changes
   - Choose whether to reload
   - Save your changes first if needed
   - Use version control for better tracking

### Getting Help

If you encounter issues:
1. Check error messages in status bar
2. Look for syntax errors in code
3. Consult this guide
4. Report bugs through the issue tracker

## Future Features

Coming soon:
1. Git integration
2. Find and replace
3. Advanced error handling
4. Theme customization
5. Collaborative editing
