"""
Memory Bank - Learns from user interactions and improves over time

Provides JARVIS-level learning by:
- Tracking command success rates
- Learning user preferences
- Remembering patterns
- Adapting responses
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from collections import defaultdict, Counter

class MemoryBank:
    def __init__(self, memory_file: str = "memory/memory_bank.json"):
        """Initialize memory bank"""
        self.memory_file = memory_file
        self.memory = {
            'user_preferences': {},
            'command_patterns': defaultdict(int),
            'successful_commands': [],
            'failed_commands': [],
            'app_usage': Counter(),
            'file_locations': {},
            'learned_patterns': [],
            'feedback_history': []
        }
        self.load_memory()
    
    def load_memory(self):
        """Load memory from file"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self.memory.update(loaded)
                    # Convert back to Counter and defaultdict
                    self.memory['app_usage'] = Counter(self.memory.get('app_usage', {}))
                    self.memory['command_patterns'] = defaultdict(int, self.memory.get('command_patterns', {}))
                print(f"[MemoryBank] Loaded memory from {self.memory_file}")
            except Exception as e:
                print(f"[MemoryBank] Error loading memory: {e}")
    
    def save_memory(self):
        """Save memory to file"""
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        
        # Convert Counter and defaultdict to regular dict for JSON
        save_data = {
            'user_preferences': self.memory['user_preferences'],
            'command_patterns': dict(self.memory['command_patterns']),
            'successful_commands': self.memory['successful_commands'][-100:],  # Keep last 100
            'failed_commands': self.memory['failed_commands'][-100:],
            'app_usage': dict(self.memory['app_usage']),
            'file_locations': self.memory['file_locations'],
            'learned_patterns': self.memory['learned_patterns'],
            'feedback_history': self.memory['feedback_history'][-50:]  # Keep last 50
        }
        
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
    
    def record_command(self, command: str, intent: Dict, success: bool):
        """Record a command execution"""
        record = {
            'timestamp': datetime.now().isoformat(),
            'command': command,
            'intent': intent,
            'success': success
        }
        
        if success:
            self.memory['successful_commands'].append(record)
            # Increment pattern count
            pattern_key = f"{intent.get('intent', 'unknown')}"
            self.memory['command_patterns'][pattern_key] += 1
        else:
            self.memory['failed_commands'].append(record)
        
        # Track app usage
        if 'app' in intent.get('entities', {}):
            app = intent['entities']['app']
            self.memory['app_usage'][app] += 1
        
        self.save_memory()
    
    def learn_preference(self, preference_type: str, value: Any):
        """Learn a user preference"""
        self.memory['user_preferences'][preference_type] = value
        self.save_memory()
    
    def get_preference(self, preference_type: str, default: Any = None) -> Any:
        """Get a learned preference"""
        return self.memory['user_preferences'].get(preference_type, default)
    
    def get_most_used_apps(self, n: int = 5) -> List[tuple]:
        """Get most frequently used applications"""
        return self.memory['app_usage'].most_common(n)
    
    def get_command_success_rate(self, intent_type: str) -> float:
        """Get success rate for a specific intent type"""
        successful = sum(1 for cmd in self.memory['successful_commands'] 
                        if cmd['intent'].get('intent') == intent_type)
        failed = sum(1 for cmd in self.memory['failed_commands'] 
                    if cmd['intent'].get('intent') == intent_type)
        
        total = successful + failed
        return successful / total if total > 0 else 0.0
    
    def remember_file_location(self, filename: str, path: str):
        """Remember where a file is located"""
        self.memory['file_locations'][filename] = path
        self.save_memory()
    
    def get_file_location(self, filename: str) -> Optional[str]:
        """Get remembered file location"""
        return self.memory['file_locations'].get(filename)
    
    def add_feedback(self, command: str, feedback: str, rating: int):
        """Add user feedback for learning"""
        feedback_record = {
            'timestamp': datetime.now().isoformat(),
            'command': command,
            'feedback': feedback,
            'rating': rating  # 1-5
        }
        self.memory['feedback_history'].append(feedback_record)
        self.save_memory()
    
    def get_suggestions_for_context(self, context: Dict) -> List[str]:
        """Get suggestions based on current context and learned patterns"""
        suggestions = []
        
        # Suggest most used apps
        if context.get('time_of_day') == 'morning':
            top_apps = self.get_most_used_apps(3)
            for app, count in top_apps:
                if count > 5:  # Only suggest if used frequently
                    suggestions.append(f"Open {app}?")
        
        return suggestions
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get summary of learned memory"""
        return {
            'total_successful_commands': len(self.memory['successful_commands']),
            'total_failed_commands': len(self.memory['failed_commands']),
            'most_used_apps': self.get_most_used_apps(5),
            'learned_preferences': len(self.memory['user_preferences']),
            'known_file_locations': len(self.memory['file_locations']),
            'feedback_count': len(self.memory['feedback_history'])
        }

# Global instance
memory_bank = MemoryBank()
