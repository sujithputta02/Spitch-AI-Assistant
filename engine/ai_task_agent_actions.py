    
    # ===== FILE INTELLIGENCE ACTIONS =====
    def organize_files_action(self, directory: str = None):
        """Organize files by category"""
        try:
            from engine.file_intelligence import file_intelligence
            
            if directory is None:
                directory = os.path.expanduser('~/Downloads')
            
            stats = file_intelligence.organize_files(directory)
            return f"Organized {stats['moved']} files. Errors: {stats['errors']}"
        except Exception as e:
            return f"Error organizing files: {e}"
    
    def find_recent_files_action(self, days: int = 7, limit: int = 10):
        """Find recently modified files"""
        try:
            from engine.file_intelligence import file_intelligence
            
            files = file_intelligence.get_recent_files(days=days, limit=limit)
            if files:
                result = f"Found {len(files)} recent files:\n"
                for f in files[:5]:  # Show top 5
                    result += f"- {f['name']}\n"
                return result
            else:
                return "No recent files found"
        except Exception as e:
            return f"Error finding recent files: {e}"
    
    def search_files_action(self, query: str, limit: int = 10):
        """Search for files by name"""
        try:
            from engine.file_intelligence import file_intelligence
            
            results = file_intelligence.search_files(query, limit=limit)
            if results:
                result = f"Found {len(results)} files matching '{query}':\n"
                for r in results[:5]:
                    result += f"- {r['name']} ({r['category']})\n"
                return result
            else:
                return f"No files found matching '{query}'"
        except Exception as e:
            return f"Error searching files: {e}"
    
    def find_duplicates_action(self, directory: str = '.'):
        """Find duplicate files"""
        try:
            from engine.file_intelligence import file_intelligence
            
            duplicates = file_intelligence.find_duplicates(directory)
            if duplicates:
                result = f"Found {len(duplicates)} sets of duplicate files:\n"
                for dup_set in duplicates[:3]:  # Show top 3
                    result += f"- {len(dup_set)} duplicates\n"
                return result
            else:
                return "No duplicate files found"
        except Exception as e:
            return f"Error finding duplicates: {e}"
    
    # ===== DEV TOOLS ACTIONS =====
    def git_status_action(self):
        """Get Git repository status"""
        try:
            from engine.dev_tools import dev_tools
            
            result = dev_tools.git_status()
            if 'error' in result:
                return f"Git error: {result['error']}"
            elif result.get('clean'):
                return "Git status: Working tree clean"
            else:
                return f"Git status:\n{result['status']}"
        except Exception as e:
            return f"Error checking git status: {e}"
    
    def git_commit_action(self, message: str = "Update"):
        """Commit changes to Git"""
        try:
            from engine.dev_tools import dev_tools
            
            result = dev_tools.git_commit(message)
            if result.get('success'):
                return f"Committed: {message}"
            else:
                return f"Commit failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error committing: {e}"
    
    def git_push_action(self):
        """Push changes to remote"""
        try:
            from engine.dev_tools import dev_tools
            
            result = dev_tools.git_push()
            if result.get('success'):
                return "Pushed to remote successfully"
            else:
                return f"Push failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error pushing: {e}"
    
    def git_pull_action(self):
        """Pull changes from remote"""
        try:
            from engine.dev_tools import dev_tools
            
            result = dev_tools.git_pull()
            if result.get('success'):
                return "Pulled from remote successfully"
            else:
                return f"Pull failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error pulling: {e}"
    
    def run_shell_command_action(self, command: str):
        """Run a shell command"""
        try:
            from engine.dev_tools import dev_tools
            
            result = dev_tools.run_command(command)
            if result.get('success'):
                return f"Command output:\n{result['output']}"
            else:
                return f"Command failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error running command: {e}"

# Global instance
ai_task_agent = AITaskAgent()
