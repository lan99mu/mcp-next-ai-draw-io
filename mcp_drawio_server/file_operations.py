"""
File I/O operations for Draw.io diagrams.

This module handles loading and saving Draw.io files to/from disk.
"""

from pathlib import Path


def load_diagram_file(file_path: str) -> str:
    """
    Load a Draw.io diagram from a file.
    
    Args:
        file_path: Path to the .drawio file
        
    Returns:
        The XML content of the file
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        IOError: If there's an error reading the file
    """
    path = Path(file_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    return path.read_text(encoding='utf-8')


def save_diagram_file(file_path: str, xml_content: str) -> int:
    """
    Save a Draw.io diagram to a file.
    
    Args:
        file_path: Path where the file should be saved
        xml_content: The XML content to write
        
    Returns:
        The number of bytes written
        
    Raises:
        IOError: If there's an error writing the file
    """
    path = Path(file_path).resolve()
    
    # Ensure the file has .drawio extension
    if not path.suffix:
        path = path.with_suffix('.drawio')
    
    path.write_text(xml_content, encoding='utf-8')
    return len(xml_content)
