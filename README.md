# Casebook Editor

A sophisticated desktop GUI editor for the Casebook interactive narrative language, built with Python, Qt6, and Lark.

![image](https://github.com/user-attachments/assets/e573fbf6-9189-44e6-8060-eb5fb7a6a1f7)


## Features

### File Management
- File tree sidebar for project navigation
- Tabs for multiple open files
- Recent files menu (up to 10 files)
- Quick file opener (Ctrl+P)
- Auto-save functionality
- File change detection and reload

### Editor Features
- Intelligent syntax highlighting:
  * Keywords in Deep Pink
  * Strings in Khaki
  * Scene elements in Medium Purple
  * Actions in Medium Turquoise
  * Character names in Yellow Green
  * Comments in Light Cyan
- Modern code editing features:
  * Undo/redo
  * Cut/copy/paste
  * Multiple cursors (Ctrl+D)
  * Code folding
  * Indent guides
  * Auto-closing brackets/quotes
  * Bracket matching
  * Error/warning indicators
- Line numbers and auto-indentation
- Word wrapping
- Zoom controls (50-200%)
- Scene detection
- Cross-platform compatibility
- Minimap code overview
  * Zoomed-out view of code
  * Current viewport indicator
  * Click-to-scroll navigation
  * Live updates

### Project Management
- Project file tree
- File operations:
  * Create new files
  * Open existing files
  * Save/Save As
  * Rename files
  * Delete files
- Tab management:
  * Multiple open files
  * Drag and drop tabs
  * Close tabs
  * Save all

## Installation

1. Requirements:
   - Python 3.12 or higher
   - PyQt6
   - QScintilla
   - Lark Parser

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Editor

```bash
python main.py
```

## Project Structure

```
LARK/
├── src/
│   ├── editor/
│   │   ├── editor.py        # Editor widget implementation
│   │   └── lexer.py         # Syntax highlighting and token styling
│   └── grammar/
│       ├── base_grammar.py  # Core language grammar and token definitions
│       └── grammar_manager.py # Grammar handling and parser configuration
│   └── gui/
│       ├── enhanced_window.py # Main application window
│       ├── editor_tabs.py    # Tabbed editor management
│       ├── file_tree.py      # Project file navigation
│       ├── file_watcher.py   # File system monitoring
│       ├── minimap.py        # Code overview widget
│       └── quick_open.py     # Quick file search dialog
├── main.py                  # Application entry point
├── README.md               # This file
├── USER_GUIDE.md          # Comprehensive user guide
├── STYLING.md            # Theme customization guide
└── requirements.txt       # Project dependencies
```

## Grammar System

The Casebook editor uses a sophisticated grammar system that supports:

### Base Grammar Features

- Scene definitions with nested content blocks
- Function declarations and calls
- Variable declarations and assignments
- Control structures (if/else, while, for)
- Character dialogue system
- Action descriptions
- Game configuration
- Comments (single-line and block)
- String literals (single, double, and triple-quoted)

### Token Categories

1. Keywords
   - Scene and function definitions
   - Control flow statements
   - Variable declarations
   - Boolean constants

2. String Literals
   - Double-quoted strings
   - Single-quoted strings
   - Triple-quoted strings
   - Unicode strings

3. Scene Elements
   - Scene names
   - Section types
   - Configuration blocks

4. Actions
   - Configure functions
   - Check functions
   - Do statements

5. Characters
   - Character names (uppercase)
   - Dialogue blocks

### Extending the Grammar

To extend the Casebook grammar with custom features:

1. Create a file named `casebook.override.lark` in the project root
2. Add your custom rules using Lark grammar syntax
3. Restart the editor to apply the changes

Example override file:
```lark
// Add a new statement type
?statement: base_statement    // Include base statements
         | special_action     // Add custom statement

// Define the new statement
special_action: "SPECIAL" STRING "WITH" expression

// Add custom operator
?operator: base_operator | "CUSTOM_OP"

// Add new token type
SPECIAL_TOKEN: /[A-Z]+_[0-9]+/
```

## Development

The editor is built with:
- PyQt6 for the GUI framework
- QScintilla for the code editing widget
- Lark for parsing and lexical analysis

### Key Components

1. Editor (`src/editor/editor.py`)
   - Code editing functionality
   - Syntax highlighting
   - Scene detection
   - Multiple cursors
   - Code folding
   - Auto-closing brackets
   - Error/warning indicators

2. Grammar (`src/grammar/base_grammar.py`)
   - Token definitions
   - Grammar rules
   - Parsing configurations

3. GUI (`src/gui/`)
   - Main window management
   - File tree navigation
   - Tab management
   - File watching
   - Quick file opening
   - Code overview minimap

### Modifying the Editor

1. To modify syntax highlighting:
   - Update token styles in `src/editor/lexer.py`
   - Modify token recognition patterns
   - Adjust style colors and categories

2. To modify grammar:
   - Update token definitions in `src/grammar/base_grammar.py`
   - Add or modify grammar rules
   - Configure parser options in `src/grammar/grammar_manager.py`

## Documentation

- `README.md` - Project overview and development guide
- `USER_GUIDE.md` - Comprehensive user documentation
- `STYLING.md` - Theme customization guide
- Inline code comments - Technical documentation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

