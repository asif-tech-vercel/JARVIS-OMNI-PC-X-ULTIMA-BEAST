"""
JARVIS File Manager Skill
Create, move, rename, delete, search files safely.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional

from jarvis_core.logger import get_logger


logger = get_logger()


def get_skill():
    """Return the file manager skill functions."""
    return {
        "create_file": create_file,
        "create_folder": create_folder,
        "delete": delete,
        "move": move,
        "copy": copy,
        "rename": rename,
        "search": search_files,
        "list_dir": list_dir,
        "exists": exists,
    }


def create_file(file_path: str, content: str = "") -> Dict[str, Any]:
    """
    Create a file with optional content.
    
    Args:
        file_path: Path to the file
        content: Optional file content
    
    Returns:
        Dict with success status
    """
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        
        logger.action(f"Create file: {file_path}", "SUCCESS", "medium")
        return {"success": True, "action": "created", "file": file_path}
    except Exception as e:
        logger.error(f"Failed to create file: {e}")
        return {"success": False, "error": str(e)}


def create_folder(folder_path: str) -> Dict[str, Any]:
    """
    Create a folder/directory.
    
    Args:
        folder_path: Path to the folder
    
    Returns:
        Dict with success status
    """
    try:
        path = Path(folder_path)
        path.mkdir(parents=True, exist_ok=True)
        
        logger.action(f"Create folder: {folder_path}", "SUCCESS", "medium")
        return {"success": True, "action": "created", "folder": folder_path}
    except Exception as e:
        logger.error(f"Failed to create folder: {e}")
        return {"success": False, "error": str(e)}


def delete(path: str, permanently: bool = False) -> Dict[str, Any]:
    """
    Delete a file or folder.
    
    Args:
        path: Path to delete
        permanently: If False, move to recycle bin (Windows)
    
    Returns:
        Dict with success status
    """
    try:
        p = Path(path)
        
        if not p.exists():
            return {"success": False, "error": f"Path not found: {path}"}
        
        if p.is_file():
            p.unlink()
        elif p.is_dir():
            shutil.rmtree(p)
        
        logger.action(f"Delete: {path}", "SUCCESS", "high")
        return {"success": True, "action": "deleted", "path": path}
    except Exception as e:
        logger.error(f"Failed to delete: {e}")
        return {"success": False, "error": str(e)}


def move(src: str, dest: str) -> Dict[str, Any]:
    """
    Move a file or folder.
    
    Args:
        src: Source path
        dest: Destination path
    
    Returns:
        Dict with success status
    """
    try:
        source = Path(src)
        destination = Path(dest)
        
        if not source.exists():
            return {"success": False, "error": f"Source not found: {src}"}
        
        # Create parent if needed
        destination.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.move(str(source), str(destination))
        
        logger.action(f"Move: {src} -> {dest}", "SUCCESS", "medium")
        return {"success": True, "action": "moved", "from": src, "to": dest}
    except Exception as e:
        logger.error(f"Failed to move: {e}")
        return {"success": False, "error": str(e)}


def copy(src: str, dest: str) -> Dict[str, Any]:
    """
    Copy a file or folder.
    
    Args:
        src: Source path
        dest: Destination path
    
    Returns:
        Dict with success status
    """
    try:
        source = Path(src)
        destination = Path(dest)
        
        if not source.exists():
            return {"success": False, "error": f"Source not found: {src}"}
        
        # Create parent if needed
        destination.parent.mkdir(parents=True, exist_ok=True)
        
        if source.is_file():
            shutil.copy2(str(source), str(destination))
        elif source.is_dir():
            shutil.copytree(str(source), str(destination), dirs_exist_ok=True)
        
        logger.action(f"Copy: {src} -> {dest}", "SUCCESS", "medium")
        return {"success": True, "action": "copied", "from": src, "to": dest}
    except Exception as e:
        logger.error(f"Failed to copy: {e}")
        return {"success": False, "error": str(e)}


def rename(old_path: str, new_path: str) -> Dict[str, Any]:
    """
    Rename a file or folder.
    
    Args:
        old_path: Current path
        new_path: New path
    
    Returns:
        Dict with success status
    """
    try:
        old = Path(old_path)
        new = Path(new_path)
        
        if not old.exists():
            return {"success": False, "error": f"Path not found: {old_path}"}
        
        old.rename(new)
        
        logger.action(f"Rename: {old_path} -> {new_path}", "SUCCESS", "medium")
        return {"success": True, "action": "renamed", "from": old_path, "to": new_path}
    except Exception as e:
        logger.error(f"Failed to rename: {e}")
        return {"success": False, "error": str(e)}


def search_files(directory: str, pattern: str = "*", file_type: str = None) -> Dict[str, Any]:
    """
    Search for files in a directory.
    
    Args:
        directory: Directory to search
        pattern: File name pattern (glob)
        file_type: Optional file extension filter
    
    Returns:
        Dict with list of matching files
    """
    try:
        dir_path = Path(directory)
        
        if not dir_path.exists():
            return {"success": False, "error": f"Directory not found: {directory}"}
        
        # Build glob pattern
        if file_type:
            glob_pattern = f"*.{file_type}"
        else:
            glob_pattern = pattern
        
        files = []
        for f in dir_path.rglob(glob_pattern):
            if f.is_file():
                files.append(str(f))
        
        # Limit results
        files = files[:50]
        
        logger.action(f"Search: {directory}/{pattern}", f"Found {len(files)} files", "low")
        return {
            "success": True,
            "files": files,
            "count": len(files)
        }
    except Exception as e:
        logger.error(f"Failed to search: {e}")
        return {"success": False, "error": str(e)}


def list_dir(directory: str) -> Dict[str, Any]:
    """
    List contents of a directory.
    
    Args:
        directory: Directory path
    
    Returns:
        Dict with directory contents
    """
    try:
        dir_path = Path(directory)
        
        if not dir_path.exists():
            return {"success": False, "error": f"Directory not found: {directory}"}
        
        if not dir_path.is_dir():
            return {"success": False, "error": f"Not a directory: {directory}"}
        
        contents = []
        for item in dir_path.iterdir():
            contents.append({
                "name": item.name,
                "type": "folder" if item.is_dir() else "file",
                "path": str(item)
            })
        
        logger.action(f"List dir: {directory}", f"Found {len(contents)} items", "low")
        return {
            "success": True,
            "contents": contents,
            "count": len(contents)
        }
    except Exception as e:
        logger.error(f"Failed to list directory: {e}")
        return {"success": False, "error": str(e)}


def exists(path: str) -> bool:
    """Check if a path exists."""
    return Path(path).exists()


# Convenience function for intent-based commands
def handle_intent(intent: str, **kwargs) -> Dict[str, Any]:
    """Handle file manager intents."""
    intent_lower = intent.lower()
    
    if "create file" in intent_lower:
        file_path = kwargs.get("path", "")
        content = kwargs.get("content", "")
        return create_file(file_path, content)
    
    elif "create folder" in intent_lower or "create directory" in intent_lower:
        folder_path = kwargs.get("path", "")
        return create_folder(folder_path)
    
    elif "delete" in intent_lower or "remove" in intent_lower:
        path = kwargs.get("path", "")
        return delete(path)
    
    elif "move" in intent_lower:
        src = kwargs.get("source", "")
        dest = kwargs.get("destination", "")
        return move(src, dest)
    
    elif "copy" in intent_lower:
        src = kwargs.get("source", "")
        dest = kwargs.get("destination", "")
        return copy(src, dest)
    
    elif "rename" in intent_lower:
        old = kwargs.get("old", "")
        new = kwargs.get("new", "")
        return rename(old, new)
    
    elif "search" in intent_lower or "find" in intent_lower:
        directory = kwargs.get("directory", ".")
        pattern = kwargs.get("pattern", "*")
        return search_files(directory, pattern)
    
    elif "list" in intent_lower:
        directory = kwargs.get("directory", ".")
        return list_dir(directory)
    
    return {"success": False, "error": "Unknown intent"}