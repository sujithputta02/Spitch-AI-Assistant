"""
Skill Registry - Unified Intent Engine
Acts as the central plugin system for Spitch.
Allows dynamic registration, discovery, and execution of AI skills.
"""
import inspect
from typing import Dict, Any, Callable, List, Optional
import functools

class SkillRegistry:
    def __init__(self):
        self.skills: Dict[str, Dict[str, Any]] = {}
    
    def register_skill(self, name: str, description: str, params: Dict[str, str] = None):
        """
        Decorator to register a function as a skill.
        
        Args:
            name: Unique identifier for the skill (e.g., 'open_app')
            description: Natural language description for the AI prompt
            params: Dictionary describing parameters (e.g., {'app': 'Name of app'})
        """
        def decorator(func: Callable):
            self.skills[name] = {
                'name': name,
                'description': description,
                'params': params or {},
                'func': func,
                'doc': func.__doc__
            }
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def get_skill(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific skill by name"""
        return self.skills.get(name)
    
    def execute_skill(self, name: str, **kwargs) -> Any:
        """Execute a registered skill"""
        skill = self.skills.get(name)
        if not skill:
            raise ValueError(f"Skill '{name}' not found")
        
        try:
            return skill['func'](**kwargs)
        except Exception as e:
            print(f"[SkillRegistry] Execution failed for {name}: {e}")
            raise e
            
    def get_all_skills(self) -> List[Dict[str, Any]]:
        """Return list of all registered skills metadata"""
        return [
            {
                'name': k,
                'description': v['description'],
                'params': v['params']
            }
            for k, v in self.skills.items()
        ]
    
    def generate_system_prompt_snippet(self) -> str:
        """Generate a prompt snippet listing available skills"""
        prompt = "Available Skills (Unified Intent Engine):\n"
        for name, data in self.skills.items():
            param_str = ", ".join([f"{k}: {v}" for k, v in data['params'].items()])
            prompt += f"- {name}({param_str}): {data['description']}\n"
        return prompt

# Global instance
skill_registry = SkillRegistry()
