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
        """Initialize the AI Task Agent"""
        # Import image generation agent to register the skill
        try:
            import engine.image_generation_agent
            print("[AITaskAgent] Image generation agent loaded")
        except Exception as e:
            print(f"[AITaskAgent] Could not load image generation agent: {e}")
        
        self.skill_registry = skill_registry
        
        # Initialize AI Intent Parser
        try:
            from engine.ai_intent_parser import AIIntentParser
            from engine.ai_assistant import spitch_ai
            self.intent_parser = AIIntentParser(spitch_ai)
            print("[AITaskAgent] AI Intent Parser initialized")
        except Exception as e:
            print(f"[AITaskAgent] Failed to initialize AI Intent Parser: {e}")
            self.intent_parser = None
        
        # Initialize registry with core skills
        self._register_core_skills()
        self.available_actions = skill_registry.skills  # Backwards compatibility
        
        print(f"[AITaskAgent] Initialized with {len(self.available_actions)} skills")
        
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

        skill_registry.register_skill(
            "wait",
            "Wait for specific duration",
            {"seconds": "Seconds to wait"}
        )(self.wait_action)
        
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
        
        skill_registry.register_skill(
            "play_spotify_song",
            "Search and play a song in Spotify",
            {"song": "Song name to search and play"}
        )(self.play_spotify_song_action)
        
        # --- Browser Automation ---
        skill_registry.register_skill(
            "open_browser",
            "Open a web browser for automation",
            {"headless": "Run in headless mode (optional, default: False)"}
        )(self.open_browser_action)
        
        skill_registry.register_skill(
            "navigate_to_url",
            "Navigate to a specific URL in the browser",
            {"url": "URL to navigate to"}
        )(self.navigate_to_url_action)
        
        skill_registry.register_skill(
            "click_on_element",
            "Click a web element",
            {"selector": "CSS selector or element description", "by": "Selector type (css, xpath, id, etc.)"}
        )(self.click_on_element_action)
        
        skill_registry.register_skill(
            "fill_form_field",
            "Fill a form input field",
            {"selector": "Field selector or description", "value": "Value to enter"}
        )(self.fill_form_field_action)
        
        skill_registry.register_skill(
            "extract_text",
            "Extract text from a web element",
            {"selector": "Element selector", "all": "Extract from all matching elements (optional)"}
        )(self.extract_text_action)
        
        skill_registry.register_skill(
            "take_page_screenshot",
            "Take a screenshot of the current page",
            {"filename": "Screenshot filename (optional)"}
        )(self.take_page_screenshot_action)
        
        skill_registry.register_skill(
            "submit_form",
            "Submit a web form",
            {"selector": "Form selector (optional)"}
        )(self.submit_form_action)
        
        skill_registry.register_skill(
            "scroll_page",
            "Scroll the page",
            {"direction": "Scroll direction (up/down)", "amount": "Pixels to scroll (optional)"}
        )(self.scroll_page_action)
        
        skill_registry.register_skill(
            "close_browser",
            "Close the web browser",
            {}
        )(self.close_browser_action)
        
        # Register take_screenshot as alias (for backward compatibility with AI intent parser)
        skill_registry.register_skill(
            "take_screenshot",
            "Take a screenshot (browser or desktop)",
            {"filename": "Screenshot filename (optional)"}
        )(self.take_screenshot_action)
    
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
        
        # ===== BROWSER AUTOMATION =====
        elif ('open browser' in command_lower or 'start browser' in command_lower) and 'automation' not in command_lower:
            # "open browser" or "open browser and go to google.com"
            steps.append({'action': 'open_browser', 'params': {}})
            
            # Check for URL to navigate to
            url_match = re.search(r'(?:go to|navigate to|open)\s+([^\s]+\.[^\s,]+)', command_lower)
            if url_match:
                url = url_match.group(1)
                steps.append({'action': 'navigate_to_url', 'params': {'url': url}})
            
            # Check for search action
            search_match = re.search(r'(?:search|find)\s+(?:for\s+)?(.+?)(?:\s+and|\s+then|$)', command_lower)
            if search_match and not url_match:
                query = search_match.group(1).strip()
                steps.append({'action': 'navigate_to_url', 'params': {'url': f'https://www.google.com/search?q={query}'}})
        
        elif 'fill' in command_lower and ('form' in command_lower or 'field' in command_lower or 'box' in command_lower or 'input' in command_lower):
            # "fill the search box with laptop" or "fill form field username with john"
            field_match = re.search(r'fill\s+(?:the\s+)?(?:form\s+)?(?:field\s+)?(.+?)\s+with\s+["\']?(.+?)["\']?(?:\s+and|\s+then|$)', command_lower)
            if field_match:
                field = field_match.group(1).strip()
                value = field_match.group(2).strip()
                steps.append({'action': 'fill_form_field', 'params': {'selector': field, 'value': value}})
                
                # Check for submit action
                if 'submit' in command_lower or 'press enter' in command_lower or 'click search' in command_lower:
                    steps.append({'action': 'submit_form', 'params': {}})
        
        elif 'click' in command_lower and ('button' in command_lower or 'link' in command_lower or 'element' in command_lower):
            # "click the login button" or "click on search"
            element_match = re.search(r'click\s+(?:on\s+)?(?:the\s+)?(.+?)(?:\s+button|\s+link|\s+element|$)', command_lower)
            if element_match:
                element = element_match.group(1).strip()
                # Convert to selector
                selector = f"button:contains('{element}'), a:contains('{element}'), [value*='{element}']"
                steps.append({'action': 'click_on_element', 'params': {'selector': selector}})
        
        elif 'screenshot' in command_lower and 'page' in command_lower:
            # "take a screenshot of the page" or "screenshot the page"
            filename_match = re.search(r'(?:save as|name it|called)\s+(.+)', command_lower)
            filename = filename_match.group(1).strip() if filename_match else None
            steps.append({'action': 'take_page_screenshot', 'params': {'filename': filename}})
        
        elif 'extract' in command_lower and 'text' in command_lower:
            # "extract all product titles" or "get text from heading"
            selector_match = re.search(r'(?:extract|get)\s+(?:all\s+)?(?:text from\s+)?(.+)', command_lower)
            if selector_match:
                selector = selector_match.group(1).strip()
                extract_all = 'all' in command_lower
                steps.append({'action': 'extract_text', 'params': {'selector': selector, 'all': extract_all}})
        
        elif 'close browser' in command_lower:
            # "close the browser" or "close browser"
            steps.append({'action': 'close_browser', 'params': {}})
        
        # ===== SPOTIFY / MEDIA OPERATIONS =====
        elif 'open' in command_lower and 'spotify' in command_lower and 'play' in command_lower:
            # "open spotify and play X"
            song_match = re.search(r'play\s+(.+?)(?:\s+on\s+spotify|$)', command_lower)
            if song_match:
                song = song_match.group(1).strip()
                # Use dedicated Spotify action with window management
                steps.append({'action': 'play_spotify_song', 'params': {'song': song}})

        # ===== MUSIC/MEDIA (YOUTUBE) =====
        elif 'play' in command_lower and 'youtube' in command_lower:
            # "play X on youtube" - Existing logic
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
        # ===== NOTEPAD/TEXT EDITOR OPERATIONS =====
        elif 'open' in command_lower and ('write' in command_lower or 'type' in command_lower):
            # "open notepad, write X, save file"
            # "open notepad and create a file called X and type Y..."
            app_match = re.search(r'open\s+(\w+)', command_lower)
            if app_match:
                app_name = app_match.group(1)
                steps.append({'action': 'open_app', 'params': {'app': app_name}})
            
            # Content extraction
            # Look for "type X" or "write X" - handle quotes or "inside the file"
            content_match = re.search(r'(?:type|write)\s+(?:["\'])(.+?)(?:["\'])', command_lower) # Strong quote match first
            if not content_match:
                # Fallback to loose match up to next keyword
                content_match = re.search(r'(?:type|write)\s+(.+?)(?:\s+inside|\s+in\s+the|\s+and\s+save|\s+save|\s+to\s+file|$)', command_lower)
            
            if content_match:
                text = content_match.group(1).strip()
                steps.append({'action': 'type_text', 'params': {'text': text}})
            
            # Save logic
            if 'save' in command_lower:
                steps.append({'action': 'press_key', 'params': {'key': 'ctrl+s'}})
                
                # Check for filename to handle "Save As" argument
                # "create a file called X" or "save it as X" or "named X"
                file_match = re.search(r'(?:called|named|save\s+as)\s+([^\s,]+)', command_lower)
                if file_match:
                    filename = file_match.group(1).strip()
                    # Wait for dialog and type filename
                    steps.append({'action': 'type_text', 'params': {'text': filename}})
                    steps.append({'action': 'press_key', 'params': {'key': 'enter'}})
        
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
                import traceback
                if self.intent_parser:
                    intent_data = self.intent_parser.parse_intent(command)
                    
                    if intent_data['confidence'] > 0.5 and intent_data['actions']:
                        print(f"[AITaskAgent] AI parsed intent: {intent_data['intent']} (confidence: {intent_data['confidence']})")
                        steps = intent_data['actions']
                    else:
                        print(f"[AITaskAgent] AI confidence too low: {intent_data['confidence']}")
                else:
                    print("[AITaskAgent] AI intent parser not initialized")
            except Exception as e:
                print(f"[AITaskAgent] AI intent parsing failed: {e}")
                traceback.print_exc()
        
        if not steps:
            return {
                'success': False,
                'message': "I couldn't understand how to break down that task. Please try rephrasing."
            }
        
        print(f"[AITaskAgent] Planned {len(steps)} steps")
        
        # Execute each step WITH RETRY LOGIC
        results = []
        for i, step in enumerate(steps):
            # Handle both 'action' and 'type' keys (AI intent parser uses 'type')
            action = step.get('action') or step.get('type')
            params = step.get('params', {})
            
            print(f"[AITaskAgent] Step {i+1}/{len(steps)}: {action} with params {params}")
            
            if action in self.available_actions:
                # Try executing with retry logic
                success, result = self._execute_with_retry(action, params, max_retries=3)
                
                if success:
                    results.append({'step': i+1, 'action': action, 'success': True, 'result': result})
                    print(f"[AITaskAgent] Step {i+1} completed successfully")
                    
                    # Add delay after opening apps to allow load time
                    if action == 'open_app':
                        import time
                        print("[AITaskAgent] Waiting 5s for app to launch...")
                        time.sleep(5.0)
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
                # Get the function from the skill dict
                skill_info = self.available_actions[action]
                skill_func = skill_info['func'] if isinstance(skill_info, dict) else skill_info
                result = skill_func(**params)
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
        if 'spotify' in command_lower and 'play' in command_lower:
            return "Spotify opened. Please search for your song manually, or say 'play [song] on youtube' for automatic playback."
        elif 'open' in command_lower and 'write' in command_lower:
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
    
    def wait_action(self, seconds: float):
        """Wait for a specified duration"""
        import time
        time.sleep(float(seconds))
        return f"Waited {seconds}s"
    
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
    
    def take_screenshot_action(self, filename: str = None):
        """Take a screenshot - uses browser automation if browser is open, otherwise desktop screenshot"""
        try:
            # Check if browser is open - if so, use browser screenshot
            from engine.browser_automation import browser_automation
            
            if browser_automation.is_browser_open():
                # Use browser screenshot
                filepath = browser_automation.take_screenshot(filename)
                if filepath:
                    return f"Screenshot saved: {filepath}"
                else:
                    return "Failed to take browser screenshot"
            else:
                # Fall back to desktop screenshot
                import pyautogui
                from datetime import datetime
                
                if not filename:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"screenshot_{timestamp}.png"
                
                screenshot = pyautogui.screenshot()
                screenshot.save(filename)
                return f"Screenshot saved as {filename}"
        except Exception as e:
            return f"Error taking screenshot: {e}"
    
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
    
    def play_spotify_song_action(self, song: str):
        """Search and play a song in Spotify with robust window management"""
        try:
            import pyautogui
            import pygetwindow as gw
            import time
            from engine.features import openCommand
            
            # Step 1: Open Spotify
            print(f"[Spotify] Opening Spotify...")
            openCommand("open spotify")
            time.sleep(6)  # Wait for Spotify to fully load
            
            # Step 2: Find and focus Spotify window
            print(f"[Spotify] Finding Spotify window...")
            spotify_windows = []
            
            # Try multiple window title patterns
            title_patterns = ['Spotify Premium', 'Spotify Free', 'Spotify', 'spotify']
            
            for pattern in title_patterns:
                try:
                    windows = gw.getWindowsWithTitle(pattern)
                    if windows:
                        spotify_windows.extend(windows)
                        break
                except Exception as e:
                    print(f"[Spotify] Error searching for '{pattern}': {e}")
            
            if spotify_windows:
                spotify_window = spotify_windows[0]
                print(f"[Spotify] Found window: {spotify_window.title}")
                
                # Restore if minimized
                if spotify_window.isMinimized:
                    spotify_window.restore()
                    time.sleep(0.5)
                
                # Bring to front and activate
                spotify_window.activate()
                time.sleep(1.0)
                
                # Click on window to ensure focus
                try:
                    center_x = spotify_window.left + spotify_window.width // 2
                    center_y = spotify_window.top + spotify_window.height // 2
                    pyautogui.click(center_x, center_y)
                    time.sleep(0.5)
                except:
                    pass
            else:
                print("[Spotify] Warning: Could not find Spotify window, proceeding anyway...")
                time.sleep(2)
            
            # Step 3: Focus search bar (Ctrl+L)
            print(f"[Spotify] Focusing search bar...")
            pyautogui.hotkey('ctrl', 'l')
            time.sleep(0.8)
            
            # Step 4: Clear any existing text
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            
            # Step 5: Type song name
            print(f"[Spotify] Typing song: {song}")
            pyautogui.write(song, interval=0.05)
            time.sleep(0.5)
            
            # Step 6: Press Enter to search
            print(f"[Spotify] Searching...")
            pyautogui.press('enter')
            time.sleep(3.0)  # Wait for search results
            
            # Step 7: Click on the Play button in "Top result" card
            # The play button (green circle) appears on the right side of the album art
            print(f"[Spotify] Clicking on Play button in Top Result...")
            try:
                if spotify_windows:
                    # The play button is on the right side of the Top Result card
                    # Approximately 55% from left, 28% from top
                    play_button_x = spotify_window.left + int(spotify_window.width * 0.55)
                    play_button_y = spotify_window.top + int(spotify_window.height * 0.28)
                    
                    # Click on the play button to open song page
                    print(f"[Spotify] Clicking at position ({play_button_x}, {play_button_y})...")
                    pyautogui.click(play_button_x, play_button_y)
                    time.sleep(1.5)  # Wait for song page to load
                    
                    # Step 8: Click the green play button on the song page
                    # This button appears on the left-center area, below the album art
                    print(f"[Spotify] Clicking green play button on song page...")
                    # Green play button is approximately 30% from left, 35% from top
                    song_play_x = spotify_window.left + int(spotify_window.width * 0.30)
                    song_play_y = spotify_window.top + int(spotify_window.height * 0.35)
                    
                    pyautogui.click(song_play_x, song_play_y)
                    time.sleep(0.5)
                    
                    print(f"[Spotify] Song should now be playing!")
                else:
                    # Fallback: just press Space
                    pyautogui.press('space')
            except Exception as e:
                print(f"[Spotify] Click failed: {e}")
                # Fallback to Space key
                pyautogui.press('space')
            
            return f"Playing '{song}' on Spotify"
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"Could not play song on Spotify: {e}"
    
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
    
    # ===== BROWSER AUTOMATION ACTIONS =====
    def open_browser_action(self, headless: bool = False):
        """Open a web browser for automation"""
        try:
            from engine.browser_automation import browser_automation
            
            if browser_automation.is_browser_open():
                return "Browser is already open"
            
            success = browser_automation.initialize_driver(headless=headless)
            if success:
                return "Browser opened successfully"
            else:
                return "Failed to open browser. Make sure Chrome is installed."
        except Exception as e:
            return f"Error opening browser: {e}"
    
    def navigate_to_url_action(self, url: str):
        """Navigate to a URL in the browser"""
        try:
            from engine.browser_automation import browser_automation
            
            if not browser_automation.is_browser_open():
                # Auto-open browser if not open
                browser_automation.initialize_driver()
            
            success = browser_automation.navigate_to(url)
            if success:
                return f"Navigated to {url}"
            else:
                return f"Failed to navigate to {url}"
        except Exception as e:
            return f"Error navigating: {e}"
    
    def click_on_element_action(self, selector: str, by: str = 'css'):
        """Click a web element"""
        try:
            from engine.browser_automation import browser_automation
            
            if not browser_automation.is_browser_open():
                return "Browser is not open. Open browser first."
            
            success = browser_automation.click_element(selector, by)
            if success:
                return f"Clicked element: {selector}"
            else:
                return f"Failed to click element: {selector}"
        except Exception as e:
            return f"Error clicking element: {e}"
    
    def fill_form_field_action(self, selector: str, value: str, by: str = 'css'):
        """Fill a form input field"""
        try:
            from engine.browser_automation import browser_automation
            
            if not browser_automation.is_browser_open():
                return "Browser is not open. Open browser first."
            
            # Try common input selectors if selector is a description
            if ' ' in selector and not selector.startswith('['):
                # Convert description to selector
                # e.g., "search box" -> "input[name*='search'], input[placeholder*='search']"
                selector = f"input[name*='{selector}'], input[placeholder*='{selector}'], input[id*='{selector}']"
            
            success = browser_automation.fill_input(selector, value, by)
            if success:
                return f"Filled field '{selector}' with '{value}'"
            else:
                return f"Failed to fill field: {selector}"
        except Exception as e:
            return f"Error filling field: {e}"
    
    def extract_text_action(self, selector: str, all: bool = False, by: str = 'css'):
        """Extract text from a web element"""
        try:
            from engine.browser_automation import browser_automation
            
            if not browser_automation.is_browser_open():
                return "Browser is not open. Open browser first."
            
            if all:
                texts = browser_automation.get_all_text(selector, by)
                if texts:
                    return f"Found {len(texts)} elements:\n" + "\n".join(texts[:10])
                else:
                    return "No text found"
            else:
                text = browser_automation.get_text(selector, by)
                if text:
                    return f"Text: {text}"
                else:
                    return "No text found"
        except Exception as e:
            return f"Error extracting text: {e}"
    
    def take_page_screenshot_action(self, filename: str = None):
        """Take a screenshot of the current page"""
        try:
            from engine.browser_automation import browser_automation
            
            if not browser_automation.is_browser_open():
                return "Browser is not open. Open browser first."
            
            filepath = browser_automation.take_screenshot(filename)
            if filepath:
                return f"Screenshot saved: {filepath}"
            else:
                return "Failed to take screenshot"
        except Exception as e:
            return f"Error taking screenshot: {e}"
    
    def submit_form_action(self, selector: str = None, by: str = 'css'):
        """Submit a web form"""
        try:
            from engine.browser_automation import browser_automation
            
            if not browser_automation.is_browser_open():
                return "Browser is not open. Open browser first."
            
            success = browser_automation.submit_form(selector, by)
            if success:
                return "Form submitted"
            else:
                return "Failed to submit form"
        except Exception as e:
            return f"Error submitting form: {e}"
    
    def scroll_page_action(self, direction: str = 'down', amount: int = 300):
        """Scroll the page"""
        try:
            from engine.browser_automation import browser_automation
            
            if not browser_automation.is_browser_open():
                return "Browser is not open. Open browser first."
            
            success = browser_automation.scroll_page(direction, amount)
            if success:
                return f"Scrolled {direction}"
            else:
                return "Failed to scroll"
        except Exception as e:
            return f"Error scrolling: {e}"
    
    def close_browser_action(self):
        """Close the web browser"""
        try:
            from engine.browser_automation import browser_automation
            
            if not browser_automation.is_browser_open():
                return "Browser is not open"
            
            success = browser_automation.close_browser()
            if success:
                return "Browser closed"
            else:
                return "Failed to close browser"
        except Exception as e:
            return f"Error closing browser: {e}"

# Global instance
ai_task_agent = AITaskAgent()
