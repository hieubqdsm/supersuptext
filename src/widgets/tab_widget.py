"""
SuperSupText - Tab Widget
Manages multiple editor tabs with close buttons, reordering, and modification indicators
"""

from PySide6.QtWidgets import (
    QTabWidget, QTabBar, QWidget, QVBoxLayout, QHBoxLayout,
    QMenu, QMessageBox, QFileDialog, QSplitter
)
from PySide6.QtCore import Signal, Qt, QPoint
from PySide6.QtGui import QAction, QIcon

from ..editor.code_editor import CodeEditor
from ..editor.minimap import MiniMap
from ..utils.file_utils import FileUtils
from ..utils.settings import Settings


class TabBar(QTabBar):
    """Custom tab bar with middle-click to close and context menu."""
    
    tabCloseRequested = Signal(int)
    tabMoved = Signal(int, int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(True)
        self.setTabsClosable(True)
        self.setElideMode(Qt.TextElideMode.ElideRight)
        self.setExpanding(False)
        self.setDocumentMode(True)
    
    def mousePressEvent(self, event):
        """Handle middle-click to close tab."""
        if event.button() == Qt.MouseButton.MiddleButton:
            index = self.tabAt(event.pos())
            if index >= 0:
                self.tabCloseRequested.emit(index)
        else:
            super().mousePressEvent(event)
    
    def contextMenuEvent(self, event):
        """Show context menu on right-click."""
        index = self.tabAt(event.pos())
        if index < 0:
            return
        
        menu = QMenu(self)
        
        close_action = menu.addAction("Close")
        close_others_action = menu.addAction("Close Others")
        close_all_action = menu.addAction("Close All")
        menu.addSeparator()
        close_right_action = menu.addAction("Close to the Right")
        close_left_action = menu.addAction("Close to the Left")
        menu.addSeparator()
        copy_path_action = menu.addAction("Copy Path")
        reveal_action = menu.addAction("Reveal in Explorer")
        
        action = menu.exec_(event.globalPos())
        
        if action == close_action:
            self.tabCloseRequested.emit(index)
        elif action == close_others_action:
            self.parent()._close_other_tabs(index)
        elif action == close_all_action:
            self.parent()._close_all_tabs()
        elif action == close_right_action:
            self.parent()._close_tabs_to_right(index)
        elif action == close_left_action:
            self.parent()._close_tabs_to_left(index)
        elif action == copy_path_action:
            self.parent()._copy_path(index)
        elif action == reveal_action:
            self.parent()._reveal_in_explorer(index)


class EditorContainer(QWidget):
    """Container for editor and minimap."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = Settings()
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Editor
        self.editor = CodeEditor(self)
        layout.addWidget(self.editor)
        
        # Minimap
        self.minimap = MiniMap(self.editor, self)
        self.minimap.setVisible(self.settings.get('editor/show_minimap'))
        self.minimap.positionClicked.connect(self._on_minimap_clicked)
        layout.addWidget(self.minimap)
    
    def _on_minimap_clicked(self, line: int):
        """Handle minimap click."""
        self.editor.goToLine(line)


class TabWidget(QTabWidget):
    """
    Tab widget for managing multiple editor tabs.
    
    Features:
    - Add/close tabs
    - Tab reordering (drag & drop)
    - Unsaved changes indicator (*)
    - Middle-click to close
    - Context menu
    """
    
    # Signals
    currentFileChanged = Signal(str)  # filepath
    fileModified = Signal(str, bool)  # filepath, is_modified
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = Settings()
        self._file_tabs = {}  # filepath -> tab index
        
        # Setup custom tab bar
        self._tab_bar = TabBar(self)
        self.setTabBar(self._tab_bar)
        
        # Connect signals
        self._tab_bar.tabCloseRequested.connect(self.closeTab)
        self.currentChanged.connect(self._on_current_changed)
        
        # Style
        self._apply_style()
    
    def _apply_style(self):
        """Apply tab widget styling."""
        self.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #bbbbbb;
                padding: 8px 28px 8px 12px;
                border: none;
                border-right: 1px solid #1e1e1e;
                min-width: 80px;
                max-width: 200px;
            }
            QTabBar::tab:selected {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QTabBar::tab:hover:!selected {
                background-color: #3c3c3c;
            }
            QTabBar::close-button {
                subcontrol-position: right;
                subcontrol-origin: padding;
                margin-right: 4px;
                width: 16px;
                height: 16px;
                border-radius: 3px;
                background-color: transparent;
                border: 1px solid #666666;
            }
            QTabBar::close-button:hover {
                background-color: #c42b1c;
                border-color: #c42b1c;
            }
        """)
    
    def newTab(self, filepath: str = None) -> int:
        """
        Create a new tab.
        
        Args:
            filepath: Optional file path to open
            
        Returns:
            Index of the new tab
        """
        # Check if file is already open
        if filepath and filepath in self._file_tabs:
            self.setCurrentIndex(self._file_tabs[filepath])
            return self._file_tabs[filepath]
        
        # Create editor container
        container = EditorContainer(self)
        editor = container.editor
        
        # Set up the tab
        if filepath:
            # Open existing file
            content, encoding = FileUtils.read_file(filepath)
            if content is not None:
                editor.setText(content)
                editor.encoding = encoding
                editor.filepath = filepath
                editor.setModified(False)
                
                # Set language
                language = FileUtils.get_language_from_extension(filepath)
                editor.set_language(language)
                
                # Update recent files
                self.settings.add_recent_file(filepath)
            else:
                QMessageBox.warning(self, "Error", f"Could not open file:\n{encoding}")
                return -1
            
            # Tab title
            import os
            title = os.path.basename(filepath)
        else:
            # New untitled file
            editor.filepath = None
            title = self._get_untitled_name()
        
        # Add tab
        index = self.addTab(container, title)
        self.setCurrentIndex(index)
        
        # Track file
        if filepath:
            self._file_tabs[filepath] = index
        
        # Connect editor signals
        editor.modificationChanged.connect(
            lambda modified: self._on_modification_changed(index, modified)
        )
        editor.cursorPositionChanged_custom.connect(self._on_cursor_changed)
        editor.fileDropped.connect(self._on_file_dropped)
        
        editor.setFocus()
        return index
    
    def _get_untitled_name(self) -> str:
        """Get a unique untitled name."""
        existing = []
        for i in range(self.count()):
            text = self.tabText(i)
            if text.startswith("Untitled"):
                existing.append(text)
        
        counter = 1
        while f"Untitled-{counter}" in existing:
            counter += 1
        
        return f"Untitled-{counter}"
    
    def closeTab(self, index: int) -> bool:
        """
        Close a tab.
        
        Args:
            index: Tab index to close
            
        Returns:
            True if closed, False if cancelled
        """
        if index < 0 or index >= self.count():
            return False
        
        container = self.widget(index)
        editor = container.editor
        
        # Check for unsaved changes
        if editor.isModified():
            result = QMessageBox.question(
                self,
                "Unsaved Changes",
                f"Do you want to save changes to '{self.tabText(index).rstrip('*')}'?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )
            
            if result == QMessageBox.StandardButton.Save:
                if not self.saveTab(index):
                    return False
            elif result == QMessageBox.StandardButton.Cancel:
                return False
        
        # Remove from file tracking
        if editor.filepath and editor.filepath in self._file_tabs:
            del self._file_tabs[editor.filepath]
        
        # Remove tab
        self.removeTab(index)
        
        # Update file tracking indices
        self._update_file_indices()
        
        return True
    
    def saveTab(self, index: int = None) -> bool:
        """
        Save the tab at the given index.
        
        Args:
            index: Tab index, or None for current tab
            
        Returns:
            True if saved successfully
        """
        if index is None:
            index = self.currentIndex()
        
        if index < 0:
            return False
        
        container = self.widget(index)
        editor = container.editor
        
        if editor.filepath:
            success, message = FileUtils.write_file(
                editor.filepath, 
                editor.text(),
                editor.encoding
            )
            if success:
                editor.setModified(False)
                return True
            else:
                QMessageBox.warning(self, "Error", f"Could not save file:\n{message}")
                return False
        else:
            return self.saveTabAs(index)
    
    def saveTabAs(self, index: int = None) -> bool:
        """
        Save the tab with a new name.
        
        Args:
            index: Tab index, or None for current tab
            
        Returns:
            True if saved successfully
        """
        if index is None:
            index = self.currentIndex()
        
        if index < 0:
            return False
        
        container = self.widget(index)
        editor = container.editor
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            self.settings.get('files/last_directory') or "",
            "All Files (*.*)"
        )
        
        if not filepath:
            return False
        
        # Remove old tracking
        if editor.filepath and editor.filepath in self._file_tabs:
            del self._file_tabs[editor.filepath]
        
        # Save file
        success, message = FileUtils.write_file(filepath, editor.text())
        if success:
            editor.filepath = filepath
            editor.setModified(False)
            
            # Update tab title
            import os
            self.setTabText(index, os.path.basename(filepath))
            
            # Update tracking
            self._file_tabs[filepath] = index
            
            # Set language
            language = FileUtils.get_language_from_extension(filepath)
            editor.set_language(language)
            
            # Update settings
            self.settings.set('files/last_directory', os.path.dirname(filepath))
            self.settings.add_recent_file(filepath)
            
            return True
        else:
            QMessageBox.warning(self, "Error", f"Could not save file:\n{message}")
            return False
    
    def currentEditor(self) -> CodeEditor:
        """Get the current tab's editor."""
        container = self.currentWidget()
        if container:
            return container.editor
        return None
    
    def editorAt(self, index: int) -> CodeEditor:
        """Get the editor at the given index."""
        container = self.widget(index)
        if container:
            return container.editor
        return None
    
    def _on_current_changed(self, index: int):
        """Handle current tab change."""
        if index >= 0:
            editor = self.editorAt(index)
            if editor:
                self.currentFileChanged.emit(editor.filepath or "")
                editor.setFocus()
    
    def _on_modification_changed(self, index: int, modified: bool):
        """Handle modification state change."""
        if index < 0 or index >= self.count():
            return
        
        title = self.tabText(index)
        if modified and not title.endswith('*'):
            self.setTabText(index, title + '*')
        elif not modified and title.endswith('*'):
            self.setTabText(index, title[:-1])
        
        editor = self.editorAt(index)
        if editor:
            self.fileModified.emit(editor.filepath or "", modified)
    
    def _on_cursor_changed(self, line: int, column: int):
        """Handle cursor position change - for minimap update."""
        pass
    
    def _on_file_dropped(self, filepath: str):
        """Handle file dropped on editor - open it in new tab."""
        self.newTab(filepath)
    
    def _update_file_indices(self):
        """Update file tracking after tab reorder or removal."""
        self._file_tabs.clear()
        for i in range(self.count()):
            editor = self.editorAt(i)
            if editor and editor.filepath:
                self._file_tabs[editor.filepath] = i
    
    def _close_other_tabs(self, keep_index: int):
        """Close all tabs except the specified one."""
        for i in range(self.count() - 1, -1, -1):
            if i != keep_index:
                self.closeTab(i)
    
    def _close_all_tabs(self):
        """Close all tabs."""
        for i in range(self.count() - 1, -1, -1):
            if not self.closeTab(i):
                break
    
    def _close_tabs_to_right(self, index: int):
        """Close all tabs to the right of the specified one."""
        for i in range(self.count() - 1, index, -1):
            self.closeTab(i)
    
    def _close_tabs_to_left(self, index: int):
        """Close all tabs to the left of the specified one."""
        for i in range(index - 1, -1, -1):
            self.closeTab(i)
    
    def _copy_path(self, index: int):
        """Copy file path to clipboard."""
        from PySide6.QtWidgets import QApplication
        
        editor = self.editorAt(index)
        if editor and editor.filepath:
            QApplication.clipboard().setText(editor.filepath)
    
    def _reveal_in_explorer(self, index: int):
        """Open file location in system explorer."""
        import os
        import subprocess
        
        editor = self.editorAt(index)
        if editor and editor.filepath:
            if os.name == 'nt':  # Windows
                subprocess.run(['explorer', '/select,', editor.filepath])
            elif os.name == 'posix':  # Linux/Mac
                subprocess.run(['xdg-open', os.path.dirname(editor.filepath)])
    
    def getOpenFiles(self) -> list:
        """Get list of open file paths."""
        files = []
        for i in range(self.count()):
            editor = self.editorAt(i)
            if editor and editor.filepath:
                files.append(editor.filepath)
        return files
    
    def hasUnsavedChanges(self) -> bool:
        """Check if any tab has unsaved changes."""
        for i in range(self.count()):
            editor = self.editorAt(i)
            if editor and editor.isModified():
                return True
        return False
