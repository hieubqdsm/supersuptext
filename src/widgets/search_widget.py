"""
SuperSupText - Search Widget
Search and replace functionality with regex support
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QLabel, QCheckBox, QFrame, QSizePolicy
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QKeySequence, QShortcut


class SearchWidget(QWidget):
    """
    Search and Replace widget.
    
    Features:
    - Find text
    - Replace text
    - Regex support
    - Case sensitive toggle
    - Whole word toggle
    - Find next/previous
    - Replace / Replace All
    """
    
    # Signals
    findRequested = Signal(str, bool, bool, bool, bool)  # text, case, word, regex, forward
    replaceRequested = Signal(str)  # replacement
    replaceAllRequested = Signal(str, str, bool, bool, bool)  # find, replace, case, word, regex
    closeRequested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._editor = None
        self._match_count = 0
        self._current_match = 0
        
        self._setup_ui()
        self._connect_signals()
        self._apply_style()
        
        self.setVisible(False)
    
    def _setup_ui(self):
        """Setup the UI layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        
        # Find row
        find_row = QHBoxLayout()
        find_row.setSpacing(4)
        
        self.find_input = QLineEdit()
        self.find_input.setPlaceholderText("Find")
        self.find_input.setObjectName("findInput")
        find_row.addWidget(self.find_input, 1)
        
        self.match_label = QLabel("")
        self.match_label.setObjectName("matchLabel")
        self.match_label.setMinimumWidth(80)
        find_row.addWidget(self.match_label)
        
        self.prev_btn = QPushButton("◀")
        self.prev_btn.setObjectName("navBtn")
        self.prev_btn.setFixedWidth(28)
        self.prev_btn.setToolTip("Previous Match (Shift+F3)")
        find_row.addWidget(self.prev_btn)
        
        self.next_btn = QPushButton("▶")
        self.next_btn.setObjectName("navBtn")
        self.next_btn.setFixedWidth(28)
        self.next_btn.setToolTip("Next Match (F3)")
        find_row.addWidget(self.next_btn)
        
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("closeBtn")
        self.close_btn.setFixedWidth(28)
        self.close_btn.setToolTip("Close (Escape)")
        find_row.addWidget(self.close_btn)
        
        layout.addLayout(find_row)
        
        # Replace row
        self.replace_row = QWidget()
        replace_layout = QHBoxLayout(self.replace_row)
        replace_layout.setContentsMargins(0, 0, 0, 0)
        replace_layout.setSpacing(4)
        
        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("Replace")
        self.replace_input.setObjectName("replaceInput")
        replace_layout.addWidget(self.replace_input, 1)
        
        self.replace_btn = QPushButton("Replace")
        self.replace_btn.setObjectName("actionBtn")
        replace_layout.addWidget(self.replace_btn)
        
        self.replace_all_btn = QPushButton("Replace All")
        self.replace_all_btn.setObjectName("actionBtn")
        replace_layout.addWidget(self.replace_all_btn)
        
        layout.addWidget(self.replace_row)
        self.replace_row.setVisible(False)
        
        # Options row
        options_row = QHBoxLayout()
        options_row.setSpacing(12)
        
        self.case_check = QCheckBox("Match Case")
        self.case_check.setObjectName("optionCheck")
        options_row.addWidget(self.case_check)
        
        self.word_check = QCheckBox("Whole Word")
        self.word_check.setObjectName("optionCheck")
        options_row.addWidget(self.word_check)
        
        self.regex_check = QCheckBox("Regex")
        self.regex_check.setObjectName("optionCheck")
        options_row.addWidget(self.regex_check)
        
        options_row.addStretch()
        
        self.show_replace_btn = QPushButton("▼ Replace")
        self.show_replace_btn.setObjectName("toggleBtn")
        self.show_replace_btn.setCheckable(True)
        options_row.addWidget(self.show_replace_btn)
        
        layout.addLayout(options_row)
    
    def _connect_signals(self):
        """Connect signals."""
        self.find_input.textChanged.connect(self._on_find_text_changed)
        self.find_input.returnPressed.connect(self._find_next)
        
        self.next_btn.clicked.connect(self._find_next)
        self.prev_btn.clicked.connect(self._find_prev)
        self.close_btn.clicked.connect(self._close)
        
        self.replace_btn.clicked.connect(self._replace)
        self.replace_all_btn.clicked.connect(self._replace_all)
        
        self.show_replace_btn.toggled.connect(self._toggle_replace)
        
        # Options trigger new search
        self.case_check.toggled.connect(lambda: self._find_next())
        self.word_check.toggled.connect(lambda: self._find_next())
        self.regex_check.toggled.connect(lambda: self._find_next())
    
    def _apply_style(self):
        """Apply styling."""
        self.setStyleSheet("""
            QWidget {
                background-color: #252526;
                color: #cccccc;
            }
            #findInput, #replaceInput {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #3c3c3c;
                padding: 6px 10px;
                border-radius: 3px;
                font-size: 13px;
            }
            #findInput:focus, #replaceInput:focus {
                border-color: #0e639c;
            }
            #matchLabel {
                color: #888888;
                font-size: 12px;
            }
            #navBtn, #closeBtn {
                background-color: transparent;
                color: #cccccc;
                border: none;
                border-radius: 3px;
                font-size: 12px;
            }
            #navBtn:hover, #closeBtn:hover {
                background-color: #3c3c3c;
            }
            #actionBtn {
                background-color: #0e639c;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 3px;
            }
            #actionBtn:hover {
                background-color: #1177bb;
            }
            #optionCheck {
                color: #cccccc;
                spacing: 4px;
            }
            #optionCheck::indicator {
                width: 14px;
                height: 14px;
                border: 1px solid #555555;
                border-radius: 3px;
                background-color: #3c3c3c;
            }
            #optionCheck::indicator:checked {
                background-color: #0e639c;
                border-color: #0e639c;
            }
            #toggleBtn {
                background-color: transparent;
                color: #888888;
                border: none;
                padding: 4px 8px;
            }
            #toggleBtn:hover {
                color: #cccccc;
            }
        """)
    
    def setEditor(self, editor):
        """Set the editor to search in."""
        self._editor = editor
    
    def showFind(self):
        """Show the find panel."""
        self.setVisible(True)
        self.replace_row.setVisible(False)
        self.show_replace_btn.setChecked(False)
        self.find_input.setFocus()
        self.find_input.selectAll()
        
        # Pre-fill with selected text
        if self._editor:
            selected = self._editor.selectedText()
            if selected and '\n' not in selected:
                self.find_input.setText(selected)
                self.find_input.selectAll()
    
    def showReplace(self):
        """Show the find and replace panel."""
        self.setVisible(True)
        self.replace_row.setVisible(True)
        self.show_replace_btn.setChecked(True)
        self.find_input.setFocus()
        self.find_input.selectAll()
        
        # Pre-fill with selected text
        if self._editor:
            selected = self._editor.selectedText()
            if selected and '\n' not in selected:
                self.find_input.setText(selected)
                self.find_input.selectAll()
    
    def _toggle_replace(self, checked: bool):
        """Toggle replace panel visibility."""
        self.replace_row.setVisible(checked)
        if checked:
            self.show_replace_btn.setText("▲ Replace")
        else:
            self.show_replace_btn.setText("▼ Replace")
    
    def _close(self):
        """Close the search panel."""
        self.setVisible(False)
        self.closeRequested.emit()
        if self._editor:
            self._editor.setFocus()
    
    def _on_find_text_changed(self, text: str):
        """Handle find text change."""
        if text:
            self._find_next()
        else:
            self.match_label.setText("")
            self._match_count = 0
            self._current_match = 0
    
    def _find_next(self):
        """Find next occurrence."""
        text = self.find_input.text()
        if not text or not self._editor:
            return
        
        found = self._editor.find(
            text,
            case_sensitive=self.case_check.isChecked(),
            whole_word=self.word_check.isChecked(),
            regex=self.regex_check.isChecked(),
            forward=True
        )
        
        self._update_match_count(text, found)
        
        self.findRequested.emit(
            text,
            self.case_check.isChecked(),
            self.word_check.isChecked(),
            self.regex_check.isChecked(),
            True
        )
    
    def _find_prev(self):
        """Find previous occurrence."""
        text = self.find_input.text()
        if not text or not self._editor:
            return
        
        found = self._editor.find(
            text,
            case_sensitive=self.case_check.isChecked(),
            whole_word=self.word_check.isChecked(),
            regex=self.regex_check.isChecked(),
            forward=False
        )
        
        self._update_match_count(text, found)
        
        self.findRequested.emit(
            text,
            self.case_check.isChecked(),
            self.word_check.isChecked(),
            self.regex_check.isChecked(),
            False
        )
    
    def _update_match_count(self, text: str, found: bool):
        """Update the match count label."""
        if not self._editor:
            return
        
        # Count total matches
        content = self._editor.text()
        
        if self.regex_check.isChecked():
            import re
            flags = 0 if self.case_check.isChecked() else re.IGNORECASE
            try:
                matches = len(re.findall(text, content, flags))
            except re.error:
                matches = 0
        else:
            if not self.case_check.isChecked():
                content = content.lower()
                text = text.lower()
            matches = content.count(text)
        
        self._match_count = matches
        
        if matches == 0:
            self.match_label.setText("No results")
            self.match_label.setStyleSheet("color: #cc6666;")
        else:
            self.match_label.setText(f"{matches} result{'s' if matches != 1 else ''}")
            self.match_label.setStyleSheet("color: #888888;")
    
    def _replace(self):
        """Replace current selection."""
        if not self._editor:
            return
        
        replacement = self.replace_input.text()
        
        # If there's a selection that matches the find text, replace it
        selected = self._editor.selectedText()
        find_text = self.find_input.text()
        
        if selected:
            if self.case_check.isChecked():
                matches = selected == find_text
            else:
                matches = selected.lower() == find_text.lower()
            
            if matches:
                self._editor.replaceSelectedText(replacement)
                self.replaceRequested.emit(replacement)
        
        # Find next
        self._find_next()
    
    def _replace_all(self):
        """Replace all occurrences."""
        if not self._editor:
            return
        
        find_text = self.find_input.text()
        replacement = self.replace_input.text()
        
        if not find_text:
            return
        
        count = self._editor.replaceAll(
            find_text,
            replacement,
            case_sensitive=self.case_check.isChecked(),
            whole_word=self.word_check.isChecked(),
            regex=self.regex_check.isChecked()
        )
        
        self.match_label.setText(f"Replaced {count}")
        self.replaceAllRequested.emit(
            find_text,
            replacement,
            self.case_check.isChecked(),
            self.word_check.isChecked(),
            self.regex_check.isChecked()
        )
        
        # Update count after replace
        self._update_match_count(find_text, False)
    
    def keyPressEvent(self, event):
        """Handle key presses."""
        if event.key() == Qt.Key.Key_Escape:
            self._close()
        elif event.key() == Qt.Key.Key_F3:
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                self._find_prev()
            else:
                self._find_next()
        else:
            super().keyPressEvent(event)
    
    def setTheme(self, theme_name: str):
        """Set the search widget theme."""
        if theme_name == 'light':
            self.setStyleSheet("""
                QWidget {
                    background-color: #f3f3f3;
                    color: #333333;
                }
                #findInput, #replaceInput {
                    background-color: #ffffff;
                    color: #333333;
                    border: 1px solid #e0e0e0;
                    padding: 6px 10px;
                    border-radius: 3px;
                }
                #findInput:focus, #replaceInput:focus {
                    border-color: #0e639c;
                }
                #matchLabel {
                    color: #666666;
                }
                #navBtn, #closeBtn {
                    background-color: transparent;
                    color: #333333;
                    border: none;
                    border-radius: 3px;
                }
                #navBtn:hover, #closeBtn:hover {
                    background-color: #e0e0e0;
                }
                #actionBtn {
                    background-color: #0e639c;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 3px;
                }
                #optionCheck {
                    color: #333333;
                }
                #toggleBtn {
                    background-color: transparent;
                    color: #666666;
                    border: none;
                }
            """)
        else:
            self._apply_style()
