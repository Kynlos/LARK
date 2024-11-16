"""Custom lexer for the Casebook language."""

from PyQt6.QtGui import QColor, QFont
from PyQt6.Qsci import QsciLexerCustom

class CasebookLexer(QsciLexerCustom):
    def __init__(self, parent=None, grammar_manager=None):
        super().__init__(parent)
        self.grammar_manager = grammar_manager
        self.create_styles()

    def create_styles(self):
        """Create and define the editor styles."""
        # Define colors
        keyword_color = QColor(249, 38, 114)    # deeppink
        string_color = QColor(230, 219, 116)    # khaki
        scene_color = QColor(174, 129, 255)     # mediumpurple
        action_color = QColor(81, 217, 205)     # mediumturquoise
        character_color = QColor(166, 226, 46)  # yellowgreen
        comment_color = QColor(213, 248, 232)   # lightcyan
        background_color = QColor(39, 40, 34)   # darkslategrey
        default_color = QColor(248, 248, 242)   # off white

        # Define styles
        self.styles = {
            0: ('default', default_color),      # Default style
            1: ('keyword', keyword_color),      # Keywords (SCENE, IF, THEN, etc)
            2: ('string', string_color),        # String literals
            3: ('scene', scene_color),          # Scene declarations
            4: ('action', action_color),        # Action declarations
            5: ('character', character_color),  # Character names
            6: ('comment', comment_color),      # Comments
        }

        # Apply styles
        for style_num, (name, color) in self.styles.items():
            self.setColor(color, style_num)
            self.setPaper(background_color, style_num)
            self.setFont(self.parent().font(), style_num)

        # Map tokens to styles
        self.token_styles = {
            # Keywords and special tokens
            'SCENE': 1,
            'DO': 1,
            'LET': 1,
            'WHILE': 1,
            'RETURN': 1,
            'THEN': 1,
            'IF': 1,
            'ELIF': 1,
            'ELSE': 1,
            'FOR': 1,
            'IN': 1,
            'TRUE': 1,
            'FALSE': 1,
            'NULL': 1,
            'AND': 1,
            'OR': 1,
            'NOT': 1,
            'FUNCTION': 1,
            
            # Operators and punctuation
            'HASH': 1,
            'DOUBLE_HASH': 1,
            'DOLLAR': 1,
            'LPAREN': 1,
            'RPAREN': 1,
            'LBRACE': 1,
            'RBRACE': 1,
            'LSQB': 1,
            'RSQB': 1,
            'COLON': 1,
            'COMMA': 1,
            'EQUALS': 1,
            'PLUS': 1,
            'MINUS': 1,
            'TIMES': 1,
            'DIVIDE': 1,
            'GT': 1,
            'LT': 1,
            'GE': 1,
            'LE': 1,
            'EQ': 1,
            'NE': 1,
            'TRIPLE_LT': 1,
            'TRIPLE_GT': 1,
            
            # String literals
            'DOUBLE_QUOTE_STRING': 2,
            'SINGLE_QUOTE_STRING': 2,
            'TRIPLE_QUOTE_STRING': 2,
            'UNICODE_STRING': 2,
            
            # Scene-related
            'SECTION_TYPE': 3,
            'ID_TEXT': 3,
            
            # Actions and functions
            'FUNCTION_NAME': 4,
            'function_call': 4,
            'control_statement': 4,
            'if_statement': 4,
            'for_statement': 4,
            'while_statement': 4,
            'let_statement': 4,
            'return_statement': 4,
            'action_block': 4,
            
            # Characters
            'CHARACTER': 5,
            
            # Comments
            'COMMENT': 6,
            'BLOCK_COMMENT': 6,
            
            # Default styling
            'IDENTIFIER': 0,
            'TEXT': 0,
            'RAW_CONTENT': 0,
            'NUMBER': 0,
            'WS': 0,
            'NEWLINE': 0,
        }

    def defaultPaper(self, style):
        """Return the default background color."""
        return QColor(39, 40, 34)  # Dark background

    def language(self):
        """Return the language name."""
        return "Casebook"

    def description(self, style):
        """Return the description for a style."""
        return self.styles.get(style, ('default', None))[0]

    def styleText(self, start, end):
        """Apply syntax highlighting to the text."""
        self.startStyling(start)
        text = self.parent().text()[start:end]
        last_pos = 0

        try:
            parser = self.grammar_manager.get_parser()
            tokens = list(parser.lex(text))
            
            for token in tokens:
                # Handle whitespace before token
                ws_len = token.start_pos - last_pos
                if ws_len > 0:
                    self.setStyling(ws_len, 0)

                # Get token length and style
                token_len = len(bytearray(str(token.value), "utf-8"))
                style = self.token_styles.get(token.type, 0)

                # Apply the style
                self.setStyling(token_len, style)
                last_pos = token.start_pos + token_len

            # Style any remaining text
            if last_pos < len(text):
                self.setStyling(len(text) - last_pos, 0)

        except Exception as e:
            print(f"Lexer error: {e}")
            # If there's an error, style the rest of the text as default
            self.setStyling(end - start, 0)
