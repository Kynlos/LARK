# Casebook Editor Styling Guide

This guide explains how to customize the appearance of the Casebook Language Editor.

## Default Color Scheme

The editor uses a dark theme by default with the following colors:

| Element | Color | RGB | Description |
|---------|-------|-----|-------------|
| Keywords | Deep Pink | (249, 38, 114) | Language keywords like SCENE, IF, THEN |
| Strings | Khaki | (230, 219, 116) | Text in quotes |
| Scene Elements | Medium Purple | (174, 129, 255) | Scene names and section types |
| Actions | Medium Turquoise | (81, 217, 205) | Function calls and actions |
| Characters | Yellow Green | (166, 226, 46) | Character names in dialogue |
| Comments | Light Cyan | (213, 248, 232) | Single and multi-line comments |
| Background | Dark Slate Grey | (39, 40, 34) | Editor background |
| Default Text | Off White | (248, 248, 242) | Regular text |

## Customizing Colors

To change the editor's color scheme, modify the `create_styles()` method in `src/editor/lexer.py`:

```python
def create_styles(self):
    """Create and define the editor styles."""
    # Define your custom colors here
    keyword_color = QColor(249, 38, 114)    # Change RGB values
    string_color = QColor(230, 219, 116)    # for each style
    scene_color = QColor(174, 129, 255)
    action_color = QColor(81, 217, 205)
    character_color = QColor(166, 226, 46)
    comment_color = QColor(213, 248, 232)
    background_color = QColor(39, 40, 34)
    default_color = QColor(248, 248, 242)
```

### Color Style Categories

1. Style 0 - Default Text
   - Used for: Regular text, identifiers, numbers
   - Default: Off White (248, 248, 242)

2. Style 1 - Keywords
   - Used for: Language keywords, operators, punctuation
   - Default: Deep Pink (249, 38, 114)

3. Style 2 - Strings
   - Used for: All string literals
   - Default: Khaki (230, 219, 116)

4. Style 3 - Scene Elements
   - Used for: Scene names, section types, IDs
   - Default: Medium Purple (174, 129, 255)

5. Style 4 - Actions
   - Used for: Function calls, action blocks
   - Default: Medium Turquoise (81, 217, 205)

6. Style 5 - Characters
   - Used for: Character names in dialogue
   - Default: Yellow Green (166, 226, 46)

7. Style 6 - Comments
   - Used for: Single and multi-line comments
   - Default: Light Cyan (213, 248, 232)

## Creating Custom Themes

To create a new theme, follow these steps:

1. Create a new color scheme:
```python
# Light theme example
keyword_color = QColor(170, 13, 145)      # Dark pink
string_color = QColor(196, 160, 0)        # Dark yellow
scene_color = QColor(107, 36, 178)        # Dark purple
action_color = QColor(0, 139, 139)        # Dark cyan
character_color = QColor(0, 128, 0)       # Dark green
comment_color = QColor(96, 139, 78)       # Dark cyan
background_color = QColor(255, 255, 255)  # White
default_color = QColor(0, 0, 0)           # Black
```

2. Apply the colors to styles:
```python
# Define styles
self.styles = {
    0: ('default', default_color),
    1: ('keyword', keyword_color),
    2: ('string', string_color),
    3: ('scene', scene_color),
    4: ('action', action_color),
    5: ('character', character_color),
    6: ('comment', comment_color),
}

# Apply styles
for style_num, (name, color) in self.styles.items():
    self.setColor(color, style_num)
    self.setPaper(background_color, style_num)
    self.setFont(self.parent().font(), style_num)
```

## Font Customization

To change the editor font:

1. In the editor widget (`src/editor/editor.py`):
```python
def setup_editor(self):
    # Set font family and size
    font = QFont("Consolas", 12)  # Change family and size
    self.setFont(font)
```

2. Font properties you can modify:
```python
font.setFamily("Your Font")     # Font family
font.setPointSize(12)           # Font size
font.setBold(True)              # Bold
font.setItalic(True)           # Italic
font.setWeight(75)             # Weight (0-99)
```

## Example Themes

### Solarized Dark
```python
# Colors from Solarized Dark theme
base03 = QColor(0, 43, 54)        # Background
base0 = QColor(131, 148, 150)     # Body text
yellow = QColor(181, 137, 0)      # Keywords
orange = QColor(203, 75, 22)      # Strings
red = QColor(220, 50, 47)         # Scene elements
magenta = QColor(211, 54, 130)    # Actions
violet = QColor(108, 113, 196)    # Characters
blue = QColor(38, 139, 210)       # Comments
```

### Light Theme
```python
# Professional light theme
background = QColor(255, 255, 255) # White
text = QColor(0, 0, 0)            # Black
keyword = QColor(170, 13, 145)     # Dark pink
string = QColor(196, 160, 0)       # Dark yellow
scene = QColor(107, 36, 178)       # Dark purple
action = QColor(0, 139, 139)       # Dark cyan
character = QColor(0, 128, 0)      # Dark green
comment = QColor(96, 139, 78)      # Dark cyan
```

## Best Practices

1. **Color Contrast**
   - Ensure good contrast between text and background
   - Test colors with color contrast analyzers
   - Consider color-blind users

2. **Consistency**
   - Keep similar elements in the same color family
   - Use consistent brightness levels
   - Maintain visual hierarchy

3. **Readability**
   - Choose clear, readable fonts
   - Use appropriate font sizes
   - Maintain sufficient line spacing

4. **Theme Design**
   - Consider the overall visual harmony
   - Test themes with different code samples
   - Get feedback from users

## Testing Colors

After making changes:
1. Restart the editor
2. Test with various code samples
3. Check readability in different lighting
4. Verify all syntax elements are distinct
5. Test with longer editing sessions
