import os
import stat
import ctypes
from pathlib import Path
from typing import Dict

class HiddenDetector:
    def __init__(self):
        self.FILE_ATTRIBUTE_HIDDEN = 0x2
        self.FILE_ATTRIBUTE_SYSTEM = 0x4
        
    def analyze_file(self, file_path: str) -> Dict:
        try:
            path = Path(file_path)
            
            # Get Windows file attributes
            attrs = ctypes.windll.kernel32.GetFileAttributesW(str(path))
            
            if attrs == -1:  # Invalid handle
                return {
                    "is_hidden": False,
                    "hidden_type": "none",
                    "reasons": ["Unable to get file attributes"]
                }

            reasons = []
            hidden_type = "none"

            # Check Windows hidden attribute
            if attrs & self.FILE_ATTRIBUTE_HIDDEN:
                reasons.append("Windows hidden attribute set")
                hidden_type = "windows_hidden"

            # Check Windows system attribute
            if attrs & self.FILE_ATTRIBUTE_SYSTEM:
                reasons.append("Windows system attribute set")
                hidden_type = "windows_system"

            # Check if name starts with dot (Unix-style hidden)
            if path.name.startswith('.'):
                reasons.append("Filename starts with dot")
                hidden_type = "unix_hidden"

            return {
                "is_hidden": bool(reasons),
                "hidden_type": hidden_type,
                "reasons": reasons
            }

        except Exception as e:
            return {
                "is_hidden": False,
                "hidden_type": "none",
                "reasons": [f"Error analyzing file: {str(e)}"]
            }