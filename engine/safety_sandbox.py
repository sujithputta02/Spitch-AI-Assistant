"""
Safety Sandbox - Enterprise Security Layer
Intercepts and validates potentially dangerous commands before execution.
Part of Production-Grade Upgrade (Phase 8).
"""
import re
import subprocess
import logging
from typing import Tuple, Optional

# Setup secure audit logging
logging.basicConfig(
    filename='engine/audit.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class SafetySandbox:
    def __init__(self):
        self.blocked_patterns = [
            r'rm\s+-rf\s+/',           # Root deletion
            r'format\s+[a-z]:',        # Disk formatting
            r'del\s+/s\s+/q\s+c:\\',   # Windows root deletion
            r':\(\)\s*\{',             # Fork bomb
            r'mkfs',                   # Filesystem creation
            r'dd\s+if=',               # Direct disk write
            r'chmod\s+777\s+/',        # Global permission grant
            r'wget\s+.*\.sh\s*\|\s*sh' # Pipe to shell
        ]
        
        self.high_risk_patterns = [
            r'pip\s+install',
            r'npm\s+install',
            r'git\s+push',
            r'curl',
            r'wget',
            r'powershell',
            r'cmd\.exe'
        ]
        
    def validate_command(self, command: str) -> Tuple[bool, str]:
        """
        Check if a command is safe to execute.
        Returns: (is_safe, reason)
        """
        command_lower = command.lower()
        
        # 1. Check blocked patterns (NEVER ALLOW)
        for pattern in self.blocked_patterns:
            if re.search(pattern, command_lower):
                logging.warning(f"BLOCKED DANGEROUS COMMAND: {command}")
                return False, f"Blocked dangerous command pattern: {pattern}"
                
        # 2. Check high risk (REQUIRE APPROVAL - simplified for now to WARN)
        for pattern in self.high_risk_patterns:
            if re.search(pattern, command_lower):
                logging.info(f"High risk command detected: {command}")
                # In a real GUI app, we would pause for user click here.
                # For this agent automation, we allow it but log heavily.
                return True, "High risk warning"
                
        return True, "Safe"

    def execute_safe_command(self, command: str) -> Tuple[bool, str]:
        """
        Execute a shell command through the sandbox.
        """
        # 1. Validate
        is_safe, reason = self.validate_command(command)
        if not is_safe:
            return False, f"Security Block: {reason}"
            
        # 2. Log attempt
        logging.info(f"EXECUTING: {command}")
        
        # 3. Execute
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True,
                check=False
            )
            output = result.stdout + result.stderr
            return True, output.strip()
            
        except Exception as e:
            logging.error(f"Execution Error: {command} - {e}")
            return False, str(e)

# Global instance
safety_sandbox = SafetySandbox()
