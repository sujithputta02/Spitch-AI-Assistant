"""
Pattern Tracker - Learns user habits and patterns

Analyzes user behavior to:
- Identify time-based routines
- Track command sequences
- Recognize app usage patterns
- Predict next actions
"""
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict, Counter

class PatternTracker:
    def __init__(self, patterns_file: str = "memory/patterns.json"):
        """Initialize pattern tracker"""
        self.patterns_file = patterns_file
        self.patterns = {
            'time_based': defaultdict(list),  # {hour: [commands]}
            'sequences': [],  # [{commands: [...], count: N}]
            'app_by_time': defaultdict(Counter),  # {hour: Counter(apps)}
            'day_of_week': defaultdict(list),  # {day: [commands]}
        }
        self.load_patterns()
    
    def load_patterns(self):
        """Load patterns from file"""
        if os.path.exists(self.patterns_file):
            try:
                with open(self.patterns_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Convert back to defaultdict and Counter
                    self.patterns['time_based'] = defaultdict(list, loaded.get('time_based', {}))
                    self.patterns['sequences'] = loaded.get('sequences', [])
                    
                    app_by_time = loaded.get('app_by_time', {})
                    self.patterns['app_by_time'] = defaultdict(
                        Counter,
                        {k: Counter(v) for k, v in app_by_time.items()}
                    )
                    
                    self.patterns['day_of_week'] = defaultdict(list, loaded.get('day_of_week', {}))
                    
                print(f"[PatternTracker] Loaded patterns from {self.patterns_file}")
            except Exception as e:
                print(f"[PatternTracker] Error loading patterns: {e}")
    
    def save_patterns(self):
        """Save patterns to file"""
        os.makedirs(os.path.dirname(self.patterns_file), exist_ok=True)
        
        save_data = {
            'time_based': dict(self.patterns['time_based']),
            'sequences': self.patterns['sequences'],
            'app_by_time': {k: dict(v) for k, v in self.patterns['app_by_time'].items()},
            'day_of_week': dict(self.patterns['day_of_week'])
        }
        
        with open(self.patterns_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
    
    def track_command(self, command: str, intent: Dict = None):
        """Track a command execution for pattern analysis"""
        now = datetime.now()
        hour = str(now.hour)
        day = now.strftime('%A')  # Monday, Tuesday, etc.
        
        # Track by time of day
        self.patterns['time_based'][hour].append({
            'command': command,
            'timestamp': now.isoformat()
        })
        
        # Track by day of week
        self.patterns['day_of_week'][day].append({
            'command': command,
            'timestamp': now.isoformat()
        })
        
        # Track app usage by time
        if intent and 'app' in intent.get('entities', {}):
            app = intent['entities']['app']
            self.patterns['app_by_time'][hour][app] += 1
        
        self.save_patterns()
    
    def get_common_commands_for_time(self, hour: Optional[int] = None) -> List[str]:
        """Get most common commands for a specific hour"""
        if hour is None:
            hour = datetime.now().hour
        
        hour_str = str(hour)
        commands = self.patterns['time_based'].get(hour_str, [])
        
        if not commands:
            return []
        
        # Count command frequencies
        command_counts = Counter([cmd['command'] for cmd in commands])
        return [cmd for cmd, count in command_counts.most_common(3)]
    
    def get_preferred_apps_for_time(self, hour: Optional[int] = None) -> List[tuple]:
        """Get preferred apps for a specific hour"""
        if hour is None:
            hour = datetime.now().hour
        
        hour_str = str(hour)
        app_counter = self.patterns['app_by_time'].get(hour_str, Counter())
        
        return app_counter.most_common(3)
    
    def predict_next_action(self, recent_commands: List[str]) -> Optional[str]:
        """Predict next action based on command sequences"""
        # Simple prediction: look for common sequences
        # This is a basic implementation
        
        if len(recent_commands) < 2:
            return None
        
        # Check if recent commands match any known sequences
        # For now, return None (can be enhanced)
        return None
    
    def get_routine_summary(self) -> Dict[str, Any]:
        """Get summary of user routines"""
        summary = {
            'total_tracked_hours': len(self.patterns['time_based']),
            'most_active_hour': None,
            'most_active_day': None,
            'top_apps': []
        }
        
        # Find most active hour
        hour_counts = {h: len(cmds) for h, cmds in self.patterns['time_based'].items()}
        if hour_counts:
            most_active_hour = max(hour_counts, key=hour_counts.get)
            summary['most_active_hour'] = f"{most_active_hour}:00"
        
        # Find most active day
        day_counts = {d: len(cmds) for d, cmds in self.patterns['day_of_week'].items()}
        if day_counts:
            summary['most_active_day'] = max(day_counts, key=day_counts.get)
        
        # Get top apps across all times
        all_apps = Counter()
        for hour_apps in self.patterns['app_by_time'].values():
            all_apps.update(hour_apps)
        summary['top_apps'] = all_apps.most_common(5)
        
        return summary

# Global instance
pattern_tracker = PatternTracker()
