"""
SuperSupText - Session Manager
Handles autosave and session recovery for unsaved files (like Sublime Text)
"""

import os
import json
import uuid
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QTimer, QStandardPaths


class SessionManager:
    """
    Manages session persistence including unsaved buffers.
    
    Saves all open tabs (including unsaved ones) so they can be restored
    when the application is reopened.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._session_dir = self._get_session_dir()
        self._buffers_dir = os.path.join(self._session_dir, 'buffers')
        self._session_file = os.path.join(self._session_dir, 'session.json')
        
        # Ensure directories exist
        os.makedirs(self._buffers_dir, exist_ok=True)
        
        # Autosave timer (every 30 seconds)
        self._autosave_timer = QTimer()
        self._autosave_timer.timeout.connect(self._autosave)
        self._autosave_interval = 30000  # 30 seconds
        
        # Current session data
        self._tabs = []
        self._tab_widget = None
    
    def _get_session_dir(self) -> str:
        """Get the session directory path."""
        # Use AppData/Local on Windows
        app_data = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation)
        session_dir = os.path.join(app_data, 'SuperSupText', 'session')
        return session_dir
    
    def set_tab_widget(self, tab_widget):
        """Set the tab widget to monitor."""
        self._tab_widget = tab_widget
    
    def start_autosave(self):
        """Start the autosave timer."""
        self._autosave_timer.start(self._autosave_interval)
    
    def stop_autosave(self):
        """Stop the autosave timer."""
        self._autosave_timer.stop()
    
    def _autosave(self):
        """Perform autosave of all tabs."""
        self.save_session()
    
    def save_session(self):
        """Save the current session including all unsaved buffers."""
        if not self._tab_widget:
            return
        
        session_data = {
            'timestamp': datetime.now().isoformat(),
            'tabs': [],
            'current_tab': self._tab_widget.currentIndex(),
        }
        
        for i in range(self._tab_widget.count()):
            editor = self._tab_widget.editorAt(i)
            if not editor:
                continue
            
            tab_data = {
                'index': i,
                'filepath': editor.filepath,
                'language': editor.language,
                'encoding': editor.encoding,
                'modified': editor.isModified(),
                'cursor_line': 1,
                'cursor_column': 1,
            }
            
            # Get cursor position
            try:
                line, col = editor.getCursorPosition()
                tab_data['cursor_line'] = line
                tab_data['cursor_column'] = col
            except:
                pass
            
            # If file has no path or is modified, save the buffer content
            if not editor.filepath or editor.isModified():
                buffer_id = self._get_buffer_id(editor)
                buffer_file = os.path.join(self._buffers_dir, f'{buffer_id}.txt')
                
                try:
                    content = editor.text()
                    with open(buffer_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    tab_data['buffer_id'] = buffer_id
                except Exception as e:
                    print(f"Error saving buffer: {e}")
            
            # Save tab title for untitled files
            if not editor.filepath:
                tab_data['title'] = self._tab_widget.tabText(i).rstrip('*')
            
            session_data['tabs'].append(tab_data)
        
        # Write session file
        try:
            with open(self._session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2)
        except Exception as e:
            print(f"Error saving session: {e}")
    
    def _get_buffer_id(self, editor) -> str:
        """Get or create a unique buffer ID for an editor."""
        if not hasattr(editor, '_buffer_id') or not editor._buffer_id:
            editor._buffer_id = str(uuid.uuid4())[:8]
        return editor._buffer_id
    
    def load_session(self) -> tuple:
        """
        Load the previous session.
        
        Returns:
            Tuple of (tabs list, current_tab index)
        """
        if not os.path.exists(self._session_file):
            return [], 0
        
        try:
            with open(self._session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            return session_data.get('tabs', []), session_data.get('current_tab', 0)
        except Exception as e:
            print(f"Error loading session: {e}")
            return [], 0
    
    def get_buffer_content(self, buffer_id: str) -> str:
        """Get the content of a saved buffer."""
        buffer_file = os.path.join(self._buffers_dir, f'{buffer_id}.txt')
        
        if os.path.exists(buffer_file):
            try:
                with open(buffer_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                print(f"Error reading buffer: {e}")
        
        return ""
    
    def cleanup_old_buffers(self, keep_ids: list):
        """Remove buffer files that are no longer needed."""
        if not os.path.exists(self._buffers_dir):
            return
        
        for filename in os.listdir(self._buffers_dir):
            buffer_id = filename.replace('.txt', '')
            if buffer_id not in keep_ids:
                try:
                    os.remove(os.path.join(self._buffers_dir, filename))
                except:
                    pass
    
    def clear_session(self):
        """Clear all session data."""
        # Remove session file
        if os.path.exists(self._session_file):
            try:
                os.remove(self._session_file)
            except:
                pass
        
        # Remove all buffer files
        if os.path.exists(self._buffers_dir):
            for filename in os.listdir(self._buffers_dir):
                try:
                    os.remove(os.path.join(self._buffers_dir, filename))
                except:
                    pass
