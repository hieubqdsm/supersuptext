"""
SuperSupText - File Utilities
Handles file operations with encoding detection
"""

import os
import codecs
from pathlib import Path
from typing import Optional, Tuple


class FileUtils:
    """Utility class for file operations."""
    
    # Common encodings to try
    ENCODINGS = ['utf-8', 'utf-8-sig', 'utf-16', 'latin-1', 'cp1252', 'ascii']
    
    # File type to extension mapping
    FILE_TYPES = {
        'Python': ['.py', '.pyw', '.pyi'],
        'JavaScript': ['.js', '.jsx', '.mjs'],
        'TypeScript': ['.ts', '.tsx'],
        'HTML': ['.html', '.htm', '.xhtml'],
        'CSS': ['.css', '.scss', '.sass', '.less'],
        'JSON': ['.json'],
        'YAML': ['.yaml', '.yml'],
        'XML': ['.xml', '.xsl', '.xslt'],
        'Markdown': ['.md', '.markdown'],
        'C': ['.c', '.h'],
        'C++': ['.cpp', '.hpp', '.cc', '.hh', '.cxx', '.hxx'],
        'Java': ['.java'],
        'C#': ['.cs'],
        'PHP': ['.php'],
        'Ruby': ['.rb'],
        'Go': ['.go'],
        'Rust': ['.rs'],
        'SQL': ['.sql'],
        'Shell': ['.sh', '.bash', '.zsh'],
        'Batch': ['.bat', '.cmd'],
        'PowerShell': ['.ps1', '.psm1'],
        'Text': ['.txt', '.text'],
    }
    
    @classmethod
    def read_file(cls, filepath: str) -> Tuple[Optional[str], str]:
        """
        Read a file with automatic encoding detection.
        
        Returns:
            Tuple of (content, encoding) or (None, error_message) on failure
        """
        if not os.path.exists(filepath):
            return None, f"File not found: {filepath}"
        
        if not os.path.isfile(filepath):
            return None, f"Not a file: {filepath}"
        
        # Try each encoding
        for encoding in cls.ENCODINGS:
            try:
                with codecs.open(filepath, 'r', encoding=encoding) as f:
                    content = f.read()
                    return content, encoding
            except (UnicodeDecodeError, UnicodeError):
                continue
            except Exception as e:
                return None, str(e)
        
        # If all encodings fail, try binary read with replacement
        try:
            with open(filepath, 'rb') as f:
                content = f.read().decode('utf-8', errors='replace')
                return content, 'utf-8 (with replacements)'
        except Exception as e:
            return None, str(e)
    
    @classmethod
    def write_file(cls, filepath: str, content: str, encoding: str = 'utf-8') -> Tuple[bool, str]:
        """
        Write content to a file.
        
        Returns:
            Tuple of (success, message)
        """
        try:
            # Create directory if it doesn't exist
            directory = os.path.dirname(filepath)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            with codecs.open(filepath, 'w', encoding=encoding) as f:
                f.write(content)
            
            return True, "File saved successfully"
        except Exception as e:
            return False, str(e)
    
    @classmethod
    def get_language_from_extension(cls, filepath: str) -> str:
        """Get the language name based on file extension."""
        ext = Path(filepath).suffix.lower()
        
        for language, extensions in cls.FILE_TYPES.items():
            if ext in extensions:
                return language
        
        return 'Text'
    
    @classmethod
    def get_file_info(cls, filepath: str) -> dict:
        """Get information about a file."""
        try:
            stat = os.stat(filepath)
            return {
                'name': os.path.basename(filepath),
                'path': filepath,
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'language': cls.get_language_from_extension(filepath),
                'exists': True
            }
        except Exception:
            return {
                'name': os.path.basename(filepath),
                'path': filepath,
                'exists': False
            }
    
    @classmethod
    def format_file_size(cls, size_bytes: int) -> str:
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    @classmethod
    def is_binary_file(cls, filepath: str) -> bool:
        """Check if a file is likely binary."""
        try:
            with open(filepath, 'rb') as f:
                chunk = f.read(8192)
                if b'\x00' in chunk:
                    return True
                # Check for high ratio of non-text characters
                text_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f})
                non_text = len(chunk.translate(None, text_chars))
                return non_text / len(chunk) > 0.30 if chunk else False
        except Exception:
            return False
