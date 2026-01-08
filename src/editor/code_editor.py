"""
SuperSupText - Code Editor Widget
Main editor component with custom syntax highlighting (no QScintilla dependency)
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit, QTextEdit
from PySide6.QtCore import Signal, Qt, QTimer, QRect, QSize, QRegularExpression
from PySide6.QtGui import (
    QColor, QFont, QKeyEvent, QPainter, QTextFormat, QTextCharFormat,
    QSyntaxHighlighter, QTextDocument, QTextCursor, QPen, QFontMetrics
)

from ..utils.settings import Settings


class LineNumberArea(QWidget):
    """Widget to display line numbers."""
    
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
    
    def sizeHint(self):
        return QSize(self.editor.lineNumberAreaWidth(), 0)
    
    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)


class PythonHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for Python code."""
    
    def __init__(self, document):
        super().__init__(document)
        self._formats = {}
        self._setup_formats()
        self._setup_rules()
    
    def _setup_formats(self):
        """Setup text formats for different token types."""
        # Keyword format
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569cd6"))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        self._formats['keyword'] = keyword_format
        
        # Built-in format
        builtin_format = QTextCharFormat()
        builtin_format.setForeground(QColor("#4ec9b0"))
        self._formats['builtin'] = builtin_format
        
        # String format
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#ce9178"))
        self._formats['string'] = string_format
        
        # Comment format
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6a9955"))
        comment_format.setFontItalic(True)
        self._formats['comment'] = comment_format
        
        # Number format
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#b5cea8"))
        self._formats['number'] = number_format
        
        # Function format
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#dcdcaa"))
        self._formats['function'] = function_format
        
        # Decorator format
        decorator_format = QTextCharFormat()
        decorator_format.setForeground(QColor("#d7ba7d"))
        self._formats['decorator'] = decorator_format
        
        # Class format
        class_format = QTextCharFormat()
        class_format.setForeground(QColor("#4ec9b0"))
        self._formats['class'] = class_format
        
        # Self format
        self_format = QTextCharFormat()
        self_format.setForeground(QColor("#9cdcfe"))
        self_format.setFontItalic(True)
        self._formats['self'] = self_format
    
    def _setup_rules(self):
        """Setup highlighting rules."""
        self._rules = []
        
        # Keywords
        keywords = [
            'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
            'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
            'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is',
            'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try',
            'while', 'with', 'yield',
        ]
        keyword_pattern = r'\b(' + '|'.join(keywords) + r')\b'
        self._rules.append((QRegularExpression(keyword_pattern), 'keyword'))
        
        # Built-in functions
        builtins = [
            'abs', 'all', 'any', 'bin', 'bool', 'bytes', 'callable', 'chr',
            'classmethod', 'compile', 'complex', 'delattr', 'dict', 'dir',
            'divmod', 'enumerate', 'eval', 'exec', 'filter', 'float', 'format',
            'frozenset', 'getattr', 'globals', 'hasattr', 'hash', 'help', 'hex',
            'id', 'input', 'int', 'isinstance', 'issubclass', 'iter', 'len',
            'list', 'locals', 'map', 'max', 'memoryview', 'min', 'next', 'object',
            'oct', 'open', 'ord', 'pow', 'print', 'property', 'range', 'repr',
            'reversed', 'round', 'set', 'setattr', 'slice', 'sorted', 'staticmethod',
            'str', 'sum', 'super', 'tuple', 'type', 'vars', 'zip',
        ]
        builtin_pattern = r'\b(' + '|'.join(builtins) + r')\b'
        self._rules.append((QRegularExpression(builtin_pattern), 'builtin'))
        
        # Self
        self._rules.append((QRegularExpression(r'\bself\b'), 'self'))
        
        # Decorators
        self._rules.append((QRegularExpression(r'@\w+'), 'decorator'))
        
        # Function definitions
        self._rules.append((QRegularExpression(r'\bdef\s+(\w+)'), 'function'))
        
        # Class definitions
        self._rules.append((QRegularExpression(r'\bclass\s+(\w+)'), 'class'))
        
        # Numbers
        self._rules.append((QRegularExpression(r'\b\d+\.?\d*\b'), 'number'))
        
        # Strings (single and double quotes)
        self._rules.append((QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), 'string'))
        self._rules.append((QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), 'string'))
        
        # Comments
        self._rules.append((QRegularExpression(r'#[^\n]*'), 'comment'))
    
    def highlightBlock(self, text):
        """Apply highlighting to a block of text."""
        for pattern, format_name in self._rules:
            match_iter = pattern.globalMatch(text)
            while match_iter.hasNext():
                match = match_iter.next()
                start = match.capturedStart()
                length = match.capturedLength()
                self.setFormat(start, length, self._formats[format_name])


class JavaScriptHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for JavaScript/TypeScript code."""
    
    def __init__(self, document):
        super().__init__(document)
        self._formats = {}
        self._setup_formats()
        self._setup_rules()
    
    def _setup_formats(self):
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569cd6"))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        self._formats['keyword'] = keyword_format
        
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#ce9178"))
        self._formats['string'] = string_format
        
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6a9955"))
        comment_format.setFontItalic(True)
        self._formats['comment'] = comment_format
        
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#b5cea8"))
        self._formats['number'] = number_format
        
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#dcdcaa"))
        self._formats['function'] = function_format
    
    def _setup_rules(self):
        self._rules = []
        
        keywords = [
            'async', 'await', 'break', 'case', 'catch', 'class', 'const', 'continue',
            'debugger', 'default', 'delete', 'do', 'else', 'export', 'extends',
            'finally', 'for', 'function', 'if', 'import', 'in', 'instanceof', 'let',
            'new', 'of', 'return', 'static', 'super', 'switch', 'this', 'throw',
            'try', 'typeof', 'var', 'void', 'while', 'with', 'yield',
            'true', 'false', 'null', 'undefined',
        ]
        keyword_pattern = r'\b(' + '|'.join(keywords) + r')\b'
        self._rules.append((QRegularExpression(keyword_pattern), 'keyword'))
        
        # Function calls
        self._rules.append((QRegularExpression(r'\b\w+(?=\s*\()'), 'function'))
        
        # Numbers
        self._rules.append((QRegularExpression(r'\b\d+\.?\d*\b'), 'number'))
        
        # Strings
        self._rules.append((QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), 'string'))
        self._rules.append((QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), 'string'))
        self._rules.append((QRegularExpression(r'`[^`\\]*(\\.[^`\\]*)*`'), 'string'))
        
        # Comments
        self._rules.append((QRegularExpression(r'//[^\n]*'), 'comment'))
        self._rules.append((QRegularExpression(r'/\*.*?\*/'), 'comment'))
    
    def highlightBlock(self, text):
        for pattern, format_name in self._rules:
            match_iter = pattern.globalMatch(text)
            while match_iter.hasNext():
                match = match_iter.next()
                start = match.capturedStart()
                length = match.capturedLength()
                self.setFormat(start, length, self._formats[format_name])


class GenericHighlighter(QSyntaxHighlighter):
    """Generic syntax highlighter for common patterns."""
    
    def __init__(self, document, keywords=None, comment_char='#'):
        super().__init__(document)
        self._keywords = keywords or []
        self._comment_char = comment_char
        self._formats = {}
        self._setup_formats()
        self._setup_rules()
    
    def _setup_formats(self):
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569cd6"))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        self._formats['keyword'] = keyword_format
        
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#ce9178"))
        self._formats['string'] = string_format
        
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6a9955"))
        comment_format.setFontItalic(True)
        self._formats['comment'] = comment_format
        
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#b5cea8"))
        self._formats['number'] = number_format
    
    def _setup_rules(self):
        self._rules = []
        
        if self._keywords:
            keyword_pattern = r'\b(' + '|'.join(self._keywords) + r')\b'
            self._rules.append((QRegularExpression(keyword_pattern), 'keyword'))
        
        # Numbers
        self._rules.append((QRegularExpression(r'\b\d+\.?\d*\b'), 'number'))
        
        # Strings
        self._rules.append((QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), 'string'))
        self._rules.append((QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), 'string'))
        
        # Comments
        if self._comment_char == '//':
            self._rules.append((QRegularExpression(r'//[^\n]*'), 'comment'))
        elif self._comment_char == '#':
            self._rules.append((QRegularExpression(r'#[^\n]*'), 'comment'))
        elif self._comment_char == '--':
            self._rules.append((QRegularExpression(r'--[^\n]*'), 'comment'))
    
    def highlightBlock(self, text):
        for pattern, format_name in self._rules:
            match_iter = pattern.globalMatch(text)
            while match_iter.hasNext():
                match = match_iter.next()
                start = match.capturedStart()
                length = match.capturedLength()
                self.setFormat(start, length, self._formats[format_name])


class CodeEditor(QPlainTextEdit):
    """
    Advanced code editor widget with:
    - Syntax highlighting
    - Line numbers
    - Current line highlighting
    - Multiple cursors (basic support)
    """
    
    # Signals
    cursorPositionChanged_custom = Signal(int, int)  # line, column
    fileDropped = Signal(str)  # filepath - emitted when a file is dropped
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = Settings()
        self._filepath = None
        self._encoding = 'utf-8'
        self._language = 'Text'
        self._highlighter = None
        
        # Multi-cursor support
        self._multi_cursors = []  # List of (position, anchor) tuples
        self._multi_cursor_active = False
        self._cursor_visible = True
        self._blink_timer = QTimer(self)
        self._blink_timer.timeout.connect(self._toggle_cursor_blink)
        self._blink_timer.setInterval(500)  # Blink every 500ms
        
        self._setup_editor()
        self._setup_line_number_area()
        self._apply_theme()
        self._connect_signals()
    
    def _toggle_cursor_blink(self):
        """Toggle cursor visibility for blinking effect."""
        self._cursor_visible = not self._cursor_visible
        self.viewport().update()  # Trigger repaint
    
    def _setup_editor(self):
        """Configure the editor settings."""
        # Font
        font = self.settings.get_font()
        self.setFont(font)
        
        # Tab width
        tab_size = self.settings.get('editor/tab_size', 4)
        font_metrics = QFontMetrics(font)
        self.setTabStopDistance(font_metrics.horizontalAdvance(' ') * tab_size)
        
        # Word wrap - default to enabled for better readability
        if self.settings.get('editor/word_wrap', True):
            self.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        else:
            self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
    
    # Drag and drop handling - forward file drops to main window
    def dragEnterEvent(self, event):
        """Handle drag enter - accept file drops."""
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    event.acceptProposedAction()
                    return
        # For other drags (text), use default behavior
        super().dragEnterEvent(event)
    
    def dragMoveEvent(self, event):
        """Handle drag move."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)
    
    def dropEvent(self, event):
        """Handle drop - open files instead of inserting text."""
        import os
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    filepath = url.toLocalFile()
                    if os.path.isfile(filepath):
                        self.fileDropped.emit(filepath)
            event.acceptProposedAction()
        else:
            # For text drops, use default behavior
            super().dropEvent(event)
    
    def _setup_line_number_area(self):
        """Setup line number area."""
        self.line_number_area = LineNumberArea(self)
        
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        
        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()
    
    def _apply_theme(self):
        """Apply the current theme to the editor."""
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: none;
                selection-background-color: #264f78;
                selection-color: #ffffff;
            }
        """)
    
    def _connect_signals(self):
        """Connect editor signals."""
        self.cursorPositionChanged.connect(self._on_cursor_position_changed)
    
    def _on_cursor_position_changed(self):
        """Handle cursor position change."""
        cursor = self.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.cursorPositionChanged_custom.emit(line, col)
    
    # Line number area methods
    def lineNumberAreaWidth(self):
        """Calculate width of line number area."""
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        
        space = 3 + self.fontMetrics().horizontalAdvance('9') * max(digits, 4)
        return space
    
    def updateLineNumberAreaWidth(self, _):
        """Update viewport margins for line number area."""
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)
    
    def updateLineNumberArea(self, rect, dy):
        """Update line number area on scroll."""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)
    
    def resizeEvent(self, event):
        """Handle resize event."""
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))
    
    def lineNumberAreaPaintEvent(self, event):
        """Paint the line number area."""
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#1e1e1e"))
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        
        current_line = self.textCursor().blockNumber()
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                
                if block_number == current_line:
                    painter.setPen(QColor("#c6c6c6"))
                else:
                    painter.setPen(QColor("#858585"))
                
                painter.drawText(
                    0, top,
                    self.line_number_area.width() - 5,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight,
                    number
                )
            
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1
    
    def highlightCurrentLine(self):
        """Highlight the current line."""
        if not self.settings.get('editor/highlight_current_line', True):
            return
        
        extra_selections = []
        
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor("#2d2d2d")
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        
        self.setExtraSelections(extra_selections)
    
    def set_language(self, language: str):
        """Set the syntax highlighting language."""
        self._language = language
        
        # Remove old highlighter
        if self._highlighter:
            self._highlighter.setDocument(None)
            self._highlighter = None
        
        # Create new highlighter based on language
        if language == 'Python':
            self._highlighter = PythonHighlighter(self.document())
        elif language in ['JavaScript', 'TypeScript']:
            self._highlighter = JavaScriptHighlighter(self.document())
        elif language in ['C', 'C++', 'C#', 'Java', 'Go', 'Rust']:
            keywords = ['if', 'else', 'for', 'while', 'do', 'switch', 'case', 'break',
                       'continue', 'return', 'void', 'int', 'float', 'double', 'char',
                       'bool', 'true', 'false', 'null', 'nullptr', 'class', 'struct',
                       'public', 'private', 'protected', 'static', 'const', 'new', 'delete']
            self._highlighter = GenericHighlighter(self.document(), keywords, '//')
        elif language == 'SQL':
            keywords = ['SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE', 'CREATE',
                       'DROP', 'TABLE', 'INDEX', 'VIEW', 'JOIN', 'LEFT', 'RIGHT', 'INNER',
                       'OUTER', 'ON', 'AND', 'OR', 'NOT', 'NULL', 'AS', 'ORDER', 'BY',
                       'GROUP', 'HAVING', 'LIMIT', 'OFFSET', 'DISTINCT', 'COUNT', 'SUM',
                       'AVG', 'MAX', 'MIN', 'UNION', 'ALL', 'INTO', 'VALUES', 'SET']
            self._highlighter = GenericHighlighter(self.document(), keywords, '--')
        elif language in ['Shell', 'Bash', 'PowerShell']:
            keywords = ['if', 'then', 'else', 'elif', 'fi', 'for', 'while', 'do', 'done',
                       'case', 'esac', 'function', 'return', 'exit', 'echo', 'export',
                       'source', 'alias', 'cd', 'pwd', 'ls', 'rm', 'mv', 'cp', 'mkdir']
            self._highlighter = GenericHighlighter(self.document(), keywords, '#')
        elif language in ['HTML', 'XML']:
            # Simple tag highlighting
            self._highlighter = GenericHighlighter(self.document(), [], '--')
        elif language == 'CSS':
            keywords = ['color', 'background', 'margin', 'padding', 'border', 'font',
                       'display', 'position', 'width', 'height', 'top', 'left', 'right',
                       'bottom', 'flex', 'grid', 'align', 'justify']
            self._highlighter = GenericHighlighter(self.document(), keywords, '//')
    
    # Public API - Compatible with QScintilla interface
    def text(self) -> str:
        """Get the editor text."""
        return self.toPlainText()
    
    def setText(self, text: str):
        """Set the editor text."""
        self.setPlainText(text)
    
    def isModified(self) -> bool:
        """Check if the document is modified."""
        return self.document().isModified()
    
    def setModified(self, modified: bool):
        """Set the modification state."""
        self.document().setModified(modified)
    
    def getCursorPosition(self) -> tuple:
        """Get current cursor position (line, column)."""
        cursor = self.textCursor()
        return cursor.blockNumber() + 1, cursor.columnNumber() + 1
    
    def setCursorPosition(self, line: int, column: int):
        """Set cursor position (1-indexed)."""
        cursor = self.textCursor()
        block = self.document().findBlockByLineNumber(line - 1)
        if block.isValid():
            cursor.setPosition(block.position() + min(column - 1, block.length() - 1))
            self.setTextCursor(cursor)
    
    def goToLine(self, line: int):
        """Go to a specific line."""
        self.setCursorPosition(line, 1)
        self.centerCursor()
    
    def selectedText(self) -> str:
        """Get selected text."""
        return self.textCursor().selectedText()
    
    def replaceSelectedText(self, text: str):
        """Replace selected text."""
        cursor = self.textCursor()
        cursor.insertText(text)
    
    def find(self, text: str, case_sensitive: bool = False,
             whole_word: bool = False, regex: bool = False, forward: bool = True) -> bool:
        """Find text in the editor."""
        flags = QTextDocument.FindFlag(0)
        
        if case_sensitive:
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        if whole_word:
            flags |= QTextDocument.FindFlag.FindWholeWords
        if not forward:
            flags |= QTextDocument.FindFlag.FindBackward
        
        if regex:
            found = self.document().find(QRegularExpression(text), self.textCursor(), flags)
        else:
            found = self.document().find(text, self.textCursor(), flags)
        
        if not found.isNull():
            self.setTextCursor(found)
            return True
        
        # Wrap around
        if forward:
            cursor = QTextCursor(self.document())
            cursor.movePosition(QTextCursor.MoveOperation.Start)
        else:
            cursor = QTextCursor(self.document())
            cursor.movePosition(QTextCursor.MoveOperation.End)
        
        if regex:
            found = self.document().find(QRegularExpression(text), cursor, flags)
        else:
            found = self.document().find(text, cursor, flags)
        
        if not found.isNull():
            self.setTextCursor(found)
            return True
        
        return False
    
    def findNext(self) -> bool:
        """Find next occurrence (placeholder)."""
        return False
    
    def replaceAll(self, find_text: str, replacement: str,
                   case_sensitive: bool = False, whole_word: bool = False, regex: bool = False) -> int:
        """Replace all occurrences."""
        content = self.toPlainText()
        count = 0
        
        if regex:
            import re
            flags = 0 if case_sensitive else re.IGNORECASE
            new_content, count = re.subn(find_text, replacement, content, flags=flags)
        else:
            if case_sensitive:
                count = content.count(find_text)
                new_content = content.replace(find_text, replacement)
            else:
                # Case insensitive replace
                import re
                pattern = re.escape(find_text)
                new_content, count = re.subn(pattern, replacement, content, flags=re.IGNORECASE)
        
        if count > 0:
            self.setPlainText(new_content)
        
        return count
    
    def getLineCount(self) -> int:
        """Get total number of lines."""
        return self.document().blockCount()
    
    def selectNextOccurrence(self):
        """Select next occurrence of current word (Ctrl+D)."""
        cursor = self.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.SelectionType.WordUnderCursor)
            self.setTextCursor(cursor)
        # Note: Full multi-cursor support would require more complex implementation
    
    def selectAllOccurrences(self):
        """Select all occurrences of current selection (Alt+F3) - Multi-cursor mode."""
        cursor = self.textCursor()
        
        # Get the word to search for
        if not cursor.hasSelection():
            cursor.select(QTextCursor.SelectionType.WordUnderCursor)
            self.setTextCursor(cursor)
        
        search_text = cursor.selectedText()
        if not search_text:
            return
        
        # Find all occurrences
        content = self.toPlainText()
        self._multi_cursors = []
        
        start = 0
        while True:
            pos = content.find(search_text, start)
            if pos == -1:
                break
            
            # Store cursor position and anchor for selection
            self._multi_cursors.append((pos, pos + len(search_text)))
            start = pos + len(search_text)
        
        if len(self._multi_cursors) > 1:
            self._multi_cursor_active = True
            self._blink_timer.start()
            self._cursor_visible = True
            self._update_multi_cursor_display()
            print(f"Multi-cursor: {len(self._multi_cursors)} cursors active")
        else:
            self._multi_cursor_active = False
            self._blink_timer.stop()
    
    def _update_multi_cursor_display(self):
        """Update visual display of multi-cursor selections (cursors drawn in paintEvent)."""
        if not self._multi_cursors:
            return
        
        extra_selections = []
        doc_len = self.document().characterCount() - 1
        
        # Selection highlight format
        sel_format = QTextCharFormat()
        sel_format.setBackground(QColor("#264f78"))
        sel_format.setForeground(QColor("#ffffff"))
        
        for anchor, pos in self._multi_cursors:
            # Bounds check
            if anchor > doc_len or pos > doc_len:
                continue
            
            try:
                # Selection highlight
                if anchor != pos:
                    selection = QTextEdit.ExtraSelection()
                    selection.format = sel_format
                    
                    cursor_sel = QTextCursor(self.document())
                    cursor_sel.setPosition(min(anchor, doc_len))
                    cursor_sel.setPosition(min(pos, doc_len), QTextCursor.MoveMode.KeepAnchor)
                    selection.cursor = cursor_sel
                    
                    extra_selections.append(selection)
            except:
                pass
        
        self.setExtraSelections(extra_selections) 
        self.viewport().update()  # Force repaint for cursors
    
    def paintEvent(self, event):
        """Paint custom cursors for multi-cursor mode."""
        super().paintEvent(event)
        
        if self._multi_cursor_active and self._cursor_visible:
            painter = QPainter(self.viewport())
            pen = QPen(QColor("#ffffff")) # White cursor
            pen.setWidth(2)
            painter.setPen(pen)
            
            doc_len = self.document().characterCount() - 1
            
            for anchor, pos in self._multi_cursors:
                if anchor > doc_len or pos > doc_len:
                    continue
                    
                cursor_pos = min(pos, doc_len)
                cursor = QTextCursor(self.document())
                cursor.setPosition(cursor_pos)
                
                rect = self.cursorRect(cursor)
                painter.drawLine(rect.topLeft(), rect.bottomLeft())
    
    def clearMultiCursors(self):
        """Clear all multi-cursors."""
        self._multi_cursors = []
        self._multi_cursor_active = False
        self._blink_timer.stop()
        self.setExtraSelections([])
        self.highlightCurrentLine()
        self.viewport().update()
    
    def toggleComment(self):
        """Toggle line comment."""
        comment_strings = {
            'Python': '#',
            'JavaScript': '//',
            'TypeScript': '//',
            'C': '//',
            'C++': '//',
            'Java': '//',
            'C#': '//',
            'SQL': '--',
            'Shell': '#',
            'PowerShell': '#',
        }
        
        comment = comment_strings.get(self._language, '#')
        
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
        
        line_text = cursor.selectedText()
        stripped = line_text.lstrip()
        
        if stripped.startswith(comment):
            # Remove comment
            idx = line_text.index(comment)
            new_text = line_text[:idx] + line_text[idx + len(comment):].lstrip(' ')
        else:
            # Add comment
            indent = len(line_text) - len(stripped)
            new_text = line_text[:indent] + comment + ' ' + stripped
        
        cursor.insertText(new_text)
    
    def zoomIn(self):
        """Zoom in."""
        font = self.font()
        font.setPointSize(font.pointSize() + 1)
        self.setFont(font)
    
    def zoomOut(self):
        """Zoom out."""
        font = self.font()
        if font.pointSize() > 6:
            font.setPointSize(font.pointSize() - 1)
            self.setFont(font)
    
    def resetZoom(self):
        """Reset zoom to default."""
        font = self.settings.get_font()
        self.setFont(font)
    
    def firstVisibleLine(self):
        """Get first visible line number."""
        return self.firstVisibleBlock().blockNumber()
    
    @property
    def filepath(self) -> str:
        return self._filepath
    
    @filepath.setter
    def filepath(self, value: str):
        self._filepath = value
    
    @property
    def encoding(self) -> str:
        return self._encoding
    
    @encoding.setter
    def encoding(self, value: str):
        self._encoding = value
    
    @property
    def language(self) -> str:
        return self._language
    
    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events for auto-indent and multi-cursor."""
        
        # Handle multi-cursor editing
        if self._multi_cursor_active and self._multi_cursors:
            # Escape to exit multi-cursor mode
            if event.key() == Qt.Key.Key_Escape:
                self.clearMultiCursors()
                return
            
            # Handle text input for multi-cursors
            if event.text() and event.text().isprintable():
                self._multi_cursor_insert(event.text())
                return
            
            # Handle backspace
            if event.key() == Qt.Key.Key_Backspace:
                self._multi_cursor_backspace()
                return
            
            # Handle delete
            if event.key() == Qt.Key.Key_Delete:
                self._multi_cursor_delete()
                return
            
            # Handle arrow keys - move all cursors
            if event.key() in (Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down):
                self._multi_cursor_move(event.key())
                return
        
        # Normal key handling
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            # Auto-indent on enter
            cursor = self.textCursor()
            block = cursor.block()
            text = block.text()
            
            # Get current indentation
            indent = ""
            for char in text:
                if char in ' \t':
                    indent += char
                else:
                    break
            
            # Add extra indent after colon (for Python)
            if text.rstrip().endswith(':') and self._language == 'Python':
                indent += "    "
            
            super().keyPressEvent(event)
            self.insertPlainText(indent)
        elif event.key() == Qt.Key.Key_Tab:
            # Insert spaces instead of tab if configured
            if self.settings.get('editor/use_spaces', True):
                tab_size = self.settings.get('editor/tab_size', 4)
                self.insertPlainText(' ' * tab_size)
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)
    
    def _multi_cursor_insert(self, text: str):
        """Insert text at all cursor positions."""
        if not self._multi_cursors:
            return
        
        # Sort cursors by position (descending) to avoid position shifts affecting earlier edits
        sorted_cursors = sorted(self._multi_cursors, key=lambda x: x[0], reverse=True)
        
        cursor = self.textCursor()
        cursor.beginEditBlock()
        
        new_cursors = []
        
        for anchor, pos in sorted_cursors:
            try:
                c = QTextCursor(self.document())
                doc_len = self.document().characterCount() - 1  # -1 because Qt counts the final \0
                
                anchor = min(anchor, doc_len)
                pos = min(pos, doc_len)
                
                c.setPosition(anchor)
                c.setPosition(pos, QTextCursor.MoveMode.KeepAnchor)
                c.insertText(text)
                
                # New position after insert (collapsed cursor)
                new_pos = anchor + len(text)
                new_cursors.append((new_pos, new_pos))
            except Exception as e:
                print(f"Multi-cursor error: {e}")
        
        cursor.endEditBlock()
        
        # Update cursor positions (reverse back to original order)
        self._multi_cursors = list(reversed(new_cursors))
        
        # Defer display update to avoid issues during edit block
        QTimer.singleShot(0, self._update_multi_cursor_display)
    
    def _multi_cursor_backspace(self):
        """Delete character before all cursor positions."""
        sorted_cursors = sorted(self._multi_cursors, key=lambda x: x[0], reverse=True)
        
        cursor = self.textCursor()
        cursor.beginEditBlock()
        
        new_cursors = []
        for anchor, pos in sorted_cursors:
            c = QTextCursor(self.document())
            if anchor != pos:
                # Delete selection
                c.setPosition(anchor)
                c.setPosition(pos, QTextCursor.MoveMode.KeepAnchor)
                c.removeSelectedText()
                new_cursors.append((anchor, anchor))
            elif anchor > 0:
                # Delete one char before
                c.setPosition(anchor)
                c.deletePreviousChar()
                new_cursors.append((anchor - 1, anchor - 1))
            else:
                new_cursors.append((anchor, anchor))
        
        cursor.endEditBlock()
        
        self._multi_cursors = list(reversed(new_cursors))
        self._update_multi_cursor_display()
    
    def _multi_cursor_delete(self):
        """Delete character after all cursor positions."""
        sorted_cursors = sorted(self._multi_cursors, key=lambda x: x[0], reverse=True)
        
        cursor = self.textCursor()
        cursor.beginEditBlock()
        
        new_cursors = []
        for anchor, pos in sorted_cursors:
            c = QTextCursor(self.document())
            if anchor != pos:
                # Delete selection
                c.setPosition(anchor)
                c.setPosition(pos, QTextCursor.MoveMode.KeepAnchor)
                c.removeSelectedText()
                new_cursors.append((anchor, anchor))
            else:
                # Delete one char after
                c.setPosition(anchor)
                c.deleteChar()
                new_cursors.append((anchor, anchor))
        
        cursor.endEditBlock()
        
        self._multi_cursors = list(reversed(new_cursors))
        self._update_multi_cursor_display()
    
    def _multi_cursor_move(self, key):
        """Move all cursors in the given direction."""
        doc_len = self.document().characterCount() - 1
        new_cursors = []
        
        for anchor, pos in self._multi_cursors:
            # Collapse selection to cursor position
            cursor_pos = pos
            
            if key == Qt.Key.Key_Left:
                new_pos = max(0, cursor_pos - 1)
            elif key == Qt.Key.Key_Right:
                new_pos = min(doc_len, cursor_pos + 1)
            elif key == Qt.Key.Key_Up:
                # Move up one line
                c = QTextCursor(self.document())
                c.setPosition(min(cursor_pos, doc_len))
                c.movePosition(QTextCursor.MoveOperation.Up)
                new_pos = c.position()
            elif key == Qt.Key.Key_Down:
                # Move down one line
                c = QTextCursor(self.document())
                c.setPosition(min(cursor_pos, doc_len))
                c.movePosition(QTextCursor.MoveOperation.Down)
                new_pos = c.position()
            else:
                new_pos = cursor_pos
            
            new_cursors.append((new_pos, new_pos))
        
        self._multi_cursors = new_cursors
        self._update_multi_cursor_display()
