"""
SuperSupText - Syntax Highlighter
Additional syntax highlighting utilities
"""

from PySide6.QtGui import QColor

# VS Code Dark+ inspired color scheme
DARK_THEME = {
    'background': '#1e1e1e',
    'foreground': '#d4d4d4',
    'comment': '#6a9955',
    'keyword': '#569cd6',
    'string': '#ce9178',
    'number': '#b5cea8',
    'function': '#dcdcaa',
    'class': '#4ec9b0',
    'operator': '#d4d4d4',
    'variable': '#9cdcfe',
    'constant': '#4fc1ff',
    'parameter': '#9cdcfe',
    'property': '#9cdcfe',
    'type': '#4ec9b0',
    'regex': '#d16969',
    'escape': '#d7ba7d',
    'tag': '#569cd6',
    'attribute': '#9cdcfe',
    'selector': '#d7ba7d',
    'pseudo': '#d7ba7d',
    'line_number': '#858585',
    'current_line': '#2d2d2d',
    'selection': '#264f78',
    'caret': '#ffffff',
    'matched_brace': '#ffcc00',
    'unmatched_brace': '#ff0000',
    'edge_line': '#3c3c3c',
    'indent_guide': '#3c3c3c',
    'fold_margin': '#1e1e1e',
}

LIGHT_THEME = {
    'background': '#ffffff',
    'foreground': '#000000',
    'comment': '#008000',
    'keyword': '#0000ff',
    'string': '#a31515',
    'number': '#098658',
    'function': '#795e26',
    'class': '#267f99',
    'operator': '#000000',
    'variable': '#001080',
    'constant': '#0070c1',
    'parameter': '#001080',
    'property': '#001080',
    'type': '#267f99',
    'regex': '#811f3f',
    'escape': '#ee0000',
    'tag': '#800000',
    'attribute': '#ff0000',
    'selector': '#800000',
    'pseudo': '#800000',
    'line_number': '#237893',
    'current_line': '#fffbdd',
    'selection': '#add6ff',
    'caret': '#000000',
    'matched_brace': '#0064001a',
    'unmatched_brace': '#ff0000',
    'edge_line': '#d3d3d3',
    'indent_guide': '#d3d3d3',
    'fold_margin': '#ffffff',
}


class SyntaxHighlighter:
    """
    Manages syntax highlighting themes and configurations.
    """
    
    _themes = {
        'dark': DARK_THEME,
        'light': LIGHT_THEME,
    }
    
    @classmethod
    def get_theme(cls, name: str) -> dict:
        """Get a theme by name."""
        return cls._themes.get(name, DARK_THEME)
    
    @classmethod
    def get_color(cls, theme_name: str, color_name: str) -> QColor:
        """Get a specific color from a theme."""
        theme = cls.get_theme(theme_name)
        color_hex = theme.get(color_name, '#ffffff')
        return QColor(color_hex)
    
    @classmethod
    def register_theme(cls, name: str, theme: dict):
        """Register a new theme."""
        cls._themes[name] = theme
    
    @classmethod
    def get_available_themes(cls) -> list:
        """Get list of available theme names."""
        return list(cls._themes.keys())


# Language keywords for custom highlighting (if needed)
LANGUAGE_KEYWORDS = {
    'Python': [
        'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
        'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
        'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is',
        'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try',
        'while', 'with', 'yield',
    ],
    'JavaScript': [
        'async', 'await', 'break', 'case', 'catch', 'class', 'const', 'continue',
        'debugger', 'default', 'delete', 'do', 'else', 'export', 'extends',
        'finally', 'for', 'function', 'if', 'import', 'in', 'instanceof', 'let',
        'new', 'of', 'return', 'static', 'super', 'switch', 'this', 'throw',
        'try', 'typeof', 'var', 'void', 'while', 'with', 'yield',
        'true', 'false', 'null', 'undefined',
    ],
    'TypeScript': [
        'abstract', 'any', 'as', 'async', 'await', 'boolean', 'break', 'case',
        'catch', 'class', 'const', 'constructor', 'continue', 'debugger',
        'declare', 'default', 'delete', 'do', 'else', 'enum', 'export',
        'extends', 'false', 'finally', 'for', 'from', 'function', 'get', 'if',
        'implements', 'import', 'in', 'infer', 'instanceof', 'interface', 'is',
        'keyof', 'let', 'module', 'namespace', 'never', 'new', 'null', 'number',
        'object', 'of', 'private', 'protected', 'public', 'readonly', 'require',
        'return', 'set', 'static', 'string', 'super', 'switch', 'symbol', 'this',
        'throw', 'true', 'try', 'type', 'typeof', 'undefined', 'unique', 'unknown',
        'var', 'void', 'while', 'with', 'yield',
    ],
}
