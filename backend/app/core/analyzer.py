import os
import hashlib
from datetime import datetime
from pathlib import Path

class FileAnalyzer:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
    
    def get_metadata(self) -> dict:
        try:
            stat = os.stat(self.file_path)
            return {
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
                "hashes": self.calculate_hashes()
            }
        except Exception as e:
            return {"error": str(e)}

    def calculate_hashes(self) -> dict:
        try:
            md5 = hashlib.md5()
            sha256 = hashlib.sha256()
            
            with open(self.file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(65536), b''):
                    md5.update(chunk)
                    sha256.update(chunk)
                    
            return {
                "md5": md5.hexdigest(),
                "sha256": sha256.hexdigest()
            }
        except Exception as e:
            return {"error": str(e)}