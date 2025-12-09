# Spitch AI Assistant - Auto Cleanup Script
# Automatically removes test files, temporary files, and cache

import os
import shutil

# Files and directories to remove
ITEMS_TO_REMOVE = [
    # Test files
    "test_ai_fallback.py",
    "test_ai_intent.py",
    "test_ai_task_agent.py",
    "test_all_rounder.py",
    "test_app_discovery.py",
    "test_calculator_fix.py",
    "test_compound_command.py",
    "test_full_system.py",
    "test_google_api.py",
    "test_google_gemini.py",
    "test_integration.py",
    "test_jarvis_integration.py",
    "test_mcp_operations.py",
    "test_open_command.py",
    "test_phase2.py",
    "test_phase4.py",
    "test_phase5.py",
    "test_phase6.py",
    "test_phase7.py",
    "test_phase8.py",
    "test_session_memory.py",
    "test_system_commands.py",
    # Temporary files
    "temp_actions.txt",
    "test.txt",
    "spitch_conversations.json",
    # Cache
    "__pycache__",
    ".vscode",
]

def main():
    print("=" * 60)
    print("Spitch AI Assistant - Auto Cleanup (Safe Mode)")
    print("=" * 60)
    print("\nRemoving test files, temporary files, and cache...")
    
    removed_count = 0
    errors = []
    
    for item in ITEMS_TO_REMOVE:
        try:
            if os.path.isfile(item):
                os.remove(item)
                print(f"   [OK] Removed file: {item}")
                removed_count += 1
            elif os.path.isdir(item):
                shutil.rmtree(item)
                print(f"   [OK] Removed directory: {item}")
                removed_count += 1
            else:
                print(f"   [SKIP] Not found: {item}")
        except Exception as e:
            error_msg = f"   [ERROR] Error removing {item}: {e}"
            print(error_msg)
            errors.append(error_msg)
    
    print(f"\nCleanup complete! Removed {removed_count} items.")
    
    if errors:
        print(f"\nWARNING: {len(errors)} errors occurred:")
        for error in errors:
            print(error)
    
    print("\nPress Enter to exit...")
    input()

if __name__ == "__main__":
    main()
