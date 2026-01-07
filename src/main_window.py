"""
SuperSupText - Main Window
The main application window with menu bar, sidebar, and tab container
"""

import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QMenuBar, QMenu, QToolBar, QStatusBar, QLabel, QFileDialog,
    QMessageBox, QInputDialog, QApplication
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QAction, QKeySequence, QIcon, QFont

from .widgets.tab_widget import TabWidget
from .widgets.file_tree import FileTree
from .widgets.search_widget import SearchWidget
from .utils.settings import Settings
from .utils.file_utils import FileUtils
from .utils.session_manager import SessionManager


class MainWindow(QMainWindow):
    """
    Main application window.
    
    Layout:
    - Menu bar (File, Edit, Search, View, Help)
    - Splitter containing:
        - File tree sidebar
        - Tab widget with editors
    - Status bar
    """
    
    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.session_manager = SessionManager()
        
        self._setup_window()
        self._setup_ui()
        self._setup_menus()
        self._setup_shortcuts()
        self._setup_status_bar()
        self._connect_signals()
        self._restore_state()
        
        # Setup session manager and start autosave
        self.session_manager.set_tab_widget(self.tab_widget)
        self.session_manager.start_autosave()
    
    def _setup_window(self):
        """Setup window properties."""
        self.setWindowTitle("SuperSupText")
        self.setMinimumSize(800, 600)
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        
        # Restore geometry
        geometry = self.settings.get('window/geometry')
        if geometry:
            self.restoreGeometry(geometry)
        else:
            self.resize(1200, 800)
            # Center on screen
            screen = QApplication.primaryScreen().geometry()
            self.move(
                (screen.width() - self.width()) // 2,
                (screen.height() - self.height()) // 2
            )
        
        # Window style
        self._apply_style()
    
    def _apply_style(self):
        """Apply global styles."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QMenuBar {
                background-color: #3c3c3c;
                color: #cccccc;
                padding: 2px;
            }
            QMenuBar::item {
                padding: 4px 10px;
                border-radius: 3px;
            }
            QMenuBar::item:selected {
                background-color: #505050;
            }
            QMenu {
                background-color: #2d2d2d;
                color: #cccccc;
                border: 1px solid #454545;
            }
            QMenu::item {
                padding: 6px 30px 6px 20px;
            }
            QMenu::item:selected {
                background-color: #094771;
            }
            QMenu::separator {
                height: 1px;
                background-color: #454545;
                margin: 4px 0;
            }
            QSplitter::handle {
                background-color: #1e1e1e;
            }
            QStatusBar {
                background-color: #007acc;
                color: #ffffff;
            }
            QStatusBar::item {
                border: none;
            }
            QStatusBar QLabel {
                padding: 2px 8px;
            }
        """)
    
    def _setup_ui(self):
        """Setup the main UI layout."""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Search widget (hidden by default)
        self.search_widget = SearchWidget()
        layout.addWidget(self.search_widget)
        
        # Main splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(self.splitter)
        
        # File tree sidebar
        self.file_tree = FileTree()
        self.file_tree.setMinimumWidth(150)
        self.file_tree.setMaximumWidth(500)
        sidebar_width = self.settings.get('window/sidebar_width', 250)
        self.file_tree.setFixedWidth(sidebar_width)
        self.splitter.addWidget(self.file_tree)
        
        # Show/hide sidebar based on settings
        if not self.settings.get('window/sidebar_visible', True):
            self.file_tree.hide()
        
        # Tab widget
        self.tab_widget = TabWidget()
        self.splitter.addWidget(self.tab_widget)
        
        # Set splitter sizes
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
    
    def _setup_menus(self):
        """Setup the menu bar."""
        menubar = self.menuBar()
        
        # ===== File Menu =====
        file_menu = menubar.addMenu("&File")
        
        new_action = file_menu.addAction("&New File")
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._new_file)
        
        open_action = file_menu.addAction("&Open File...")
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._open_file)
        
        open_folder_action = file_menu.addAction("Open &Folder...")
        open_folder_action.setShortcut("Ctrl+K Ctrl+O")
        open_folder_action.triggered.connect(self._open_folder)
        
        file_menu.addSeparator()
        
        save_action = file_menu.addAction("&Save")
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._save_file)
        
        save_as_action = file_menu.addAction("Save &As...")
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self._save_file_as)
        
        save_all_action = file_menu.addAction("Save A&ll")
        save_all_action.setShortcut("Ctrl+Shift+S")
        save_all_action.triggered.connect(self._save_all)
        
        file_menu.addSeparator()
        
        # Recent files submenu
        self.recent_menu = file_menu.addMenu("&Recent Files")
        self._update_recent_menu()
        
        file_menu.addSeparator()
        
        close_action = file_menu.addAction("&Close")
        close_action.setShortcut(QKeySequence.StandardKey.Close)
        close_action.triggered.connect(self._close_tab)
        
        close_all_action = file_menu.addAction("Close All")
        close_all_action.setShortcut("Ctrl+Shift+W")
        close_all_action.triggered.connect(self._close_all_tabs)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("E&xit")
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        
        # ===== Edit Menu =====
        edit_menu = menubar.addMenu("&Edit")
        
        undo_action = edit_menu.addAction("&Undo")
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self._undo)
        
        redo_action = edit_menu.addAction("&Redo")
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self._redo)
        
        edit_menu.addSeparator()
        
        cut_action = edit_menu.addAction("Cu&t")
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.triggered.connect(self._cut)
        
        copy_action = edit_menu.addAction("&Copy")
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self._copy)
        
        paste_action = edit_menu.addAction("&Paste")
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self._paste)
        
        edit_menu.addSeparator()
        
        select_all_action = edit_menu.addAction("Select &All")
        select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        select_all_action.triggered.connect(self._select_all)
        
        edit_menu.addSeparator()
        
        toggle_comment_action = edit_menu.addAction("Toggle &Comment")
        toggle_comment_action.setShortcut("Ctrl+/")
        toggle_comment_action.triggered.connect(self._toggle_comment)
        
        # ===== Selection Menu =====
        selection_menu = menubar.addMenu("&Selection")
        
        select_word_action = selection_menu.addAction("Select &Word")
        select_word_action.setShortcut("Ctrl+D")
        select_word_action.triggered.connect(self._select_next_occurrence)
        
        select_all_occurrences_action = selection_menu.addAction("Select All &Occurrences")
        select_all_occurrences_action.setShortcut("Ctrl+Shift+L")
        select_all_occurrences_action.triggered.connect(self._select_all_occurrences)
        
        # Alt+F3 - Sublime Text style shortcut for Select All Occurrences
        select_all_alt_action = selection_menu.addAction("Select All (Alt+F3)")
        select_all_alt_action.setShortcut("Alt+F3")
        select_all_alt_action.triggered.connect(self._select_all_occurrences)
        
        # ===== Search Menu =====
        search_menu = menubar.addMenu("&Search")
        
        find_action = search_menu.addAction("&Find")
        find_action.setShortcut(QKeySequence.StandardKey.Find)
        find_action.triggered.connect(self._show_find)
        
        find_next_action = search_menu.addAction("Find &Next")
        find_next_action.setShortcut(QKeySequence.StandardKey.FindNext)
        find_next_action.triggered.connect(self._find_next)
        
        find_prev_action = search_menu.addAction("Find &Previous")
        find_prev_action.setShortcut(QKeySequence.StandardKey.FindPrevious)
        find_prev_action.triggered.connect(self._find_prev)
        
        search_menu.addSeparator()
        
        replace_action = search_menu.addAction("&Replace")
        replace_action.setShortcut(QKeySequence.StandardKey.Replace)
        replace_action.triggered.connect(self._show_replace)
        
        search_menu.addSeparator()
        
        goto_line_action = search_menu.addAction("&Go to Line...")
        goto_line_action.setShortcut("Ctrl+G")
        goto_line_action.triggered.connect(self._goto_line)
        
        # ===== View Menu =====
        view_menu = menubar.addMenu("&View")
        
        self.sidebar_action = view_menu.addAction("Toggle &Sidebar")
        self.sidebar_action.setShortcut("Ctrl+B")
        self.sidebar_action.setCheckable(True)
        self.sidebar_action.setChecked(self.settings.get('window/sidebar_visible', True))
        self.sidebar_action.triggered.connect(self._toggle_sidebar)
        
        self.minimap_action = view_menu.addAction("Toggle &Minimap")
        self.minimap_action.setShortcut("Ctrl+Shift+M")
        self.minimap_action.setCheckable(True)
        self.minimap_action.setChecked(self.settings.get('editor/show_minimap', True))
        self.minimap_action.triggered.connect(self._toggle_minimap)
        
        view_menu.addSeparator()
        
        zoom_in_action = view_menu.addAction("Zoom &In")
        zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
        zoom_in_action.triggered.connect(self._zoom_in)
        
        zoom_out_action = view_menu.addAction("Zoom &Out")
        zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
        zoom_out_action.triggered.connect(self._zoom_out)
        
        reset_zoom_action = view_menu.addAction("&Reset Zoom")
        reset_zoom_action.setShortcut("Ctrl+0")
        reset_zoom_action.triggered.connect(self._reset_zoom)
        
        view_menu.addSeparator()
        
        word_wrap_action = view_menu.addAction("&Word Wrap")
        word_wrap_action.setCheckable(True)
        word_wrap_action.setChecked(self.settings.get('editor/word_wrap', False))
        word_wrap_action.triggered.connect(self._toggle_word_wrap)
        
        # ===== Help Menu =====
        help_menu = menubar.addMenu("&Help")
        
        about_action = help_menu.addAction("&About SuperSupText")
        about_action.triggered.connect(self._show_about)
        
        keyboard_shortcuts_action = help_menu.addAction("&Keyboard Shortcuts")
        keyboard_shortcuts_action.setShortcut("Ctrl+Shift+/")
        keyboard_shortcuts_action.triggered.connect(self._show_shortcuts)
    
    def _setup_shortcuts(self):
        """Setup additional keyboard shortcuts."""
        pass  # All shortcuts are set in menu items
    
    def _setup_status_bar(self):
        """Setup the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Cursor position
        self.cursor_label = QLabel("Ln 1, Col 1")
        self.status_bar.addPermanentWidget(self.cursor_label)
        
        # Language
        self.language_label = QLabel("Plain Text")
        self.status_bar.addPermanentWidget(self.language_label)
        
        # Encoding
        self.encoding_label = QLabel("UTF-8")
        self.status_bar.addPermanentWidget(self.encoding_label)
    
    def _connect_signals(self):
        """Connect signals."""
        # File tree
        self.file_tree.fileDoubleClicked.connect(self._open_file_path)
        self.file_tree.hideRequested.connect(self._toggle_sidebar)
        
        # Tab widget
        self.tab_widget.currentFileChanged.connect(self._on_file_changed)
        
        # Search widget
        self.search_widget.closeRequested.connect(self._hide_search)
    
    def _restore_state(self):
        """Restore session state including unsaved buffers."""
        # Restore window state
        state = self.settings.get('window/state')
        if state:
            self.restoreState(state)
        
        # Restore session from session manager (includes unsaved buffers)
        tabs_data, current_tab = self.session_manager.load_session()
        
        if tabs_data:
            for tab_data in tabs_data:
                filepath = tab_data.get('filepath')
                buffer_id = tab_data.get('buffer_id')
                title = tab_data.get('title')
                
                if filepath and os.path.exists(filepath):
                    # Open existing file
                    index = self.tab_widget.newTab(filepath)
                    
                    # If there's a modified buffer, restore it
                    if buffer_id and tab_data.get('modified'):
                        editor = self.tab_widget.editorAt(index)
                        if editor:
                            content = self.session_manager.get_buffer_content(buffer_id)
                            if content:
                                editor.setText(content)
                                editor._buffer_id = buffer_id
                else:
                    # Unsaved buffer - create new tab and restore content
                    index = self.tab_widget.newTab()
                    editor = self.tab_widget.editorAt(index)
                    
                    if editor and buffer_id:
                        content = self.session_manager.get_buffer_content(buffer_id)
                        if content:
                            editor.setText(content)
                            editor._buffer_id = buffer_id
                        
                        # Set language if available
                        if tab_data.get('language'):
                            editor.set_language(tab_data['language'])
                    
                    # Restore tab title
                    if title:
                        self.tab_widget.setTabText(index, title)
                
                # Restore cursor position
                if index >= 0:
                    editor = self.tab_widget.editorAt(index)
                    if editor:
                        line = tab_data.get('cursor_line', 1)
                        col = tab_data.get('cursor_column', 1)
                        editor.setCursorPosition(line, col)
            
            # Restore current tab
            if current_tab < self.tab_widget.count():
                self.tab_widget.setCurrentIndex(current_tab)
        
        # If no tabs, create empty tab
        if self.tab_widget.count() == 0:
            self.tab_widget.newTab()
    
    def _update_recent_menu(self):
        """Update the recent files menu."""
        self.recent_menu.clear()
        
        recent_files = self.settings.get_recent_files()
        
        if not recent_files:
            no_recent = self.recent_menu.addAction("No Recent Files")
            no_recent.setEnabled(False)
            return
        
        for filepath in recent_files[:10]:
            action = self.recent_menu.addAction(os.path.basename(filepath))
            action.setData(filepath)
            action.setToolTip(filepath)
            action.triggered.connect(lambda checked, f=filepath: self._open_file_path(f))
        
        self.recent_menu.addSeparator()
        
        clear_action = self.recent_menu.addAction("Clear Recent Files")
        clear_action.triggered.connect(self._clear_recent)
    
    def _clear_recent(self):
        """Clear recent files."""
        self.settings.clear_recent_files()
        self._update_recent_menu()
    
    # ===== File Actions =====
    
    def _new_file(self):
        """Create a new file."""
        self.tab_widget.newTab()
    
    def _open_file(self):
        """Open a file dialog."""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            self.settings.get('files/last_directory') or "",
            "All Files (*.*)"
        )
        
        if filepath:
            self._open_file_path(filepath)
    
    def _open_file_path(self, filepath: str):
        """Open a specific file."""
        self.tab_widget.newTab(filepath)
        self.settings.set('files/last_directory', os.path.dirname(filepath))
        self._update_recent_menu()
    
    def _open_folder(self):
        """Open a folder."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Open Folder",
            self.settings.get('files/last_directory') or "",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if folder:
            self.file_tree.openFolder(folder)
    
    def _save_file(self):
        """Save the current file."""
        self.tab_widget.saveTab()
    
    def _save_file_as(self):
        """Save the current file with a new name."""
        self.tab_widget.saveTabAs()
    
    def _save_all(self):
        """Save all open files."""
        for i in range(self.tab_widget.count()):
            editor = self.tab_widget.editorAt(i)
            if editor and editor.isModified():
                self.tab_widget.saveTab(i)
    
    def _close_tab(self):
        """Close the current tab."""
        self.tab_widget.closeTab(self.tab_widget.currentIndex())
    
    def _close_all_tabs(self):
        """Close all tabs."""
        for i in range(self.tab_widget.count() - 1, -1, -1):
            if not self.tab_widget.closeTab(i):
                break
    
    # ===== Edit Actions =====
    
    def _get_current_editor(self):
        """Get the current editor."""
        return self.tab_widget.currentEditor()
    
    def _undo(self):
        editor = self._get_current_editor()
        if editor:
            editor.undo()
    
    def _redo(self):
        editor = self._get_current_editor()
        if editor:
            editor.redo()
    
    def _cut(self):
        editor = self._get_current_editor()
        if editor:
            editor.cut()
    
    def _copy(self):
        editor = self._get_current_editor()
        if editor:
            editor.copy()
    
    def _paste(self):
        editor = self._get_current_editor()
        if editor:
            editor.paste()
    
    def _select_all(self):
        editor = self._get_current_editor()
        if editor:
            editor.selectAll()
    
    def _toggle_comment(self):
        editor = self._get_current_editor()
        if editor:
            editor.toggleComment()
    
    def _select_next_occurrence(self):
        """Select next occurrence of current word."""
        editor = self._get_current_editor()
        if editor:
            editor.selectNextOccurrence()
    
    def _select_all_occurrences(self):
        """Select all occurrences of current word."""
        editor = self._get_current_editor()
        if editor:
            editor.selectAllOccurrences()
    
    # ===== Search Actions =====
    
    def _show_find(self):
        """Show the find panel."""
        editor = self._get_current_editor()
        if editor:
            self.search_widget.setEditor(editor)
            self.search_widget.showFind()
    
    def _show_replace(self):
        """Show the replace panel."""
        editor = self._get_current_editor()
        if editor:
            self.search_widget.setEditor(editor)
            self.search_widget.showReplace()
    
    def _hide_search(self):
        """Hide the search panel."""
        self.search_widget.hide()
    
    def _find_next(self):
        self.search_widget._find_next()
    
    def _find_prev(self):
        self.search_widget._find_prev()
    
    def _goto_line(self):
        """Go to a specific line."""
        editor = self._get_current_editor()
        if not editor:
            return
        
        max_line = editor.getLineCount()
        line, ok = QInputDialog.getInt(
            self,
            "Go to Line",
            f"Line number (1-{max_line}):",
            1, 1, max_line
        )
        
        if ok:
            editor.goToLine(line)
    
    # ===== View Actions =====
    
    def _toggle_sidebar(self):
        """Toggle the sidebar visibility."""
        visible = self.file_tree.isVisible()
        self.file_tree.setVisible(not visible)
        self.sidebar_action.setChecked(not visible)
        self.settings.set('window/sidebar_visible', not visible)
    
    def _toggle_minimap(self):
        """Toggle the minimap visibility."""
        visible = self.settings.get('editor/show_minimap', True)
        self.settings.set('editor/show_minimap', not visible)
        self.minimap_action.setChecked(not visible)
        
        # Update all open editors
        for i in range(self.tab_widget.count()):
            container = self.tab_widget.widget(i)
            if container and hasattr(container, 'minimap'):
                container.minimap.setVisible(not visible)
    
    def _zoom_in(self):
        editor = self._get_current_editor()
        if editor:
            editor.zoomIn()
    
    def _zoom_out(self):
        editor = self._get_current_editor()
        if editor:
            editor.zoomOut()
    
    def _reset_zoom(self):
        editor = self._get_current_editor()
        if editor:
            editor.resetZoom()
    
    def _toggle_word_wrap(self):
        """Toggle word wrap."""
        current = self.settings.get('editor/word_wrap', False)
        self.settings.set('editor/word_wrap', not current)
        # Would need to update all editors
    
    # ===== Help Actions =====
    
    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About SuperSupText",
            "<h2>SuperSupText</h2>"
            "<p>Version 1.0.0</p>"
            "<p>A lightweight, fast text editor inspired by Sublime Text.</p>"
            "<p>Built with Python and PySide6.</p>"
            "<hr>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Syntax highlighting for 15+ languages</li>"
            "<li>Multiple tabs with easy navigation</li>"
            "<li>File explorer sidebar</li>"
            "<li>Search and replace with regex</li>"
            "<li>Minimap for quick navigation</li>"
            "<li>Multiple cursors support</li>"
            "</ul>"
        )
    
    def _show_shortcuts(self):
        """Show keyboard shortcuts dialog."""
        shortcuts = """
        <h3>Keyboard Shortcuts</h3>
        <table>
        <tr><td><b>Ctrl+N</b></td><td>New File</td></tr>
        <tr><td><b>Ctrl+O</b></td><td>Open File</td></tr>
        <tr><td><b>Ctrl+S</b></td><td>Save</td></tr>
        <tr><td><b>Ctrl+Shift+S</b></td><td>Save All</td></tr>
        <tr><td><b>Ctrl+W</b></td><td>Close Tab</td></tr>
        <tr><td colspan="2"><hr></td></tr>
        <tr><td><b>Ctrl+F</b></td><td>Find</td></tr>
        <tr><td><b>Ctrl+H</b></td><td>Replace</td></tr>
        <tr><td><b>Ctrl+G</b></td><td>Go to Line</td></tr>
        <tr><td><b>F3</b></td><td>Find Next</td></tr>
        <tr><td><b>Shift+F3</b></td><td>Find Previous</td></tr>
        <tr><td colspan="2"><hr></td></tr>
        <tr><td><b>Ctrl+D</b></td><td>Select Next Occurrence</td></tr>
        <tr><td><b>Ctrl+Shift+L</b></td><td>Select All Occurrences</td></tr>
        <tr><td><b>Ctrl+/</b></td><td>Toggle Comment</td></tr>
        <tr><td colspan="2"><hr></td></tr>
        <tr><td><b>Ctrl+B</b></td><td>Toggle Sidebar</td></tr>
        <tr><td><b>Ctrl+Shift+M</b></td><td>Toggle Minimap</td></tr>
        <tr><td><b>Ctrl++</b></td><td>Zoom In</td></tr>
        <tr><td><b>Ctrl+-</b></td><td>Zoom Out</td></tr>
        <tr><td><b>Ctrl+0</b></td><td>Reset Zoom</td></tr>
        </table>
        """
        QMessageBox.information(self, "Keyboard Shortcuts", shortcuts)
    
    # ===== Event Handlers =====
    
    def _on_file_changed(self, filepath: str):
        """Handle file change."""
        if filepath:
            self.setWindowTitle(f"{os.path.basename(filepath)} - SuperSupText")
            language = FileUtils.get_language_from_extension(filepath)
            self.language_label.setText(language)
            
            # Update search widget editor reference
            editor = self._get_current_editor()
            if editor:
                self.search_widget.setEditor(editor)
                
                # Update cursor position
                line, col = editor.getCursorPosition()
                self.cursor_label.setText(f"Ln {line}, Col {col}")
                
                # Update encoding
                self.encoding_label.setText(editor.encoding.upper())
                
                # Connect cursor position signal (safely disconnect first)
                try:
                    editor.cursorPositionChanged_custom.disconnect(self._on_cursor_changed)
                except (TypeError, RuntimeError):
                    pass  # Not connected
                editor.cursorPositionChanged_custom.connect(self._on_cursor_changed)
        else:
            self.setWindowTitle("SuperSupText")
            self.language_label.setText("Plain Text")
    
    def _on_cursor_changed(self, line: int, column: int):
        """Handle cursor position change."""
        self.cursor_label.setText(f"Ln {line}, Col {column}")
    
    # ===== Drag and Drop =====
    
    def dragEnterEvent(self, event):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            # Check if any URL is a file
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    event.acceptProposedAction()
                    return
        event.ignore()
    
    def dragMoveEvent(self, event):
        """Handle drag move event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        """Handle drop event - open dropped files."""
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    filepath = url.toLocalFile()
                    if os.path.isfile(filepath):
                        self._open_file_path(filepath)
                    elif os.path.isdir(filepath):
                        # If a folder is dropped, open it in the file tree
                        self.file_tree.openFolder(filepath)
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def closeEvent(self, event):
        """Handle window close - autosave everything without asking."""
        # Stop autosave timer
        self.session_manager.stop_autosave()
        
        # Save session (includes all unsaved buffers)
        self.session_manager.save_session()
        
        # Save window state
        self.settings.set('window/geometry', self.saveGeometry())
        self.settings.set('window/state', self.saveState())
        self.settings.set('window/sidebar_width', self.file_tree.width())
        
        # Also save file paths for backward compatibility
        self.settings.save_session(self.tab_widget.getOpenFiles())
        
        event.accept()
