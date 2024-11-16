"""Grammar manager for handling base and override grammars."""

import os
from pathlib import Path
from lark import Lark, Token
from .base_grammar import BASE_GRAMMAR

class GrammarManager:
    def __init__(self):
        self.base_grammar = BASE_GRAMMAR
        self.override_grammar = ""
        self.combined_grammar = ""
        self.parser = None
        
    def load_override_grammar(self, override_path):
        """Load the override grammar if it exists."""
        if os.path.exists(override_path):
            with open(override_path, 'r') as f:
                self.override_grammar = f.read()
                return True
        return False

    def combine_grammars(self):
        """Combine base and override grammars."""
        if not self.override_grammar:
            self.combined_grammar = self.base_grammar
            return

        # Prepare the base grammar for combining
        modified_base = self.base_grammar.replace('statement:', '?base_statement:')
        
        # Combine grammars
        self.combined_grammar = f"""
            // Combined Grammar (Base + Override)
            {modified_base}

            // User Overrides
            {self.override_grammar}

            // If no start rule in override, use base start
            ?statement: base_statement
        """

    def create_parser(self):
        """Create a Lark parser from the combined grammar."""
        self.combine_grammars()
        print("\nCreating parser with options:")
        print("  parser='lalr'")
        print("  lexer='basic'")
        print("  propagate_positions=True")
        print("  keep_all_tokens=True")
        self.parser = Lark(self.combined_grammar, 
                          parser='lalr',
                          lexer='basic',
                          propagate_positions=True,
                          keep_all_tokens=True)
        return self.parser

    def get_parser(self):
        """Get the current parser instance."""
        if not self.parser:
            self.create_parser()
        return self.parser
