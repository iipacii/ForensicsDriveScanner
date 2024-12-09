# backend/app/core/analyzer.py
import os
import hashlib
from datetime import datetime
from pathlib import Path

class FileAnalyzer:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

    def calculate_hashes(self) -> dict:
        try:
            if not self.file_path.exists():
                return {"error": f"File not found: {self.file_path}"}
            
            if not self.file_path.is_file():
                return {"error": f"Not a file: {self.file_path}"}

            md5 = hashlib.md5()
            sha256 = hashlib.sha256()
            
            with open(self.file_path, 'rb') as f:
                # Read in chunks to handle large files
                for chunk in iter(lambda: f.read(65536), b''):
                    md5.update(chunk)
                    sha256.update(chunk)
            
            return {
                "md5": md5.hexdigest(),
                "sha256": sha256.hexdigest()
            }

        except PermissionError as e:
            print(f"Permission denied: {self.file_path}")
            return {"error": f"Permission denied: {e}"}
        except Exception as e:
            print(f"Hash calculation failed for {self.file_path}: {e}")
            return {"error": str(e)}