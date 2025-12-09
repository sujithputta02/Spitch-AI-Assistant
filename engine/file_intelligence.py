"""
File Intelligence - Smart file operations and organization

Provides intelligent file management:
- Smart organization by type/date
- Content-based search
- Duplicate detection
- Recent files tracking
- Auto-categorization
"""
import os
import shutil
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import hashlib

class FileIntelligence:
    def __init__(self):
        """Initialize file intelligence"""
        self.recent_files = []
        self.file_categories = {
            'documents': ['.pdf', '.doc', '.docx', '.txt', '.md'],
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'],
            'videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv'],
            'audio': ['.mp3', '.wav', '.flac', '.m4a', '.ogg'],
            'code': ['.py', '.js', '.java', '.cpp', '.c', '.html', '.css'],
            'archives': ['.zip', '.rar', '.7z', '.tar', '.gz']
        }
    
    def get_recent_files(self, directory: str = None, days: int = 7, limit: int = 10) -> List[Dict]:
        """Get recently modified files"""
        if directory is None:
            directory = os.path.expanduser('~')
        
        recent_files = []
        cutoff_time = datetime.now() - timedelta(days=days)
        
        try:
            for root, dirs, files in os.walk(directory):
                # Skip system directories
                if any(skip in root for skip in ['AppData', 'System', 'Windows', '.git']):
                    continue
                
                for file in files:
                    try:
                        filepath = os.path.join(root, file)
                        mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                        
                        if mtime > cutoff_time:
                            recent_files.append({
                                'path': filepath,
                                'name': file,
                                'modified': mtime.isoformat(),
                                'size': os.path.getsize(filepath)
                            })
                    except (OSError, PermissionError):
                        continue
                
                if len(recent_files) >= limit * 2:  # Get more than needed
                    break
        
        except Exception as e:
            print(f"[FileIntelligence] Error scanning files: {e}")
        
        # Sort by modification time and limit
        recent_files.sort(key=lambda x: x['modified'], reverse=True)
        return recent_files[:limit]
    
    def categorize_file(self, filepath: str) -> str:
        """Categorize file by extension"""
        ext = Path(filepath).suffix.lower()
        
        for category, extensions in self.file_categories.items():
            if ext in extensions:
                return category
        
        return 'other'
    
    def organize_files(self, source_dir: str, dest_dir: str = None) -> Dict[str, int]:
        """Organize files by category"""
        if dest_dir is None:
            dest_dir = os.path.join(source_dir, 'Organized')
        
        os.makedirs(dest_dir, exist_ok=True)
        stats = {'moved': 0, 'errors': 0}
        
        try:
            for file in os.listdir(source_dir):
                filepath = os.path.join(source_dir, file)
                
                if os.path.isfile(filepath):
                    category = self.categorize_file(filepath)
                    category_dir = os.path.join(dest_dir, category.capitalize())
                    os.makedirs(category_dir, exist_ok=True)
                    
                    try:
                        shutil.move(filepath, os.path.join(category_dir, file))
                        stats['moved'] += 1
                    except Exception as e:
                        print(f"[FileIntelligence] Error moving {file}: {e}")
                        stats['errors'] += 1
        
        except Exception as e:
            print(f"[FileIntelligence] Error organizing files: {e}")
        
        return stats
    
    def find_duplicates(self, directory: str) -> List[List[str]]:
        """Find duplicate files by content hash"""
        file_hashes = {}
        duplicates = []
        
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    filepath = os.path.join(root, file)
                    
                    try:
                        # Calculate file hash
                        file_hash = self._get_file_hash(filepath)
                        
                        if file_hash in file_hashes:
                            file_hashes[file_hash].append(filepath)
                        else:
                            file_hashes[file_hash] = [filepath]
                    
                    except (OSError, PermissionError):
                        continue
            
            # Find duplicates
            for hash_val, files in file_hashes.items():
                if len(files) > 1:
                    duplicates.append(files)
        
        except Exception as e:
            print(f"[FileIntelligence] Error finding duplicates: {e}")
        
        return duplicates
    
    def _get_file_hash(self, filepath: str, block_size: int = 65536) -> str:
        """Calculate MD5 hash of file"""
        hasher = hashlib.md5()
        
        with open(filepath, 'rb') as f:
            while True:
                data = f.read(block_size)
                if not data:
                    break
                hasher.update(data)
        
        return hasher.hexdigest()
    
    def search_files(self, query: str, directory: str = None, limit: int = 10) -> List[Dict]:
        """Search files by name or content"""
        if directory is None:
            directory = os.path.expanduser('~')
        
        results = []
        query_lower = query.lower()
        
        try:
            for root, dirs, files in os.walk(directory):
                # Skip system directories
                if any(skip in root for skip in ['AppData', 'System', 'Windows']):
                    continue
                
                for file in files:
                    if query_lower in file.lower():
                        filepath = os.path.join(root, file)
                        results.append({
                            'path': filepath,
                            'name': file,
                            'category': self.categorize_file(filepath)
                        })
                        
                        if len(results) >= limit:
                            return results
        
        except Exception as e:
            print(f"[FileIntelligence] Error searching files: {e}")
        
        return results

# Global instance
file_intelligence = FileIntelligence()
