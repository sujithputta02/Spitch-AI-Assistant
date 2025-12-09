"""
AI Task Agent - Automatically plans and executes complex multi-step tasks
"""
import json
import re
from typing import Dict, Any, List
from datetime import datetime
from engine.mcp_operations import *
from engine.skill_registry import skill_registry

class AITaskAgent:
    def __init__(self):
        # Initialize registry with core skills
        self._register_core_skills()
        self.available_actions = skill_registry.skills  # Backwards compatibility
        
    def _register_core_skills(self):
        """Register all available actions with the registry"""
        
        # --- App Operations ---
        skill_registry.register_skill(
            "open_app", 
            "Open a desktop application", 
            {"app": "Name of the application (e.g., 'notepad', 'calculator')"}
        )(self.open_app_action)
        
        skill_registry.register_skill(
            "open_website",
            "Open a website in default browser",
            {"url": "URL to open"}
        )(self.open_website_action)
        
        # --- Input Automation ---
        skill_registry.register_skill(
            "type_text",
            "Type text at current cursor position",
            {"text": "Text to type"}
        )(self.type_text_action)
        
        skill_registry.register_skill(
            "press_key",
            "Press a keyboard key or shortcut",
            {"key": "Key or combination (e.g., 'enter', 'ctrl+s')"}
        )(self.press_key_action)
        
        # --- File Intelligence ---
        skill_registry.register_skill(
            "organize_files",
            "Organize files in a directory by type",
            {"directory": "Path to directory (optional)"}
        )(self.organize_files_action)
        
        skill_registry.register_skill(
            "find_recent_files",
            "Find recently modified files",
            {"days": "Number of days to look back (default 7)"}
        )(self.find_recent_files_action)
        
        skill_registry.register_skill(
            "search_files",
            "Search for files by name",
            {"query": "Search query"}
        )(self.search_files_action)
        
        skill_registry.register_skill(
            "find_duplicates",
            "Find duplicate files in a directory",
            {"directory": "Path to directory"}
        )(self.find_duplicates_action)

        # --- Dev Tools ---
        skill_registry.register_skill(
            "git_status",
            "Check git repository status",
            {}
        )(self.git_status_action)
        
        skill_registry.register_skill(
            "git_commit",
            "Commit staged changes",
            {"message": "Commit message"}
        )(self.git_commit_action)
        
        skill_registry.register_skill(
            "git_push",
            "Push changes to remote",
            {}
        )(self.git_push_action)
        
        skill_registry.register_skill(
            "run_shell_command",
            "Run a shell command",
            {"command": "Command to execute"}
        )(self.run_shell_command_action)
        
        # --- System & Utils ---
        skill_registry.register_skill(
            "calculate",
            "Calculate a mathematical expression",
            {"expression": "Math expression (e.g., '5+5')"}
        )(self.calculate_action)
    
    def parse_complex_command(self, command: str) -> List[Dict[str, Any]]:
        """Parse a complex natural language command into actionable steps - ALL-ROUNDER VERSION"""
        command_lower = command.lower()
        steps = []
        
        # ===== BROWSER OPERATIONS =====
        if 'search' in command_lower and ('google' in command_lower or 'web' in command_lower or 'internet' in command_lower):
            # "search google for X" or "search web for X"
            search_match = re.search(r'search\s+(?:google|web|internet)?\s*(?:for\s+)?(.+)', command_lower)
            if search_match:
                query = search_match.group(1).strip()
                steps.append({'action': 'open_website', 'params': {'url': f'https://www.google.com/search?q={query}'}})
        
        elif 'open' in command_lower and any(site in command_lower for site in ['youtube', 'facebook', 'twitter', 'instagram', 'gmail', 'github']):
            # "open youtube" or "open facebook"
            for site in ['youtube', 'facebook', 'twitter', 'instagram', 'gmail', 'github', 'linkedin']:
                if site in command_lower:
                    urls = {
                        'youtube': 'https://www.youtube.com',
                        'facebook': 'https://www.facebook.com',
                        'twitter': 'https://www.twitter.com',
                        'instagram': 'https://www.instagram.com',
                        'gmail': 'https://mail.google.com',
                        'github': 'https://www.github.com',
                        'linkedin': 'https://www.linkedin.com'
                    }
                    steps.append({'action': 'open_website', 'params': {'url': urls[site]}})
                    break
        
        elif 'play' in command_lower and 'youtube' in command_lower:
            # "play X on youtube"
            video_match = re.search(r'play\s+(.+?)\s+on\s+youtube', command_lower)
            if video_match:
                query = video_match.group(1).strip()
                steps.append({'action': 'open_website', 'params': {'url': f'https://www.youtube.com/results?search_query={query}'}})
        
        # ===== OPEN APP AND DO ACTION =====
        elif 'open' in command_lower and 'and' in command_lower and 'calculate' in command_lower:
            # "open calculator and calculate 3+2"
            app_match = re.search(r'open\s+(\w+)', command_lower)
            if app_match:
                app_name = app_match.group(1)
                steps.append({'action': 'open_app', 'params': {'app': app_name}})
            
            # Extract calculation
            calc_match = re.search(r'calculate\s+(.+)', command_lower)
            if calc_match:
                expression = calc_match.group(1).strip()
                steps.append({'action': 'calculate', 'params': {'expression': expression}})
        
        # ===== NOTEPAD/TEXT EDITOR OPERATIONS =====
        elif 'open' in command_lower and 'write' in command_lower:
            # "open notepad, write X, save file"
            app_match = re.search(r'open\s+(\w+)', command_lower)
            if app_match:
                app_name = app_match.group(1)
                steps.append({'action': 'open_app', 'params': {'app': app_name}})
            
            write_match = re.search(r'write\s+(.+?)(?:\s+and\s+save|\s+save|,|$)', command_lower)
            if write_match:
                text = write_match.group(1).strip()
                steps.append({'action': 'type_text', 'params': {'text': text}})
            
            if 'save' in command_lower:
                steps.append({'action': 'press_key', 'params': {'key': 'ctrl+s'}})
        
        # ===== FILE OPERATIONS =====
        elif 'create file' in command_lower or 'write file' in command_lower:
            # "create file X with content Y"
            file_match = re.search(r'(?:create|write)\s+file\s+(?:called\s+)?([^\s]+)', command_lower)
            content_match = re.search(r'(?:with content|containing)\s+(.+)', command_lower)
            
            if file_match:
                filename = file_match.group(1)
                content = content_match.group(1) if content_match else ""
                steps.append({'action': 'write_file', 'params': {'file_path': filename, 'content': content}})
        
        elif 'delete file' in command_lower or 'remove file' in command_lower:
            # "delete file X"
            file_match = re.search(r'(?:delete|remove)\s+file\s+(.+)', command_lower)
            if file_match:
                filename = file_match.group(1).strip()
                steps.append({'action': 'delete_file', 'params': {'file_path': filename}})
        
        elif 'rename file' in command_lower:
            # "rename file X to Y"
            rename_match = re.search(r'rename\s+file\s+(.+?)\s+to\s+(.+)', command_lower)
            if rename_match:
                old_name = rename_match.group(1).strip()
                new_name = rename_match.group(2).strip()
                steps.append({'action': 'rename_file', 'params': {'old_path': old_name, 'new_path': new_name}})
        
        # ===== SYSTEM CONTROL =====
        elif 'set volume' in command_lower or 'volume' in command_lower:
            # "set volume to X"
            volume_match = re.search(r'(\d+)', command_lower)
            if volume_match:
                volume = int(volume_match.group(1))
                steps.append({'action': 'set_volume', 'params': {'level': volume}})
        
        elif 'mute' in command_lower or 'unmute' in command_lower:
            # "mute" or "unmute"
            if 'mute' in command_lower and 'unmute' not in command_lower:
                steps.append({'action': 'set_volume', 'params': {'level': 0}})
            else:
                steps.append({'action': 'set_volume', 'params': {'level': 50}})
        
        elif 'lock' in command_lower and ('screen' in command_lower or 'computer' in command_lower):
            # "lock screen" or "lock computer"
            steps.append({'action': 'lock_screen', 'params': {}})
        
        elif 'shutdown' in command_lower or 'restart' in command_lower or 'sleep' in command_lower:
            # "shutdown computer", "restart", "sleep"
            if 'shutdown' in command_lower:
                steps.append({'action': 'shutdown', 'params': {'action': 'shutdown'}})
            elif 'restart' in command_lower:
                steps.append({'action': 'shutdown', 'params': {'action': 'restart'}})
            elif 'sleep' in command_lower:
                steps.append({'action': 'shutdown', 'params': {'action': 'sleep'}})
        
        # ===== CLIPBOARD OPERATIONS =====
        elif 'copy' in command_lower and 'clipboard' in command_lower:
            # "copy X to clipboard"
            text_match = re.search(r'copy\s+["\']?(.+?)["\']?\s+to\s+clipboard', command_lower)
            if text_match:
                text = text_match.group(1)
                steps.append({'action': 'copy_to_clipboard', 'params': {'text': text}})
        
        # ===== PROCESS MANAGEMENT =====
        elif 'close' in command_lower or 'kill' in command_lower:
            # "close notepad" or "kill chrome"
            app_match = re.search(r'(?:close|kill)\s+(\w+)', command_lower)
            if app_match:
                app_name = app_match.group(1)
                steps.append({'action': 'kill_process', 'params': {'process': app_name}})
        
        # ===== SCREENSHOT =====
        elif 'screenshot' in command_lower or 'take screenshot' in command_lower:
            # "take screenshot"
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            steps.append({'action': 'take_screenshot', 'params': {'filename': filename}})
        
        # ===== EMAIL (if applicable) =====
        elif 'send email' in command_lower or 'email' in command_lower:
            # "send email to X" - opens email client
            steps.append({'action': 'open_website', 'params': {'url': 'https://mail.google.com'}})
        
        # ===== CALCULATOR =====
        elif 'calculate' in command_lower or 'what is' in command_lower:
            # "calculate 5+5" or "what is 10*2"
            expr_match = re.search(r'(?:calculate|what is)\s+(.+)', command_lower)
            if expr_match:
                expression = expr_match.group(1).strip()
                steps.append({'action': 'calculate', 'params': {'expression': expression}})
        
        # ===== MUSIC/MEDIA =====
        elif 'play music' in command_lower or 'play song' in command_lower:
            # "play music" or "play song X"
            song_match = re.search(r'play\s+(?:music|song)\s+(.+)', command_lower)
            if song_match:
                query = song_match.group(1).strip()
                steps.append({'action': 'open_website', 'params': {'url': f'https://www.youtube.com/results?search_query={query}'}})
            else:
                steps.append({'action': 'open_app', 'params': {'app': 'spotify'}})
        
        # ===== FILE INTELLIGENCE OPERATIONS =====
        elif 'organize' in command_lower and 'file' in command_lower:
            # "organize my files" or "organize files in downloads"
            dir_match = re.search(r'in\s+(.+)', command_lower)
            directory = dir_match.group(1) if dir_match else None
            steps.append({'action': 'organize_files', 'params': {'directory': directory}})
        
        elif 'recent file' in command_lower or 'show recent' in command_lower:
            # "show recent files"
            steps.append({'action': 'find_recent_files', 'params': {}})
        
        elif 'search' in command_lower and 'file' in command_lower:
            # "search for file named report"
            query_match = re.search(r'(?:search|find).*?(?:file|files).*?(?:named|called)?\s+(.+)', command_lower)
            if query_match:
                query = query_match.group(1).strip()
                steps.append({'action': 'search_files', 'params': {'query': query}})
        
        elif 'find duplicate' in command_lower or 'duplicate file' in command_lower:
            # "find duplicates in my documents"
            dir_match = re.search(r'in\s+(.+)', command_lower)
            directory = dir_match.group(1) if dir_match else '.'
            steps.append({'action': 'find_duplicates', 'params': {'directory': directory}})
        
        # ===== GIT OPERATIONS =====
        elif 'git status' in command_lower or 'check git' in command_lower:
            # "git status" or "check git status"
            steps.append({'action': 'git_status', 'params': {}})
        
        elif 'git commit' in command_lower or 'commit' in command_lower:
            # "commit changes with message update" or "git commit update"
            msg_match = re.search(r'(?:message|msg)\s+(.+)', command_lower)
            if msg_match:
                message = msg_match.group(1).strip()
            else:
                message = "Update"
            steps.append({'action': 'git_commit', 'params': {'message': message}})
        
        elif 'git push' in command_lower or 'push' in command_lower:
            # "git push" or "push to git"
            steps.append({'action': 'git_push', 'params': {}})
        
        elif 'git pull' in command_lower or 'pull' in command_lower:
            # "git pull" or "pull from git"
            steps.append({'action': 'git_pull', 'params': {}})
        
        elif 'run command' in command_lower or 'execute' in command_lower:
            # "run command npm install"
            cmd_match = re.search(r'(?:run|execute)\s+(?:command\s+)?(.+)', command_lower)
            if cmd_match:
                command = cmd_match.group(1).strip()
                steps.append({'action': 'run_shell_command', 'params': {'command': command}})
        
        # ===== MULTI-APP WORKFLOWS =====
        elif 'open' in command_lower and 'and' in command_lower:
            # "open chrome and youtube"
            apps = re.findall(r'open\s+(\w+)', command_lower)
            for app in apps:
                steps.append({'action': 'open_app', 'params': {'app': app}})
        
        return steps
    
    def execute_task(self, command: str, speak_func=None) -> Dict[str, Any]:
        """Execute a complex task automatically - JARVIS-LEVEL with AI intent parsing"""
        print(f"[AITaskAgent] Parsing command: {command}")
        
        # First, try pattern-based parsing
        steps = self.parse_complex_command(command)
        
        # If no steps found, use AI-powered intent parsing
        if not steps:
            print("[AITaskAgent] No pattern match, using AI intent parser...")
            try:
                from engine.ai_intent_parser import ai_intent_parser
                
                if ai_intent_parser:
                    intent_data = ai_intent_parser.parse_intent(command)
                    
                    if intent_data['confidence'] > 0.5 and intent_data['actions']:
                        print(f"[AITaskAgent] AI parsed intent: {intent_data['intent']} (confidence: {intent_data['confidence']})")
                        steps = intent_data['actions']
                    else:
                        print(f"[AITaskAgent] AI confidence too low: {intent_data['confidence']}")
                else:
                    print("[AITaskAgent] AI intent parser not initialized")
            except Exception as e:
                print(f"[AITaskAgent] AI intent parsing failed: {e}")
        
        if not steps:
            return {
                'success': False,
                'message': "I couldn't understand how to break down that task. Please try rephrasing."
            }
        
        print(f"[AITaskAgent] Planned {len(steps)} steps")
        
        # Execute each step WITH RETRY LOGIC
        results = []
        for i, step in enumerate(steps):
            action = step['action']
            params = step['params']
            
            print(f"[AITaskAgent] Step {i+1}/{len(steps)}: {action} with params {params}")
            
            if action in self.available_actions:
                # Try executing with retry logic
                success, result = self._execute_with_retry(action, params, max_retries=3)
                
                if success:
                    results.append({'step': i+1, 'action': action, 'success': True, 'result': result})
                    print(f"[AITaskAgent] Step {i+1} completed successfully")
                else:
                    error_msg = f"Error in step {i+1}: {result}"
                    results.append({'step': i+1, 'action': action, 'success': False, 'error': error_msg})
                    print(f"[AITaskAgent] Step {i+1} failed after retries: {result}")
                    if speak_func:
                        speak_func(f"Step {i+1} failed: {result}")
                    return {
                        'success': False,
                        'message': error_msg,
                        'completed_steps': results
                    }
            else:
                error_msg = f"Unknown action: {action}"
                results.append({'step': i+1, 'action': action, 'success': False, 'error': error_msg})
                print(f"[AITaskAgent] {error_msg}")
        
        # All steps completed - RECORD IN SESSION, MEMORY, AND PATTERNS
        success_msg = self._generate_success_message(len(steps), command)
        
        # Record interaction in session manager, memory bank, and pattern tracker
        try:
            from engine.session_manager import session_manager
            from engine.memory_bank import memory_bank
            from engine.pattern_tracker import pattern_tracker
            
            intent_data = {'intent': 'multi_step_task', 'entities': {}, 'actions': steps}
            
            # Record in session
            session_manager.add_interaction(
                user_input=command,
                assistant_response=success_msg,
                intent=intent_data,
                success=True
            )
            
            # Record in memory bank
            memory_bank.record_command(
                command=command,
                intent=intent_data,
                success=True
            )
            
            # Track patterns for proactive suggestions
            pattern_tracker.track_command(command, intent_data)
            
            print(f"[AITaskAgent] Recorded interaction in session, memory, and patterns")
        except Exception as e:
            print(f"[AITaskAgent] Could not record interaction: {e}")
        
        if speak_func:
            speak_func(success_msg)
        
        return {
            'success': True,
            'message': success_msg,
            'steps': results
        }
    
    
    def _execute_with_retry(self, action: str, params: Dict, max_retries: int = 3) -> tuple:
        """
        Execute an action with retry logic and exponential backoff
        
        Returns:
            (success: bool, result: Any)
        """
        import time
        
        for attempt in range(max_retries):
            try:
                result = self.available_actions[action](**params)
                return (True, result)
            except Exception as e:
                print(f"[AITaskAgent] Attempt {attempt + 1}/{max_retries} failed: {e}")
                
                if attempt < max_retries - 1:
                    # Exponential backoff: 0.5s, 1s, 2s
                    wait_time = 0.5 * (2 ** attempt)
                    print(f"[AITaskAgent] Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    # Final attempt failed
                    return (False, str(e))
        
        return (False, "Max retries exceeded")
    
    def _generate_success_message(self, num_steps: int, command: str) -> str:
        """Generate conversational success message like JARVIS"""
        command_lower = command.lower()
        
        # Contextual responses based on command type
        if 'open' in command_lower and 'write' in command_lower:
            return "Done. I've opened the application and entered your text."
        elif 'calculate' in command_lower or 'what is' in command_lower:
            return "Calculation complete."
        elif 'search' in command_lower or 'find' in command_lower:
            return "Here's what I found."
        elif 'create file' in command_lower:
            return "File created successfully."
        elif 'screenshot' in command_lower:
            return "Screenshot captured."
        elif 'volume' in command_lower:
            return "Volume adjusted."
        else:
            # Generic but conversational
            if num_steps == 1:
                return "Done."
            else:
                return f"All set. Completed {num_steps} steps."
    
    # Action implementations
    def write_file_action(self, file_path: str, content: str):
        """Write content to a file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"File {file_path} created"
    
    def read_file_action(self, file_path: str):
        """Read file contents"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def open_app_action(self, app: str):
        """Open an application"""
        from engine.features import openCommand
        openCommand(f"open {app}")
        return f"Opened {app}"
    
    def open_website_action(self, url: str):
        """Open a website in the default browser"""
        import webbrowser
        
        # Ensure URL has schema
        if not url.startswith('http'):
            url = 'https://' + url
            
        webbrowser.open(url)
        return f"Opened {url}"
    
    def type_text_action(self, text: str):
        """Type text using keyboard automation"""
        import pyautogui
        import time
        time.sleep(1)  # Wait for app to be ready
        pyautogui.write(text, interval=0.05)
        return f"Typed: {text}"
    
    def press_key_action(self, key: str):
        """Press a keyboard key or combination"""
        import pyautogui
        import time
        time.sleep(0.5)
        
        # Handle key combinations like 'ctrl+s'
        if '+' in key:
            keys = key.split('+')
            pyautogui.hotkey(*keys)
        else:
            pyautogui.press(key)
        return f"Pressed: {key}"
    
    def execute_command_action(self, command: str):
        """Execute a system command"""
        import subprocess
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout if result.stdout else result.stderr
    
    def set_volume_action(self, level: int):
        """Set system volume"""
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMasterVolumeLevelScalar(level / 100.0, None)
            return f"Volume set to {level}%"
        except Exception as e:
            return f"Could not set volume: {e}"
    
    def lock_screen_action(self):
        """Lock the computer screen"""
        import subprocess
        subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
        return "Screen locked"
    
    def shutdown_action(self, action: str = "shutdown"):
        """Shutdown, restart, or sleep"""
        import subprocess
        if action == "shutdown":
            subprocess.run(["shutdown", "/s", "/t", "10"])
            return "System will shutdown in 10 seconds"
        elif action == "restart":
            subprocess.run(["shutdown", "/r", "/t", "10"])
            return "System will restart in 10 seconds"
        elif action == "sleep":
            subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])
            return "System going to sleep"
    
    def copy_to_clipboard_action(self, text: str):
        """Copy text to clipboard"""
        import pyperclip
        pyperclip.copy(text)
        return f"Copied to clipboard: {text}"
    
    def kill_process_action(self, process: str):
        """Kill a process by name"""
        import psutil
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if process.lower() in proc.info['name'].lower():
                    proc.terminate()
                    return f"Terminated {proc.info['name']}"
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return f"Process {process} not found"
    
    def start_process_action(self, command: str):
        """Start a new process"""
        import subprocess
        subprocess.Popen(command, shell=True)
        return f"Started: {command}"
    
    def open_website_action(self, url: str):
        """Open a website in the default browser"""
        import webbrowser
        webbrowser.open(url)
        return f"Opened: {url}"
    
    def delete_file_action(self, file_path: str):
        """Delete a file"""
        import os
        if os.path.exists(file_path):
            os.remove(file_path)
            return f"Deleted: {file_path}"
        else:
            return f"File not found: {file_path}"
    
    def rename_file_action(self, old_path: str, new_path: str):
        """Rename a file"""
        import os
        if os.path.exists(old_path):
            os.rename(old_path, new_path)
            return f"Renamed {old_path} to {new_path}"
        else:
            return f"File not found: {old_path}"
    
    def take_screenshot_action(self, filename: str):
        """Take a screenshot"""
        import pyautogui
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        return f"Screenshot saved as {filename}"
    
    def calculate_action(self, expression: str):
        """Calculate a mathematical expression by typing into calculator - ENHANCED"""
        try:
            import pyautogui
            import pygetwindow as gw
            import time
            
            # Wait for calculator to open
            time.sleep(1.5)
            
            # Find and focus the calculator window - IMPROVED
            calc_windows = []
            
            # Try multiple window title patterns
            title_patterns = ['Calculator', 'calc', 'Калькулятор']  # Support multiple languages
            
            for pattern in title_patterns:
                try:
                    windows = gw.getWindowsWithTitle(pattern)
                    if windows:
                        calc_windows.extend(windows)
                except Exception as e:
                    print(f"[AITaskAgent] Error searching for '{pattern}': {e}")
            
            if calc_windows:
                # Activate the calculator window
                calc_window = calc_windows[0]
                
                try:
                    # Handle minimized windows
                    if calc_window.isMinimized:
                        calc_window.restore()
                        time.sleep(0.3)
                    
                    # Bring to front
                    calc_window.activate()
                    time.sleep(0.5)
                    
                    # Verify window is active
                    if not calc_window.isActive:
                        # Try clicking on the window
                        calc_window.moveTo(calc_window.left + 100, calc_window.top + 100)
                        pyautogui.click()
                        time.sleep(0.3)
                    
                except Exception as e:
                    print(f"[AITaskAgent] Window activation error: {e}")
                    # Continue anyway, might still work
            else:
                print("[AITaskAgent] Warning: Calculator window not found, typing anyway")
            
            # Clean the expression for calculator input
            expression = expression.replace('x', '*').replace('×', '*').replace('÷', '/')
            
            # Type the expression into the calculator
            for char in expression:
                if char in '0123456789+-*/.()':
                    pyautogui.press(char)
                    time.sleep(0.1)
            
            # Press Enter to calculate
            time.sleep(0.3)
            pyautogui.press('enter')
            
            return f"Calculated: {expression}"
        except Exception as e:
            # Fallback: just compute it
            try:
                result = eval(expression)
                return f"{expression} = {result}"
            except:
                return f"Could not calculate: {e}"
    
    # ===== FILE INTELLIGENCE ACTIONS =====
    def organize_files_action(self, directory: str = None):
        """Organize files by category"""
        try:
            from engine.file_intelligence import file_intelligence
            import os
            
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
                for f in files[:5]:
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
                for dup_set in duplicates[:3]:
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
