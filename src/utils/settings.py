"""
SuperSupText - Settings Manager
Handles application settings persistence using QSettings
"""

from PySide6.QtCore import QSettings, QSize, QPoint
from PySide6.QtGui import QFont
import json
import os


class Settings:
    """Centralized settings manager for the application."""
    
    # Default values
    DEFAULTS = {
        'editor/font_family': 'Consolas',
        'editor/font_size': 12,
        'editor/tab_size': 4,
        'editor/use_spaces': True,
        'editor/show_line_numbers': True,
        'editor/show_minimap': True,
        'editor/word_wrap': False,
        'editor/auto_indent': True,
        'editor/highlight_current_line': True,
        'editor/show_whitespace': False,
        
        'window/geometry': None,
        'window/state': None,
        'window/sidebar_visible': True,
        'window/sidebar_width': 250,
        
        'theme/name': 'dark',
        
        'files/recent': [],
        'files/recent_max': 10,
        'files/last_directory': '',
        'files/session': [],
    }
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._settings = QSettings('SuperSupText', 'SuperSupText')
        return cls._instance
    
    def get(self, key, default=None):
        """Get a setting value."""
        if default is None:
            default = self.DEFAULTS.get(key)
        value = self._settings.value(key, default)
        
        # Handle type conversion for boolean values
        if isinstance(default, bool):
            if isinstance(value, str):
                return value.lower() == 'true'
            return bool(value)
        
        # Handle type conversion for integer values
        if isinstance(default, int) and not isinstance(default, bool):
            try:
                return int(value)
            except (ValueError, TypeError):
                return default
        
        return value
    
    def set(self, key, value):
        """Set a setting value."""
        self._settings.setValue(key, value)
    
    def get_font(self):
        """Get the editor font."""
        font = QFont(
            self.get('editor/font_family'),
            self.get('editor/font_size')
        )
        font.setFixedPitch(True)
        return font
    
    def set_font(self, font):
        """Set the editor font."""
        self.set('editor/font_family', font.family())
        self.set('editor/font_size', font.pointSize())
    
    def add_recent_file(self, filepath):
        """Add a file to recent files list."""
        recent = self.get('files/recent', [])
        if not isinstance(recent, list):
            recent = []
        
        # Remove if already exists
        if filepath in recent:
            recent.remove(filepath)
        
        # Add to beginning
        recent.insert(0, filepath)
        
        # Limit size
        max_recent = self.get('files/recent_max', 10)
        recent = recent[:max_recent]
        
        self.set('files/recent', recent)
    
    def get_recent_files(self):
        """Get list of recent files."""
        recent = self.get('files/recent', [])
        if not isinstance(recent, list):
            return []
        # Filter out files that no longer exist
        return [f for f in recent if os.path.exists(f)]
    
    def clear_recent_files(self):
        """Clear recent files list."""
        self.set('files/recent', [])
    
    def save_session(self, files):
        """Save current session (open files)."""
        self.set('files/session', files)
    
    def get_session(self):
        """Get saved session files."""
        session = self.get('files/session', [])
        if not isinstance(session, list):
            return []
        return session
    
    def sync(self):
        """Force sync settings to disk."""
        self._settings.sync()
