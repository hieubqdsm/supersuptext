"""
SuperSupText - File Tree Widget
File explorer sidebar with tree view navigation
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeView, QFileSystemModel,
    QLineEdit, QPushButton, QMenu, QInputDialog, QMessageBox,
    QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Signal, Qt, QDir, QModelIndex
from PySide6.QtGui import QAction, QIcon

from ..utils.settings import Settings


class FileTree(QWidget):
    """
    File explorer sidebar widget.
    
    Features:
    - Tree view of file system
    - Open folder support
    - Context menu (New file, Rename, Delete)
    - File filtering
    - Single/double click to open
    """
    
    # Signals
    fileDoubleClicked = Signal(str)  # filepath
    folderOpened = Signal(str)  # folder path
    hideRequested = Signal()  # request to hide sidebar
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = Settings()
        self._root_path = None
        
        self._setup_ui()
        self._setup_model()
        self._connect_signals()
        self._apply_style()
    
    def _setup_ui(self):
        """Setup the UI layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header with title and collapse button
        header = QWidget()
        header.setObjectName("sidebarHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 8, 8, 8)
        header_layout.setSpacing(8)
        
        from PySide6.QtWidgets import QLabel
        title = QLabel("EXPLORER")
        title.setObjectName("sidebarTitle")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.collapse_btn = QPushButton("«")
        self.collapse_btn.setObjectName("collapseBtn")
        self.collapse_btn.setFixedSize(24, 24)
        self.collapse_btn.setToolTip("Hide Sidebar (Ctrl+B)")
        self.collapse_btn.clicked.connect(self._on_collapse_clicked)
        header_layout.addWidget(self.collapse_btn)
        
        layout.addWidget(header)
        
        # Search/filter box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Filter files...")
        self.search_box.setObjectName("searchBox")
        self.search_box.textChanged.connect(self._on_filter_changed)
        layout.addWidget(self.search_box)
        
        # Tree view
        self.tree = QTreeView()
        self.tree.setObjectName("fileTree")
        self.tree.setHeaderHidden(True)
        self.tree.setAnimated(True)
        self.tree.setIndentation(16)
        self.tree.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        layout.addWidget(self.tree)
    
    def _on_collapse_clicked(self):
        """Handle collapse button click."""
        self.hideRequested.emit()
    
    def _setup_model(self):
        """Setup the file system model."""
        self.model = QFileSystemModel()
        self.model.setRootPath("")
        
        # Show only these file types (all by default)
        self.model.setNameFilterDisables(False)
        
        # Setup tree
        self.tree.setModel(self.model)
        
        # Hide all columns except name
        for i in range(1, self.model.columnCount()):
            self.tree.hideColumn(i)
    
    def _connect_signals(self):
        """Connect signals."""
        self.tree.doubleClicked.connect(self._on_item_double_clicked)
        self.tree.customContextMenuRequested.connect(self._show_context_menu)
    
    def _apply_style(self):
        """Apply styling."""
        self.setStyleSheet("""
            QWidget {
                background-color: #252526;
                color: #cccccc;
            }
            #sidebarHeader {
                background-color: #252526;
                border-bottom: 1px solid #1e1e1e;
            }
            #sidebarTitle {
                color: #bbbbbb;
                font-size: 11px;
                font-weight: bold;
                letter-spacing: 1px;
            }
            #collapseBtn {
                background-color: transparent;
                color: #cccccc;
                border: none;
                border-radius: 3px;
                font-size: 14px;
                font-weight: bold;
            }
            #collapseBtn:hover {
                background-color: #3c3c3c;
            }
            #searchBox {
                background-color: #3c3c3c;
                color: #cccccc;
                border: 1px solid #3c3c3c;
                padding: 6px 10px;
                margin: 8px;
                border-radius: 3px;
            }
            #searchBox:focus {
                border-color: #0e639c;
            }
            #fileTree {
                background-color: #252526;
                border: none;
                outline: none;
            }
            #fileTree::item {
                padding: 4px 8px;
                border-radius: 3px;
            }
            #fileTree::item:hover {
                background-color: #2a2d2e;
            }
            #fileTree::item:selected {
                background-color: #094771;
            }
            #fileTree::branch {
                background-color: #252526;
            }
        """)
    
    def openFolder(self, path: str):
        """Open a folder in the tree."""
        if os.path.isdir(path):
            self._root_path = path
            self.model.setRootPath(path)
            self.tree.setRootIndex(self.model.index(path))
            self.folderOpened.emit(path)
            self.settings.set('files/last_directory', path)
    
    def _open_folder_dialog(self):
        """Show folder dialog."""
        from PySide6.QtWidgets import QFileDialog
        
        last_dir = self.settings.get('files/last_directory') or ""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Open Folder",
            last_dir,
            QFileDialog.Option.ShowDirsOnly
        )
        
        if folder:
            self.openFolder(folder)
    
    def _refresh(self):
        """Refresh the tree view."""
        if self._root_path:
            self.model.setRootPath("")
            self.model.setRootPath(self._root_path)
    
    def _on_filter_changed(self, text: str):
        """Handle filter text change."""
        if text:
            self.model.setNameFilters([f"*{text}*"])
        else:
            self.model.setNameFilters([])
    
    def _on_item_double_clicked(self, index: QModelIndex):
        """Handle item double click."""
        filepath = self.model.filePath(index)
        
        if os.path.isfile(filepath):
            self.fileDoubleClicked.emit(filepath)
    
    def _show_context_menu(self, position):
        """Show context menu."""
        index = self.tree.indexAt(position)
        
        menu = QMenu(self)
        
        if index.isValid():
            filepath = self.model.filePath(index)
            is_dir = os.path.isdir(filepath)
            
            if not is_dir:
                open_action = menu.addAction("Open")
                open_action.triggered.connect(lambda: self.fileDoubleClicked.emit(filepath))
                menu.addSeparator()
            
            if is_dir:
                new_file_action = menu.addAction("New File")
                new_file_action.triggered.connect(lambda: self._new_file(filepath))
                
                new_folder_action = menu.addAction("New Folder")
                new_folder_action.triggered.connect(lambda: self._new_folder(filepath))
                menu.addSeparator()
            
            rename_action = menu.addAction("Rename")
            rename_action.triggered.connect(lambda: self._rename(filepath))
            
            delete_action = menu.addAction("Delete")
            delete_action.triggered.connect(lambda: self._delete(filepath))
            
            menu.addSeparator()
            
            copy_path_action = menu.addAction("Copy Path")
            copy_path_action.triggered.connect(lambda: self._copy_path(filepath))
            
            reveal_action = menu.addAction("Reveal in Explorer")
            reveal_action.triggered.connect(lambda: self._reveal_in_explorer(filepath))
        else:
            # Clicked on empty area
            if self._root_path:
                new_file_action = menu.addAction("New File")
                new_file_action.triggered.connect(lambda: self._new_file(self._root_path))
                
                new_folder_action = menu.addAction("New Folder")
                new_folder_action.triggered.connect(lambda: self._new_folder(self._root_path))
        
        if menu.actions():
            menu.exec_(self.tree.mapToGlobal(position))
    
    def _new_file(self, parent_dir: str):
        """Create a new file."""
        name, ok = QInputDialog.getText(
            self, "New File", "File name:"
        )
        
        if ok and name:
            filepath = os.path.join(parent_dir, name)
            try:
                with open(filepath, 'w') as f:
                    pass
                self.fileDoubleClicked.emit(filepath)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not create file:\n{e}")
    
    def _new_folder(self, parent_dir: str):
        """Create a new folder."""
        name, ok = QInputDialog.getText(
            self, "New Folder", "Folder name:"
        )
        
        if ok and name:
            folderpath = os.path.join(parent_dir, name)
            try:
                os.makedirs(folderpath, exist_ok=True)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not create folder:\n{e}")
    
    def _rename(self, filepath: str):
        """Rename a file or folder."""
        old_name = os.path.basename(filepath)
        name, ok = QInputDialog.getText(
            self, "Rename", "New name:", text=old_name
        )
        
        if ok and name and name != old_name:
            new_path = os.path.join(os.path.dirname(filepath), name)
            try:
                os.rename(filepath, new_path)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not rename:\n{e}")
    
    def _delete(self, filepath: str):
        """Delete a file or folder."""
        result = QMessageBox.question(
            self,
            "Delete",
            f"Are you sure you want to delete '{os.path.basename(filepath)}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if result == QMessageBox.StandardButton.Yes:
            try:
                if os.path.isfile(filepath):
                    os.remove(filepath)
                else:
                    import shutil
                    shutil.rmtree(filepath)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not delete:\n{e}")
    
    def _copy_path(self, filepath: str):
        """Copy path to clipboard."""
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(filepath)
    
    def _reveal_in_explorer(self, filepath: str):
        """Reveal in system explorer."""
        import subprocess
        
        if os.name == 'nt':  # Windows
            if os.path.isfile(filepath):
                subprocess.run(['explorer', '/select,', filepath])
            else:
                subprocess.run(['explorer', filepath])
        elif os.name == 'posix':  # Linux/Mac
            subprocess.run(['xdg-open', os.path.dirname(filepath)])
    
    def getCurrentFolder(self) -> str:
        """Get the currently opened folder."""
        return self._root_path
    
    def setTheme(self, theme_name: str):
        """Set the file tree theme."""
        if theme_name == 'light':
            self.setStyleSheet("""
                QWidget {
                    background-color: #f3f3f3;
                    color: #333333;
                }
                #searchBox {
                    background-color: #ffffff;
                    color: #333333;
                    border: 1px solid #e0e0e0;
                    padding: 6px 10px;
                    margin: 8px;
                    border-radius: 3px;
                }
                #fileTree {
                    background-color: #f3f3f3;
                    border: none;
                }
                #fileTree::item:hover {
                    background-color: #e8e8e8;
                }
                #fileTree::item:selected {
                    background-color: #0060c0;
                    color: white;
                }
            """)
        else:
            self._apply_style()
