"""
Proactive Assistant - JARVIS-Level Anticipation and Suggestions

Provides proactive assistance by:
- Monitoring system health
- Suggesting actions based on patterns
- Anticipating user needs
- Providing contextual recommendations
"""
import psutil
import os
from datetime import datetime, time
from typing import List, Dict, Any, Optional

class ProactiveAssistant:
    def __init__(self):
        """Initialize proactive assistant"""
        self.suggestions_enabled = True
        self.monitoring_enabled = True
        
    def get_time_of_day(self) -> str:
        """Get current time period"""
        current_hour = datetime.now().hour
        
        if 5 <= current_hour < 12:
            return "morning"
        elif 12 <= current_hour < 17:
            return "afternoon"
        elif 17 <= current_hour < 21:
            return "evening"
        else:
            return "night"
    
    def get_proactive_suggestions(self, context: Dict = None) -> List[str]:
        """
        Get proactive suggestions based on context and patterns
        
        Returns list of suggestion strings
        """
        suggestions = []
        
        try:
            from engine.memory_bank import memory_bank
            
            time_period = self.get_time_of_day()
            
            # Time-based suggestions
            if time_period == "morning":
                suggestions.extend(self._get_morning_suggestions(memory_bank))
            elif time_period == "afternoon":
                suggestions.extend(self._get_afternoon_suggestions(memory_bank))
            elif time_period == "evening":
                suggestions.extend(self._get_evening_suggestions(memory_bank))
            
            # System health suggestions
            health_suggestions = self._get_system_health_suggestions()
            suggestions.extend(health_suggestions)
            
            # Pattern-based suggestions
            pattern_suggestions = self._get_pattern_suggestions(memory_bank, context)
            suggestions.extend(pattern_suggestions)
            
        except Exception as e:
            print(f"[ProactiveAssistant] Error getting suggestions: {e}")
        
        return suggestions[:3]  # Return top 3 suggestions
    
    def _get_morning_suggestions(self, memory_bank) -> List[str]:
        """Get morning-specific suggestions"""
        suggestions = []
        
        # Check most used morning apps
        most_used = memory_bank.get_most_used_apps(5)
        if most_used:
            top_app = most_used[0][0]
            if most_used[0][1] > 3:  # Used more than 3 times
                suggestions.append(f"Good morning! Would you like me to open {top_app}?")
        
        return suggestions
    
    def _get_afternoon_suggestions(self, memory_bank) -> List[str]:
        """Get afternoon-specific suggestions"""
        suggestions = []
        
        # Suggest productivity apps
        current_hour = datetime.now().hour
        if 14 <= current_hour < 15:
            suggestions.append("It's 2 PM. Time for a productivity boost?")
        
        return suggestions
    
    def _get_evening_suggestions(self, memory_bank) -> List[str]:
        """Get evening-specific suggestions"""
        suggestions = []
        
        # Suggest winding down
        current_hour = datetime.now().hour
        if 20 <= current_hour < 21:
            suggestions.append("Evening time. Would you like me to help you wrap up?")
        
        return suggestions
    
    def _get_system_health_suggestions(self) -> List[str]:
        """Monitor system and suggest actions"""
        suggestions = []
        
        try:
            # Check disk space
            disk = psutil.disk_usage('/')
            if disk.percent > 90:
                suggestions.append(f"⚠️ Disk space is {disk.percent}% full. Should I help clean up?")
            elif disk.percent > 80:
                suggestions.append(f"Disk space is {disk.percent}% full. Consider cleanup soon.")
            
            # Check memory
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                suggestions.append(f"⚠️ Memory usage is {memory.percent}%. Close some apps?")
            
            # Check CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 90:
                suggestions.append(f"⚠️ CPU usage is {cpu_percent}%. System may be slow.")
            
        except Exception as e:
            print(f"[ProactiveAssistant] System monitoring error: {e}")
        
        return suggestions
    
    def _get_pattern_suggestions(self, memory_bank, context: Dict = None) -> List[str]:
        """Get suggestions based on learned patterns"""
        suggestions = []
        
        try:
            # Check for frequent command patterns
            if context and 'last_command' in context:
                # Suggest related commands
                pass
            
            # Check for file location patterns
            known_files = len(memory_bank.memory.get('file_locations', {}))
            if known_files > 0:
                # Could suggest opening recent files
                pass
            
        except Exception as e:
            print(f"[ProactiveAssistant] Pattern analysis error: {e}")
        
        return suggestions
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'time_of_day': self.get_time_of_day(),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"[ProactiveAssistant] Error getting system status: {e}")
            return {}
    
    def should_suggest_now(self) -> bool:
        """Determine if it's appropriate to make suggestions"""
        if not self.suggestions_enabled:
            return False
        
        # Don't suggest too frequently
        # Could track last suggestion time here
        
        return True
    
    def format_suggestion(self, suggestion: str) -> str:
        """Format suggestion for display"""
        return f"💡 {suggestion}"

# Global instance
proactive_assistant = ProactiveAssistant()
