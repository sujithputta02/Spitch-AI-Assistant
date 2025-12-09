# Spitch AI Assistant - Cleanup Script
# This script removes unwanted files from the project

import os
import shutil

# Define file categories to clean
CLEANUP_CATEGORIES = {
    "test_files": [
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
    ],
    "documentation_duplicates": [
        "AI_FALLBACK_SYSTEM.md",
        "GOOGLE_API_STATUS.md",
        "INTEGRATION_COMPLETE.md",
        "LEARNING_SYSTEM_SUMMARY.md",
        "MCP_IMPLEMENTATION.md",
        "MCP_INTEGRATION_COMPLETE.md",
        "OLLAMA_SETUP.md",
        "PROJECT_STRUCTURE.md",
        "QUICK_REFERENCE.md",
        "RUNNING_STATUS.md",
        "SYSTEM_COMPLETE.md",
        "SYSTEM_STATUS.md",
        "USER_MANUAL.txt",
    ],
    "temporary_files": [
        "temp_actions.txt",
        "test.txt",
        "spitch_conversations.json",  # Old conversation format
    ],
    "cache_and_build": [
        "__pycache__",
        ".vscode",
    ],
    "old_app_files": [
        "app.py",  # Replaced by main.py
        "mcp_server.py",  # MCP integration (if not needed)
        "setup_mcp.py",
        "requirements_mcp.txt",
    ],
}

def cleanup(categories_to_remove):
    """Remove files based on selected categories"""
    removed_count = 0
    errors = []
    
    for category in categories_to_remove:
        if category not in CLEANUP_CATEGORIES:
            print(f"WARNING: Unknown category: {category}")
            continue
            
        print(f"\nCleaning {category}...")
        
        for item in CLEANUP_CATEGORIES[category]:
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

if __name__ == "__main__":
    print("=" * 60)
    print("Spitch AI Assistant - Project Cleanup")
    print("=" * 60)
    
    print("\nAvailable cleanup categories:")
    for i, category in enumerate(CLEANUP_CATEGORIES.keys(), 1):
        file_count = len(CLEANUP_CATEGORIES[category])
        print(f"  {i}. {category} ({file_count} items)")
    
    print("\nOptions:")
    print("  - Enter category numbers separated by commas (e.g., 1,2,3)")
    print("  - Enter 'all' to clean everything")
    print("  - Enter 'safe' to clean only test_files and temporary_files")
    print("  - Enter 'quit' to exit")
    
    choice = input("\nYour choice: ").strip().lower()
    
    if choice == 'quit':
        print("Cleanup cancelled.")
        exit(0)
    elif choice == 'all':
        categories = list(CLEANUP_CATEGORIES.keys())
    elif choice == 'safe':
        categories = ['test_files', 'temporary_files', 'cache_and_build']
    else:
        try:
            indices = [int(x.strip()) for x in choice.split(',')]
            category_list = list(CLEANUP_CATEGORIES.keys())
            categories = [category_list[i-1] for i in indices if 0 < i <= len(category_list)]
        except (ValueError, IndexError):
            print("ERROR: Invalid input. Cleanup cancelled.")
            exit(1)
    
    print(f"\nWARNING: About to remove files from: {', '.join(categories)}")
    confirm = input("Are you sure? (yes/no): ").strip().lower()
    
    if confirm == 'yes':
        cleanup(categories)
    else:
        print("Cleanup cancelled.")
