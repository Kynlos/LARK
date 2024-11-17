"""Search and replace functionality manager."""

import re
from PyQt6.QtWidgets import QListWidgetItem
from PyQt6.QtCore import QObject, Qt

class SearchManager(QObject):
    """Manages search and replace operations."""
    
    def __init__(self, editor_tabs):
        super().__init__()
        self.editor_tabs = editor_tabs
        
    def search(self, params, dialog):
        """Perform search operation."""
        text = params['text']
        case_sensitive = params['case_sensitive']
        whole_word = params['whole_word']
        use_regex = params['regex']
        multi_file = params['multi_file']
        
        # Clear previous results
        dialog.results_list.clear()
        dialog.preview.clear()
        
        if multi_file:
            self.search_all_files(text, case_sensitive, whole_word, use_regex, dialog)
        else:
            self.search_current_file(text, case_sensitive, whole_word, use_regex, dialog)
            
    def search_current_file(self, text, case_sensitive, whole_word, use_regex, dialog):
        """Search in current file."""
        editor = self.get_current_editor()
        if not editor:
            return
            
        content = editor.text()
        line_count = editor.lines()
        
        matches = self.find_matches(content, text, case_sensitive, whole_word, use_regex)
        
        for match in matches:
            start_pos, end_pos = match.span()
            line_start = content.count('\n', 0, start_pos)
            line_text = content.split('\n')[line_start]
            
            # Create result item
            item = QListWidgetItem(f"Line {line_start + 1}: {line_text.strip()}")
            item.setData(Qt.ItemDataRole.UserRole, self.get_context(content, start_pos, end_pos))
            dialog.results_list.addItem(item)
            
    def search_all_files(self, text, case_sensitive, whole_word, use_regex, dialog):
        """Search in all open files."""
        for filepath, editor in self.editor_tabs.open_files.items():
            content = editor.text()
            matches = self.find_matches(content, text, case_sensitive, whole_word, use_regex)
            
            for match in matches:
                start_pos, end_pos = match.span()
                line_start = content.count('\n', 0, start_pos)
                line_text = content.split('\n')[line_start]
                
                # Create result item with file name
                filename = filepath.split('/')[-1]
                item = QListWidgetItem(f"{filename} - Line {line_start + 1}: {line_text.strip()}")
                item.setData(Qt.ItemDataRole.UserRole, self.get_context(content, start_pos, end_pos))
                dialog.results_list.addItem(item)
                
    def preview_replace(self, params, dialog):
        """Preview replace operation."""
        search_text = params['search_text']
        replace_text = params['replace_text']
        case_sensitive = params['case_sensitive']
        whole_word = params['whole_word']
        use_regex = params['regex']
        multi_file = params['multi_file']
        
        # Clear previous results
        dialog.replace_results_list.clear()
        dialog.replace_preview.clear()
        
        if multi_file:
            self.preview_replace_all_files(search_text, replace_text, case_sensitive, whole_word, use_regex, dialog)
        else:
            self.preview_replace_current_file(search_text, replace_text, case_sensitive, whole_word, use_regex, dialog)
            
    def preview_replace_current_file(self, search_text, replace_text, case_sensitive, whole_word, use_regex, dialog):
        """Preview replace in current file."""
        editor = self.get_current_editor()
        if not editor:
            return
            
        content = editor.text()
        modified_content = self.perform_replace(content, search_text, replace_text, case_sensitive, whole_word, use_regex)
        
        # Show diff in preview
        item = QListWidgetItem("Current File")
        item.setData(Qt.ItemDataRole.UserRole, self.create_diff(content, modified_content))
        dialog.replace_results_list.addItem(item)
        
    def preview_replace_all_files(self, search_text, replace_text, case_sensitive, whole_word, use_regex, dialog):
        """Preview replace in all files."""
        for filepath, editor in self.editor_tabs.open_files.items():
            content = editor.text()
            modified_content = self.perform_replace(content, search_text, replace_text, case_sensitive, whole_word, use_regex)
            
            if content != modified_content:
                filename = filepath.split('/')[-1]
                item = QListWidgetItem(filename)
                item.setData(Qt.ItemDataRole.UserRole, self.create_diff(content, modified_content))
                dialog.replace_results_list.addItem(item)
                
    def perform_replace(self, content, search_text, replace_text, case_sensitive, whole_word, use_regex):
        """Perform replace operation on content."""
        if use_regex:
            flags = 0 if case_sensitive else re.IGNORECASE
            pattern = search_text
            if whole_word:
                pattern = fr'\b{pattern}\b'
            return re.sub(pattern, replace_text, content, flags=flags)
        else:
            if whole_word:
                words = content.split()
                for i, word in enumerate(words):
                    if (word == search_text) if case_sensitive else (word.lower() == search_text.lower()):
                        words[i] = replace_text
                return ' '.join(words)
            else:
                if case_sensitive:
                    return content.replace(search_text, replace_text)
                else:
                    return re.sub(re.escape(search_text), replace_text, content, flags=re.IGNORECASE)
                    
    def replace_in_editor(self, editor, params):
        """Perform replace operation in editor."""
        search_text = params['search_text']
        replace_text = params['replace_text']
        case_sensitive = params['case_sensitive']
        whole_word = params['whole_word']
        use_regex = params['regex']
        
        content = editor.text()
        modified_content = self.perform_replace(content, search_text, replace_text, case_sensitive, whole_word, use_regex)
        
        if content != modified_content:
            editor.setText(modified_content)
            return True
        return False
        
    def replace_current(self, params):
        """Replace in current file."""
        editor = self.get_current_editor()
        if editor:
            return self.replace_in_editor(editor, params)
        return False
        
    def replace_all(self, params):
        """Replace in all files if multi-file is enabled, otherwise just current file."""
        if params['multi_file']:
            count = 0
            for editor in self.editor_tabs.open_files.values():
                if self.replace_in_editor(editor, params):
                    count += 1
            return count
        else:
            return 1 if self.replace_current(params) else 0
            
    def find_matches(self, content, text, case_sensitive, whole_word, use_regex):
        """Find all matches in content."""
        if use_regex:
            flags = 0 if case_sensitive else re.IGNORECASE
            pattern = text
            if whole_word:
                pattern = fr'\b{pattern}\b'
            return list(re.finditer(pattern, content, flags=flags))
        else:
            if whole_word:
                pattern = fr'\b{re.escape(text)}\b'
            else:
                pattern = re.escape(text)
            flags = 0 if case_sensitive else re.IGNORECASE
            return list(re.finditer(pattern, content, flags=flags))
            
    def get_context(self, content, start_pos, end_pos):
        """Get context around match."""
        lines = content.split('\n')
        start_line = content.count('\n', 0, start_pos)
        end_line = content.count('\n', 0, end_pos)
        
        # Get 3 lines before and after
        context_start = max(0, start_line - 3)
        context_end = min(len(lines), end_line + 4)
        
        context_lines = []
        for i in range(context_start, context_end):
            prefix = '> ' if i == start_line else '  '
            context_lines.append(f"{prefix}{lines[i]}")
            
        return '\n'.join(context_lines)
        
    def create_diff(self, original, modified):
        """Create a simple diff view."""
        original_lines = original.split('\n')
        modified_lines = modified.split('\n')
        
        diff_lines = []
        for i, (orig, mod) in enumerate(zip(original_lines, modified_lines)):
            if orig != mod:
                diff_lines.append(f"Line {i + 1}:")
                diff_lines.append(f"- {orig}")
                diff_lines.append(f"+ {mod}")
                diff_lines.append("")
                
        return '\n'.join(diff_lines) if diff_lines else "No changes"
        
    def get_current_editor(self):
        """Get current editor widget."""
        container = self.editor_tabs.currentWidget()
        return container.editor if container else None
