#!/usr/bin/env python3
"""
JARVIS-OMNI-PC-X-ULTIMA-BEAST - Main Entry Point
A fully free, offline/online, voice-controlled, vision-enabled AI desktop operator.
"""

import json
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import config
from jarvis_core.logger import get_logger
from jarvis_core.brain import get_intent_classifier, classify_command
from jarvis_core.tool_router import get_router
from jarvis_core.memory import get_memory
from jarvis_core.voice_input import get_voice_input
from jarvis_core.voice_output import get_voice_output
from jarvis_core.automation import get_automation
from jarvis_core.system_control import SystemControl


logger = None


def print_banner():
    """Print the JARVIS banner."""
    banner = """
╔═══════════════════════════════════════════════════════════════════╗
║   JARVIS-OMNI-PC-X-ULTIMA-BEAST  v1.0.0              ║
║   Your Personal AI Desktop Operator                     ║
╠═══════════════════════════════════════════════════════════════╣
║   Type 'help' for commands, 'exit' to quit           ║
╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_help():
    """Print help message."""
    help_text = """
╔═══════════════════════════════════════════════════════════════╗
║                 AVAILABLE COMMANDS                  ║
╠═══════════════════════════════════════════════════════════════╣
║   help           - Show this help message            ║
║   status         - Show JARVIS status             ║
║   skills         - List available skills         ║
║   quit/exit      - Exit JARVIS                  ║
╠═══════════════════════════════════════════════════════════════╣
║   App Control:                                 ║
║   open <app>      - Open an application          ║
║   close <app>     - Close an application         ║
║   processes      - List running processes      ║
╠═══════════════════════════════════════════════════════════════╣
║   File Manager:                                ║
║   create file <path> - Create a file               ║
║   create folder <path>- Create a folder              ║
║   list <dir>      - List directory contents    ║
║   search <dir> <pattern> - Search files          ║
║   delete <path>   - Delete file/folder           ║
╠═══════════════════════════════════════════════════════════════╣
║   Terminal:                                   ║
║   run <command>    - Run terminal command          ║
║   powershell <cmd> - Run PowerShell command      ║
╚═══════════════════════════════════════════════════════════════╝
    """
    print(help_text)


def show_status():
    """Show JARVIS status."""
    status = f"""
╔═══════════════════════════════════════════════════════╗
║                 JARVIS STATUS                    ║
╠═══════════════════════════════════════════════════════╣
║   Version:     {config.VERSION:<30}║
║   Mode:       {config.ExecutionMode.get_current():<30}║
║   Base Dir:   {str(config.BASE_DIR):<30}║
║   Logs Dir:   {str(config.LOGS_DIR):<30}║
║   Data Dir:   {str(config.DATA_DIR):<30}║
╚═══════════════════════════════════════════════════════╝
    """
    print(status)


def list_skills():
    """List available skills."""
    router = get_router()
    skills = router.list_skills()
    
    print("\n╔═══════════════════════════════════════════════════════╗")
    print("║           AVAILABLE SKILLS                    ║")
    print("╠═══════════════════════════════════════════════════════╣")
    for skill in skills:
        print(f"║   {skill:<37}║")
    print("╚═══════════════════════════════════════════════════════╝\n")


def handle_command(command: str) -> bool:
    """Handle a user command."""
    global logger
    router = get_router()
    
    cmd_lower = command.lower().strip()
    
    # Built-in commands
    if cmd_lower in ["help", "?"]:
        print_help()
        return True
    
    elif cmd_lower in ["status", "info"]:
        show_status()
        return True
    
    elif cmd_lower in ["skills", "list skills"]:
        list_skills()
        return True
    
    elif cmd_lower in ["quit", "exit", "q"]:
        print("\n👋 Shutting down JARVIS...")
        return False
    
    # Route to skills based on first word
    parts = command.split()
    if not parts:
        return True
    
    action = parts[0].lower()
    
    if action == "open" and len(parts) > 1:
        app = " ".join(parts[1:])
        result = router.route(f"open {app}", app=app)
        print_result(result)
    
    elif action == "close" and len(parts) > 1:
        app = " ".join(parts[1:])
        result = router.route(f"close {app}", app=app)
        print_result(result)
    
    elif action == "list" and len(parts) > 1:
        directory = " ".join(parts[1:])
        # Use file_manager directly
        from skills.file_manager import list_dir
        result = list_dir(directory)
        print_result(result)
    
    elif action == "create" and len(parts) > 2:
        item_type = parts[1].lower()
        path = " ".join(parts[2:])
        if item_type == "file":
            from skills.file_manager import create_file
            result = create_file(path, "")
        elif item_type == "folder":
            from skills.file_manager import create_folder
            result = create_folder(path)
        else:
            result = {"success": False, "error": "Unknown create type. Use 'file' or 'folder'"}
        print_result(result)
    
    elif action == "delete" and len(parts) > 1:
        path = " ".join(parts[1:])
        from skills.file_manager import delete
        result = delete(path)
        print_result(result)
    
    elif action == "search" and len(parts) > 2:
        directory = parts[1]
        pattern = " ".join(parts[2:])
        from skills.file_manager import search_files
        result = search_files(directory, pattern)
        print_result(result)
    
    elif action == "run" and len(parts) > 1:
        cmd = " ".join(parts[1:])
        from skills.terminal_control import run_command
        result = run_command(cmd)
        print_result(result)
    
    elif action == "powershell" and len(parts) > 1:
        cmd = " ".join(parts[1:])
        from skills.terminal_control import run_powershell
        result = run_powershell(cmd)
        print_result(result)
    
    else:
        # Try general routing
        result = router.route(command)
        print_result(result)
    
    return True


def print_result(result: dict):
    """Print command result."""
    if not result:
        print("⚠️ No result returned")
        return
    
    if result.get("success"):
        print(f"✅ Success")
        
        # Print relevant output fields
        if "action" in result:
            print(f"   Action: {result['action']}")
        if "files" in result:
            files = result["files"]
            print(f"   Found {result.get('count', len(files))} files:")
            for f in files[:5]:
                print(f"   - {f}")
            if len(files) > 5:
                print(f"   ... and {len(files) - 5} more")
        if "contents" in result:
            contents = result["contents"]
            print(f"   Found {result.get('count', len(contents))} items:")
            for c in contents[:5]:
                icon = "📁" if c["type"] == "folder" else "📄"
                print(f"   {icon} {c['name']}")
            if len(contents) > 5:
                print(f"   ... and {len(contents) - 5} more")
        if "stdout" in result and result["stdout"]:
            output = result["stdout"].strip()[:500]
            if output:
                print(f"   Output: {output}")
    else:
        error = result.get("error", "Unknown error")
        print(f"❌ Error: {error}")


def main():
    """Main entry point."""
    global logger
    
    # Initialize logger
    logger = get_logger()
    logger.info("JARVIS starting...")
    
    # Print banner
    print_banner()
    
    # Main command loop
    running = True
    while running:
        try:
            command = input("\n🎙️ JARVIS> ").strip()
            
            if command:
                running = handle_command(command)
                
        except KeyboardInterrupt:
            print("\n\n👋 Shutting down JARVIS...")
            running = False
        except Exception as e:
            print(f"\n❌ Error: {e}")
            if logger:
                logger.error(f"Command error: {e}")
    
    logger.info("JARVIS shutdown complete.")


if __name__ == "__main__":
    main()