"""JARVIS Image/Capture Skill."""

import os
import shutil
from pathlib import Path
from jarvis_core.logger import get_logger

logger = get_logger()

# Default downloads folder
DOWNLOADS = str(Path.home() / "Downloads")

def organize_downloads() -> dict:
    """Organize downloads folder."""
    try:
        # Create folders
        folders = {"images": [".jpg", ".png", ".gif", ".bmp"],
                 "docs": [".pdf", ".doc", ".docx"],
                 "archives": [".zip", ".rar", ".7z"],
                 "code": [".py", ".js", ".java"]}
        
        downloads = Path(DOWNLOADS)
        organized = 0
        
        for file in downloads.iterdir():
            if file.is_file():
                for folder, exts in folders.items():
                    if file.suffix.lower() in exts:
                        dest = downloads / folder
                        dest.mkdir(exist_ok=True)
                        shutil.move(str(file), str(dest / file.name))
                        organized += 1
                        break
        
        logger.action(f"Organized {organized} files", "SUCCESS", "medium")
        return {"success": True, "files": organized}
    except Exception as e:
        return {"success": False, "error": str(e)}

def find_duplicates() -> list:
    """Find duplicate files."""
    size_map = {}
    duplicates = []
    
    for file in Path(DOWNLOADS).iterdir():
        if file.is_file():
            size = file.stat().st_size
            if size in size_map:
                duplicates.append((str(size_map[size]), str(file)))
            else:
                size_map[size] = file
    
    return duplicates

def clean_old_files(days: int = 30) -> dict:
    """Clean old files."""
    import time
    now = time.time()
    cutoff = now - (days * 86400)
    cleaned = 0
    
    for file in Path(DOWNLOADS).iterdir():
        if file.is_file() and file.stat().st_mtime < cutoff:
            try:
                file.unlink()
                cleaned += 1
            except:
                pass
    
    return {"success": True, "cleaned": cleaned}