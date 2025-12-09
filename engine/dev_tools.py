"""
Development Tools - Git and code operations

Provides developer assistance:
- Git operations (status, commit, push, pull)
- Code file operations
- Project management
- Build/run commands
"""
import subprocess
import os
from typing import Dict, Any, List, Optional

class DevTools:
    def __init__(self):
        """Initialize development tools"""
        self.git_available = self._check_git()
    
    def _check_git(self) -> bool:
        """Check if Git is available"""
        try:
            result = subprocess.run(['git', '--version'], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def git_status(self, repo_path: str = '.') -> Dict[str, Any]:
        """Get Git repository status"""
        if not self.git_available:
            return {'error': 'Git not available'}
        
        try:
            result = subprocess.run(
                ['git', 'status', '--short'],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'status': result.stdout,
                    'clean': len(result.stdout.strip()) == 0
                }
            else:
                return {'error': result.stderr}
        
        except Exception as e:
            return {'error': str(e)}
    
    def git_commit(self, message: str, repo_path: str = '.') -> Dict[str, Any]:
        """Commit changes to Git"""
        if not self.git_available:
            return {'error': 'Git not available'}
        
        try:
            # Add all changes
            subprocess.run(['git', 'add', '.'], cwd=repo_path, check=True)
            
            # Commit
            result = subprocess.run(
                ['git', 'commit', '-m', message],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr if result.returncode != 0 else None
            }
        
        except Exception as e:
            return {'error': str(e)}
    
    def git_push(self, repo_path: str = '.') -> Dict[str, Any]:
        """Push changes to remote"""
        if not self.git_available:
            return {'error': 'Git not available'}
        
        try:
            result = subprocess.run(
                ['git', 'push'],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr if result.returncode != 0 else None
            }
        
        except Exception as e:
            return {'error': str(e)}
    
    def git_pull(self, repo_path: str = '.') -> Dict[str, Any]:
        """Pull changes from remote"""
        if not self.git_available:
            return {'error': 'Git not available'}
        
        try:
            result = subprocess.run(
                ['git', 'pull'],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr if result.returncode != 0 else None
            }
        
        except Exception as e:
            return {'error': str(e)}
    
    def run_command(self, command: str, cwd: str = '.') -> Dict[str, Any]:
        """Run a shell command SECURELY"""
        from engine.safety_sandbox import safety_sandbox
        
        # Validate and Execute
        is_safe, reason = safety_sandbox.validate_command(command)
        if not is_safe:
            return {'error': f"Security Blocked: {reason}"}
            
        try:
            # We use subprocess directly here to maintain cwd support, 
            # but we've validated the command string above.
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout if result.returncode == 0 else result.stderr,
                'error': result.stderr if result.returncode != 0 else None,
                'returncode': result.returncode
            }
        
        except subprocess.TimeoutExpired:
            return {'error': 'Command timed out'}
        except Exception as e:
            return {'error': str(e)}
    
    def find_project_root(self, start_path: str = '.') -> Optional[str]:
        """Find project root (looks for .git, package.json, etc.)"""
        current = os.path.abspath(start_path)
        
        while current != os.path.dirname(current):  # Not at root
            # Check for project markers
            if any(os.path.exists(os.path.join(current, marker)) 
                   for marker in ['.git', 'package.json', 'requirements.txt', 'pom.xml']):
                return current
            
            current = os.path.dirname(current)
        
        return None

# Global instance
dev_tools = DevTools()
