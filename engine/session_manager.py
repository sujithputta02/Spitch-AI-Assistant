"""
Session Manager - Tracks conversation history and context

Provides JARVIS-level memory and context awareness by:
- Storing conversation history
- Tracking session context
- Enabling pronoun resolution
- Maintaining conversation flow
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import deque

class SessionManager:
    def __init__(self, max_history: int = 20):
        """Initialize session manager with conversation history"""
        self.max_history = max_history
        self.conversation_history = deque(maxlen=max_history)
        self.current_session_id = self._generate_session_id()
        self.session_start_time = datetime.now()
        self.context = {}  # Current session context
        
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def add_interaction(self, user_input: str, assistant_response: str, 
                       intent: Optional[Dict] = None, success: bool = True):
        """Add an interaction to conversation history"""
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'assistant_response': assistant_response,
            'intent': intent,
            'success': success
        }
        
        self.conversation_history.append(interaction)
        self._update_context(interaction)
    
    def _update_context(self, interaction: Dict):
        """Update session context based on interaction"""
        # Extract entities from the interaction
        if interaction.get('intent'):
            entities = interaction['intent'].get('entities', {})
            
            # Store last mentioned entities for pronoun resolution
            if 'app' in entities:
                self.context['last_app'] = entities['app']
            if 'file_path' in entities:
                self.context['last_file'] = entities['file_path']
            if 'url' in entities:
                self.context['last_url'] = entities['url']
            if 'expression' in entities:
                self.context['last_calculation'] = entities['expression']
    
    def get_recent_history(self, n: int = 5) -> List[Dict]:
        """Get last N interactions"""
        history_list = list(self.conversation_history)
        return history_list[-n:] if len(history_list) >= n else history_list
    
    def get_context_for_prompt(self) -> str:
        """Generate context string for AI prompts"""
        if not self.conversation_history:
            return ""
        
        recent = self.get_recent_history(3)
        context_lines = []
        
        for interaction in recent:
            context_lines.append(f"User: {interaction['user_input']}")
            context_lines.append(f"Assistant: {interaction['assistant_response']}")
        
        return "\n".join(context_lines)
    
    def resolve_pronoun(self, user_input: str) -> str:
        """Resolve pronouns like 'it', 'that', 'this' to actual entities"""
        resolved = user_input.lower()
        
        # Resolve "it" or "that" to last mentioned entity
        if any(word in resolved for word in ['it', 'that', 'this']):
            # Check what was last mentioned
            if 'last_app' in self.context:
                resolved = resolved.replace('it', self.context['last_app'])
                resolved = resolved.replace('that', self.context['last_app'])
                resolved = resolved.replace('this', self.context['last_app'])
            elif 'last_file' in self.context:
                resolved = resolved.replace('it', self.context['last_file'])
                resolved = resolved.replace('that', self.context['last_file'])
                resolved = resolved.replace('this', self.context['last_file'])
        
        return resolved
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session"""
        return {
            'session_id': self.current_session_id,
            'start_time': self.session_start_time.isoformat(),
            'duration_minutes': (datetime.now() - self.session_start_time).total_seconds() / 60,
            'total_interactions': len(self.conversation_history),
            'context': self.context
        }
    
    def save_session(self, filepath: str = "sessions/current_session.json"):
        """Save session to file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        session_data = {
            'session_id': self.current_session_id,
            'start_time': self.session_start_time.isoformat(),
            'conversation_history': list(self.conversation_history),
            'context': self.context
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
    
    def load_session(self, filepath: str = "sessions/current_session.json"):
        """Load session from file"""
        if not os.path.exists(filepath):
            return False
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            self.current_session_id = session_data['session_id']
            self.session_start_time = datetime.fromisoformat(session_data['start_time'])
            self.conversation_history = deque(session_data['conversation_history'], maxlen=self.max_history)
            self.context = session_data['context']
            
            return True
        except Exception as e:
            print(f"[SessionManager] Error loading session: {e}")
            return False

# Global instance
session_manager = SessionManager()
