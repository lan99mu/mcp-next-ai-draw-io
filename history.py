"""
Diagram version history management

Tracks diagram versions for each session, allowing users to restore
previous states of their diagrams.
"""

from typing import Dict, List, Optional
from datetime import datetime


class DiagramVersion:
    """Represents a single version of a diagram"""
    def __init__(self, xml: str, svg: str = '', timestamp: Optional[datetime] = None):
        self.xml = xml
        self.svg = svg
        self.timestamp = timestamp or datetime.now()


# History storage: session_id -> list of versions
_history: Dict[str, List[DiagramVersion]] = {}


def add_history(session_id: str, xml: str, svg: str = ''):
    """
    Add a diagram version to history
    
    Args:
        session_id: The session identifier
        xml: The diagram XML content
        svg: Optional SVG preview (for thumbnails)
    """
    if session_id not in _history:
        _history[session_id] = []
    
    # Don't add if it's the same as the last version
    if _history[session_id]:
        last_version = _history[session_id][-1]
        if last_version.xml == xml:
            return
    
    version = DiagramVersion(xml, svg)
    _history[session_id].append(version)
    
    # Keep only last 50 versions to prevent memory bloat
    if len(_history[session_id]) > 50:
        _history[session_id] = _history[session_id][-50:]


def get_history(session_id: str) -> List[DiagramVersion]:
    """
    Get all versions for a session
    
    Args:
        session_id: The session identifier
        
    Returns:
        List of DiagramVersion objects
    """
    return _history.get(session_id, [])


def get_version(session_id: str, index: int) -> Optional[DiagramVersion]:
    """
    Get a specific version by index
    
    Args:
        session_id: The session identifier
        index: Version index (0 = oldest, -1 = newest)
        
    Returns:
        DiagramVersion object or None if not found
    """
    versions = _history.get(session_id, [])
    if not versions:
        return None
    
    try:
        return versions[index]
    except IndexError:
        return None


def clear_history(session_id: str):
    """
    Clear all history for a session
    
    Args:
        session_id: The session identifier
    """
    if session_id in _history:
        del _history[session_id]


def get_history_count(session_id: str) -> int:
    """
    Get the number of versions in history
    
    Args:
        session_id: The session identifier
        
    Returns:
        Number of versions
    """
    return len(_history.get(session_id, []))
