"""Casebook editor widget implementation."""

import os
from PyQt6.QtWidgets import QScrollBar
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QTextCursor, QPainter
from PyQt6.Qsci import (
    QsciScintilla, QsciLexerCustom, QsciAPIs,
    QsciStyle, QsciLexerPython, QsciLexerCPP,
    QsciLexerHTML, QsciLexerCSS, QsciLexerJavaScript,
    QsciLexerXML, QsciLexerYAML, QsciLexerJSON,
    QsciLexerMarkdown, QsciLexerSQL, QsciLexerBash,
    QsciLexerDiff, QsciLexerProperties
)
from .lexer import CasebookLexer

class CasebookEditor(QsciScintilla):
    """Casebook editor widget."""
    
    # Custom signals
    sceneChanged = pyqtSignal(str)
    
    def __init__(self, parent=None, grammar_manager=None):
        super().__init__(parent)
        self.grammar_manager = grammar_manager
        self.base_font_size = 10
        self.additional_cursors = []  # Store additional cursor positions
        self.setup_editor()
        self.setup_margins()
        self.setup_folding()
        self.current_scene = None
        self.cursorPositionChanged.connect(self.check_current_scene)
        self.selectionChanged.connect(self.update_additional_cursors)
        
    def get_lexer_for_file(self, filepath):
        """Get the appropriate lexer based on file extension."""
        if not filepath:
            return None
            
        ext = os.path.splitext(filepath)[1].lower()
        lexer_map = {
            '.case': lambda: CasebookLexer(self, self.grammar_manager),
            '.py': QsciLexerPython,
            '.cpp': QsciLexerCPP,
            '.h': QsciLexerCPP,
            '.hpp': QsciLexerCPP,
            '.c': QsciLexerCPP,
            '.html': QsciLexerHTML,
            '.htm': QsciLexerHTML,
            '.css': QsciLexerCSS,
            '.js': QsciLexerJavaScript,
            '.xml': QsciLexerXML,
            '.yaml': QsciLexerYAML,
            '.yml': QsciLexerYAML,
            '.json': QsciLexerJSON,
            '.md': QsciLexerMarkdown,
            '.sql': QsciLexerSQL,
            '.sh': QsciLexerBash,
            '.bash': QsciLexerBash,
            '.diff': QsciLexerDiff,
            '.patch': QsciLexerDiff,
            '.properties': QsciLexerProperties,
            '.ini': QsciLexerProperties,
            '.conf': QsciLexerProperties,
        }
        
        lexer_class = lexer_map.get(ext)
        if lexer_class:
            if callable(lexer_class):
                lexer = lexer_class()
            else:
                lexer = lexer_class(self)
                
            # Set lexer font
            font = self.font()
            lexer.setFont(font)
            
            # Apply dark theme colors
            if ext != '.case':  # Don't override Casebook lexer colors
                self.apply_dark_theme_to_lexer(lexer)
                
            return lexer
            
        return None
        
    def apply_dark_theme_to_lexer(self, lexer):
        """Apply dark theme colors to a lexer."""
        # Define colors
        background = QColor(39, 40, 34)      # Dark background
        foreground = QColor(248, 248, 242)   # Light foreground
        keyword = QColor(249, 38, 114)       # Pink
        string = QColor(230, 219, 116)       # Yellow
        comment = QColor(98, 114, 164)       # Grayish blue
        number = QColor(174, 129, 255)       # Purple
        operator = QColor(249, 38, 114)      # Pink
        identifier = QColor(248, 248, 242)   # White
        function = QColor(166, 226, 46)      # Green
        class_name = QColor(102, 217, 239)   # Light blue
        list_marker = QColor(253, 151, 31)   # Orange
        code_block_bg = QColor(44, 49, 58)   # Light blue tinted background
        
        # Set paper (background) for all styles
        for style in range(128):  # QScintilla uses style numbers 0-127
            lexer.setPaper(background, style)
        
        # Common style numbers across different lexers
        if isinstance(lexer, QsciLexerPython):
            lexer.setColor(foreground, QsciLexerPython.Default)
            lexer.setColor(keyword, QsciLexerPython.Keyword)
            lexer.setColor(comment, QsciLexerPython.Comment)
            lexer.setColor(string, QsciLexerPython.DoubleQuotedString)
            lexer.setColor(string, QsciLexerPython.SingleQuotedString)
            lexer.setColor(string, QsciLexerPython.TripleDoubleQuotedString)
            lexer.setColor(string, QsciLexerPython.TripleSingleQuotedString)
            lexer.setColor(number, QsciLexerPython.Number)
            lexer.setColor(operator, QsciLexerPython.Operator)
            lexer.setColor(identifier, QsciLexerPython.Identifier)
            lexer.setColor(function, QsciLexerPython.FunctionMethodName)
            lexer.setColor(class_name, QsciLexerPython.ClassName)
            
        elif isinstance(lexer, QsciLexerCPP):
            lexer.setColor(foreground, QsciLexerCPP.Default)
            lexer.setColor(keyword, QsciLexerCPP.Keyword)
            lexer.setColor(comment, QsciLexerCPP.Comment)
            lexer.setColor(string, QsciLexerCPP.DoubleQuotedString)
            lexer.setColor(string, QsciLexerCPP.SingleQuotedString)
            lexer.setColor(number, QsciLexerCPP.Number)
            lexer.setColor(operator, QsciLexerCPP.Operator)
            lexer.setColor(identifier, QsciLexerCPP.Identifier)
            lexer.setColor(function, QsciLexerCPP.GlobalFunction)
            
        elif isinstance(lexer, QsciLexerMarkdown):
            # Basic text
            lexer.setColor(foreground, 0)  # Default
            
            # Headers (styles 1-6)
            for i in range(1, 7):
                lexer.setColor(class_name, i)
                lexer.setFont(QFont("Consolas", pointSize=self.font().pointSize() + (6 - i)), i)
            
            # Set a light blue background for code blocks first
            # Try all possible code block style numbers
            code_styles = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
            for style in code_styles:
                lexer.setPaper(code_block_bg, style)
                lexer.setColor(foreground, style)
            
            # Other styles
            lexer.setColor(list_marker, 7)   # Emphasis
            lexer.setColor(function, 8)      # Bold
            lexer.setColor(string, 9)        # Link
            lexer.setColor(list_marker, 12)  # Bullet point
            lexer.setColor(list_marker, 13)  # Number
            lexer.setColor(comment, 14)      # Quote
            lexer.setColor(string, 15)       # Reference
            
            # Make sure code blocks are properly styled
            # Override any previous styling for code blocks
            code_styles = [
                21,  # Code Block
                20,  # Code
                19,  # Code2
                18,  # Code3
                17,  # PreChar
                16   # PreProc
            ]
            for style in code_styles:
                lexer.setPaper(code_block_bg, style)
                lexer.setColor(foreground, style)
            
        elif isinstance(lexer, QsciLexerHTML):
            lexer.setColor(foreground, QsciLexerHTML.Default)
            lexer.setColor(keyword, QsciLexerHTML.Tag)
            lexer.setColor(function, QsciLexerHTML.Attribute)
            lexer.setColor(string, QsciLexerHTML.DoubleQuotedString)
            lexer.setColor(string, QsciLexerHTML.SingleQuotedString)
            lexer.setColor(comment, QsciLexerHTML.Comment)
            
        elif isinstance(lexer, QsciLexerCSS):
            lexer.setColor(foreground, QsciLexerCSS.Default)
            lexer.setColor(keyword, QsciLexerCSS.Tag)
            lexer.setColor(class_name, QsciLexerCSS.ClassSelector)
            lexer.setColor(function, QsciLexerCSS.PseudoClass)
            lexer.setColor(operator, QsciLexerCSS.Operator)
            lexer.setColor(string, QsciLexerCSS.DoubleQuotedString)
            lexer.setColor(string, QsciLexerCSS.SingleQuotedString)
            lexer.setColor(comment, QsciLexerCSS.Comment)
            
        elif isinstance(lexer, QsciLexerJSON):
            lexer.setColor(foreground, QsciLexerJSON.Default)
            lexer.setColor(keyword, QsciLexerJSON.Keyword)
            lexer.setColor(string, QsciLexerJSON.String)
            lexer.setColor(number, QsciLexerJSON.Number)
            lexer.setColor(operator, QsciLexerJSON.Operator)
            
        else:
            # For any other lexer, at least set basic colors
            lexer.setDefaultColor(foreground)
            lexer.setDefaultPaper(background)
            
    def setup_lexer(self, filepath=None):
        """Set up the syntax highlighter."""
        lexer = self.get_lexer_for_file(filepath)
        if lexer:
            self.setLexer(lexer)
        else:
            # No specific lexer found, remove any existing lexer
            self.setLexer(None)
            
    def setup_editor(self):
        """Configure the editor settings."""
        # Set font defaults
        font = QFont()
        font.setFamily('Consolas')
        font.setFixedPitch(True)
        font.setPointSize(self.base_font_size)
        self.setFont(font)
        
        # Set margin defaults
        fontmetrics = QFontMetrics(font)
        self.setMarginsFont(font)
        self.setMarginWidth(0, fontmetrics.horizontalAdvance("000") + 6)
        self.setMarginLineNumbers(0, True)
        self.setMarginsForegroundColor(QColor(128, 128, 128))  # Gray line numbers
        self.setMarginsBackgroundColor(QColor(39, 40, 34))     # Dark background
        
        # Set colors
        self.setPaper(QColor(39, 40, 34))  # Background
        self.setColor(QColor(248, 248, 242))  # Default text
        
        # Set indentation defaults
        self.setIndentationsUseTabs(False)
        self.setIndentationWidth(4)
        self.setBackspaceUnindents(True)
        self.setIndentationGuides(True)
        self.setIndentationGuidesBackgroundColor(QColor(39, 40, 34))
        self.setIndentationGuidesForegroundColor(QColor(64, 64, 64))
        
        # Set caret defaults
        self.setCaretForegroundColor(QColor(247, 247, 241))
        self.setCaretWidth(2)
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor(45, 45, 45))
        
        # Set selection color defaults
        self.setSelectionBackgroundColor(QColor(61, 61, 52))
        self.resetSelectionForegroundColor()
        
        # Set scrolling behavior
        self.SendScintilla(QsciScintilla.SCI_SETSCROLLWIDTHTRACKING, 1)
        self.SendScintilla(QsciScintilla.SCI_SETSCROLLWIDTH, 1)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Set word wrapping
        self.setWrapMode(QsciScintilla.WrapMode.WrapWord)
        self.setWrapVisualFlags(QsciScintilla.WrapVisualFlag.WrapFlagNone)
        self.setWrapIndentMode(QsciScintilla.WrapIndentMode.WrapIndentFixed)
        
        # Set other defaults
        self.setBraceMatching(QsciScintilla.BraceMatch.StrictBraceMatch)
        self.setAutoIndent(True)
        
        # Set auto-closing brackets
        self.setBraceMatching(QsciScintilla.BraceMatch.StrictBraceMatch)
        self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAll)
        self.setAutoCompletionThreshold(1)
        self.setAutoCompletionCaseSensitivity(True)
        self.setAutoCompletionReplaceWord(True)
        
    def setup_margins(self):
        """Configure the editor margins."""
        # Line numbers
        self.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.setMarginWidth(0, "000")
        self.setMarginLineNumbers(0, True)
        
        # Folding markers
        self.setMarginType(2, QsciScintilla.MarginType.SymbolMargin)
        self.setMarginWidth(2, 12)
        self.setMarginSensitivity(2, True)
        self.setMarginMarkerMask(2, 0b1111)
        
        # Error/warning indicators
        self.setMarginType(1, QsciScintilla.MarginType.SymbolMargin)
        self.setMarginWidth(1, 12)
        self.setMarginSensitivity(1, True)
        
        # Define markers
        self.markerDefine(QsciScintilla.MarkerSymbol.BoxedPlus, 0)  # Folding marker closed
        self.markerDefine(QsciScintilla.MarkerSymbol.BoxedMinus, 1)  # Folding marker open
        self.markerDefine(QsciScintilla.MarkerSymbol.Circle, 2)  # Error marker
        self.markerDefine(QsciScintilla.MarkerSymbol.CircledMinus, 3)  # Warning marker
        
        # Set marker colors
        self.setMarkerBackgroundColor(QColor(64, 64, 64), 0)  # Folding closed
        self.setMarkerBackgroundColor(QColor(64, 64, 64), 1)  # Folding open
        self.setMarkerBackgroundColor(QColor(200, 50, 50), 2)  # Error
        self.setMarkerBackgroundColor(QColor(200, 150, 50), 3)  # Warning
        
    def setup_folding(self):
        """Configure code folding."""
        self.setFolding(QsciScintilla.FoldStyle.BoxedTreeFoldStyle)
        self.setFoldMarginColors(
            QColor(39, 40, 34),  # Background
            QColor(39, 40, 34)   # Foreground
        )
        
        # Connect folding signals
        self.marginClicked.connect(self.on_margin_clicked)
        
    def on_margin_clicked(self, margin, line, modifiers):
        """Handle margin clicks for folding."""
        if margin == 2:  # Folding margin
            self.foldLine(line)
            
    def set_zoom(self, value):
        """Set zoom level."""
        if not 50 <= value <= 200:
            return
            
        # Calculate new font size
        new_size = int(self.base_font_size * value / 100)
        
        # Update editor font
        font = self.font()
        font.setPointSize(new_size)
        self.setFont(font)
        
        # Update margin font
        margin_font = font  # Use the same font for margins
        self.setMarginsFont(margin_font)
        
        # Update margin width
        fontmetrics = QFontMetrics(margin_font)
        self.setMarginWidth(0, fontmetrics.horizontalAdvance("000") + 6)
        
        # Force refresh
        self.update()
        
    def isUndoAvailable(self):
        """Check if undo is available."""
        return super().isUndoAvailable()
        
    def isRedoAvailable(self):
        """Check if redo is available."""
        return super().isRedoAvailable()
        
    def hasSelectedText(self):
        """Check if text is selected."""
        return super().hasSelectedText()
        
    def keyPressEvent(self, event):
        """Handle key press events."""
        # Handle multiple cursors
        if event.key() == Qt.Key.Key_D and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.add_cursor_at_next_occurrence()
            return
            
        # Auto-closing brackets and quotes
        if event.key() in (Qt.Key.Key_BraceLeft, Qt.Key.Key_QuoteDbl, Qt.Key.Key_Apostrophe):
            closing_chars = {
                Qt.Key.Key_BraceLeft: '}',
                Qt.Key.Key_QuoteDbl: '"',
                Qt.Key.Key_Apostrophe: "'"
            }
            
            # Insert closing character and move cursor back
            line, pos = self.getCursorPosition()
            self.insert(closing_chars[event.key()])
            self.setCursorPosition(line, pos)
            
        # Handle input at all cursor positions
        if self.additional_cursors and event.key() not in (Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt):
            text = event.text()
            if text:
                # Store current position
                main_line, main_pos = self.getCursorPosition()
                
                # Insert at additional cursors
                for line, pos in reversed(self.additional_cursors):
                    self.setCursorPosition(line, pos)
                    if event.key() == Qt.Key.Key_Backspace:
                        if pos > 0:
                            self.setSelection(line, pos - 1, line, pos)
                            self.removeSelectedText()
                    else:
                        self.insert(text)
                        
                # Restore main cursor
                self.setCursorPosition(main_line, main_pos)
                if event.key() == Qt.Key.Key_Backspace:
                    if main_pos > 0:
                        self.setSelection(main_line, main_pos - 1, main_line, main_pos)
                        self.removeSelectedText()
                else:
                    self.insert(text)
                    
                # Update cursor positions
                self.update_additional_cursors()
                return
                
        super().keyPressEvent(event)
        
    def add_cursor_at_next_occurrence(self):
        """Add a cursor at the next occurrence of selected text."""
        # Get current selection or word under cursor
        if self.hasSelectedText():
            search_text = self.selectedText()
            start_line, start_pos, end_line, end_pos = self.getSelection()
        else:
            # Get current position
            pos = self.SendScintilla(QsciScintilla.SCI_GETCURRENTPOS)
            
            # Select word at current position
            start = self.SendScintilla(QsciScintilla.SCI_WORDSTARTPOSITION, pos, 1)
            end = self.SendScintilla(QsciScintilla.SCI_WORDENDPOSITION, pos, 1)
            
            # Set selection
            self.SendScintilla(QsciScintilla.SCI_SETSEL, start, end)
            
            if not self.hasSelectedText():
                return
                
            search_text = self.selectedText()
            start_line, start_pos, end_line, end_pos = self.getSelection()
            
        # Find next occurrence
        self.findFirst(
            search_text,
            False,  # Regular expression
            True,   # Case sensitive
            True,   # Whole words only
            True,   # Wrap around
            True,   # Forward search
            end_line,
            end_pos
        )
        
        if self.hasSelectedText():
            new_start_line, new_start_pos, _, _ = self.getSelection()
            self.additional_cursors.append((new_start_line, new_start_pos))
            self.update()

    def update_additional_cursors(self):
        """Update additional cursor positions after text changes."""
        # Remove invalid cursors
        self.additional_cursors = [
            (line, pos) for line, pos in self.additional_cursors
            if line < self.lines() and pos <= len(self.text(line))
        ]
        
    def paintEvent(self, event):
        """Override paint event to draw additional cursors."""
        super().paintEvent(event)
        
        if not self.additional_cursors:
            return
            
        # Draw additional cursors
        painter = QPainter(self.viewport())
        painter.setPen(self.caretForegroundColor())
        
        for line, pos in self.additional_cursors:
            x = self.SendScintilla(QsciScintilla.SCI_POINTXFROMPOSITION, 0, self.positionFromLineIndex(line, pos))
            y = self.SendScintilla(QsciScintilla.SCI_POINTYFROMPOSITION, 0, self.positionFromLineIndex(line, pos))
            height = self.textHeight(line)
            painter.drawLine(x, y, x, y + height)
            
    def clear_additional_cursors(self):
        """Clear all additional cursors."""
        self.additional_cursors = []
        self.update()
        
    def check_current_scene(self):
        """Check if cursor is in a different scene and emit signal if changed."""
        line, _ = self.getCursorPosition()
        text = self.text()
        lines = text.split('\n')
        
        current_scene = None
        for i, line_text in enumerate(lines):
            if line_text.strip().startswith('SCENE '):
                scene_name = line_text.strip().split()[1].split('{')[0].strip()
                if i <= line:
                    current_scene = scene_name
                else:
                    break
        
        if current_scene != self.current_scene:
            self.current_scene = current_scene
            self.sceneChanged.emit(current_scene)
