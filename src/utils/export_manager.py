"""Export and import functionality for the Casebook Editor."""

import os
import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from PyQt6.QtCore import QObject, QSettings, pyqtSignal, QThread

class ExportWorker(QObject):
    """Worker for export operations."""
    
    finished = pyqtSignal(bool, str, str)  # success, path, error
    progress = pyqtSignal(int)  # progress percentage
    
    def __init__(self, export_manager, operation, **kwargs):
        super().__init__()
        self.export_manager = export_manager
        self.operation = operation
        self.kwargs = kwargs
        
    def run(self):
        """Run the export operation."""
        try:
            if self.operation == 'project':
                result = self.export_manager._export_project_zip(self.kwargs['project_path'])
                self.finished.emit(True, result, None)
            elif self.operation == 'file':
                result = self.export_manager._export_file(
                    self.kwargs['file_path'],
                    self.kwargs['export_format'],
                    self.kwargs.get('target_path')
                )
                self.finished.emit(True, result, None)
        except Exception as e:
            self.finished.emit(False, None, str(e))

class ExportManager(QObject):
    """Manages export and import operations."""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.settings = QSettings('Codeium', 'Casebook Editor')
        self.worker = None
        self.thread = None
        
    def export_project(self, project_path):
        """Export the entire project."""
        self._cleanup_thread()
        
        # Create new thread and worker
        self.thread = QThread()
        self.worker = ExportWorker(self, 'project', project_path=project_path)
        self.worker.moveToThread(self.thread)
        
        # Connect signals
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self._update_progress)
        
        # Start thread
        self.thread.start()
        
    def export_file(self, file_path, export_format, target_path=None):
        """Export a single file in the specified format."""
        self._cleanup_thread()
        
        # Create new thread and worker
        self.thread = QThread()
        self.worker = ExportWorker(
            self, 'file',
            file_path=file_path,
            export_format=export_format,
            target_path=target_path
        )
        self.worker.moveToThread(self.thread)
        
        # Connect signals
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self._update_progress)
        
        # Start thread
        self.thread.start()
        
    def _cleanup_thread(self):
        """Clean up any existing thread."""
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
        self.worker = None
        self.thread = None
        
    def _update_progress(self, value):
        """Update progress dialog."""
        if hasattr(self.main_window, 'progress_dialog'):
            try:
                self.main_window.progress_dialog.setValue(value)
            except:
                pass
                
    def _export_project_zip(self, project_path):
        """Export project as a ZIP file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        project_name = os.path.basename(project_path)
        zip_name = f"{project_name}_backup_{timestamp}.zip"
        zip_path = os.path.join(os.path.dirname(project_path), zip_name)
        
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                total_files = sum([len(files) for _, _, files in os.walk(project_path)])
                processed_files = 0
                
                for root, _, files in os.walk(project_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_path = os.path.relpath(file_path, project_path)
                        zipf.write(file_path, arc_path)
                        processed_files += 1
                        progress = int((processed_files / total_files) * 100)
                        if hasattr(self, 'worker'):
                            self.worker.progress.emit(progress)
                        
            return zip_path
        except Exception as e:
            if os.path.exists(zip_path):
                try:
                    os.remove(zip_path)
                except:
                    pass
            raise Exception(f"Failed to create project backup: {str(e)}")
            
    def _export_file(self, file_path, export_format, target_path=None):
        """Export a single file in the specified format."""
        supported_formats = {
            'txt': self._export_as_text,
            'html': self._export_as_html,
            'md': self._export_as_markdown,
            'pdf': self._export_as_pdf
        }
        
        if export_format not in supported_formats:
            raise ValueError(f"Unsupported export format: {export_format}")
            
        if not target_path:
            target_path = f"{os.path.splitext(file_path)[0]}.{export_format}"
            
        try:
            if hasattr(self, 'worker'):
                self.worker.progress.emit(0)
                
            result = supported_formats[export_format](file_path, target_path)
            
            if hasattr(self, 'worker'):
                self.worker.progress.emit(100)
                
            return result
            
        except Exception as e:
            if os.path.exists(target_path):
                try:
                    os.remove(target_path)
                except:
                    pass
            raise e
            
    def _export_as_text(self, file_path, target_path):
        """Export file as plain text."""
        editor = self.main_window.editor_tabs.get_editor_for_file(file_path)
        if not editor:
            raise Exception("File not open in editor")
            
        content = editor.text()
        
        try:
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return target_path
        except Exception as e:
            raise Exception(f"Failed to export as text: {str(e)}")
            
    def _export_as_html(self, file_path, target_path):
        """Export file as HTML."""
        editor = self.main_window.editor_tabs.get_editor_for_file(file_path)
        if not editor:
            raise Exception("File not open in editor")
            
        content = editor.text()
        
        # Simple HTML conversion - can be enhanced with proper syntax highlighting
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{os.path.basename(file_path)}</title>
    <style>
        body {{ font-family: monospace; background: #272822; color: #F8F8F2; }}
        pre {{ padding: 20px; }}
    </style>
</head>
<body>
    <pre>{content}</pre>
</body>
</html>"""
        
        try:
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return target_path
        except Exception as e:
            raise Exception(f"Failed to export as HTML: {str(e)}")
            
    def _export_as_markdown(self, file_path, target_path):
        """Export file as Markdown."""
        editor = self.main_window.editor_tabs.get_editor_for_file(file_path)
        if not editor:
            raise Exception("File not open in editor")
            
        content = editor.text()
        
        try:
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return target_path
        except Exception as e:
            raise Exception(f"Failed to export as Markdown: {str(e)}")
            
    def _export_as_pdf(self, file_path, target_path):
        """Export file as PDF."""
        # TODO: Implement PDF export using a library like reportlab or Qt's PDF capabilities
        raise NotImplementedError("PDF export not yet implemented")

    def import_project(self, zip_path, target_dir):
        """Import a project from a backup."""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(target_dir)
            return target_dir
        except Exception as e:
            raise Exception(f"Failed to import project: {str(e)}")

    def export_settings(self, file_path):
        """Export application settings."""
        settings_data = {}
        
        # Export all settings
        self.settings.sync()
        for key in self.settings.allKeys():
            settings_data[key] = self.settings.value(key)
            
        try:
            with open(file_path, 'w') as f:
                json.dump(settings_data, f, indent=4)
            return True
        except Exception as e:
            raise Exception(f"Failed to export settings: {str(e)}")

    def import_settings(self, file_path):
        """Import application settings."""
        try:
            with open(file_path, 'r') as f:
                settings_data = json.load(f)
                
            # Clear existing settings
            self.settings.clear()
            
            # Import new settings
            for key, value in settings_data.items():
                self.settings.setValue(key, value)
                
            self.settings.sync()
            return True
        except Exception as e:
            raise Exception(f"Failed to import settings: {str(e)}")
