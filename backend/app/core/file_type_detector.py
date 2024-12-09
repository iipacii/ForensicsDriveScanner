# backend/app/core/file_type_detector.py
from pathlib import Path
from typing import Dict
from dataclasses import dataclass
from mimetypes import guess_type

@dataclass
class FileSignature:
    extension: str
    mime_type: str
    description: str

class FileTypeDetector:
    SIGNATURES = {
        b'\x50\x4B\x03\x04': FileSignature('zip', 'application/zip', 'ZIP Archive'),
        b'\x25\x50\x44\x46': FileSignature('pdf', 'application/pdf', 'PDF Document'),
        b'\xFF\xD8\xFF': FileSignature('jpg', 'image/jpeg', 'JPEG Image'),
        b'\x89\x50\x4E\x47': FileSignature('png', 'image/png', 'PNG Image'),
        b'\x4D\x5A': FileSignature('exe', 'application/x-msdownload', 'Windows Executable'),
        b'\x7F\x45\x4C\x46': FileSignature('elf', 'application/x-executable', 'Linux Executable'),
        b'\x52\x61\x72\x21': FileSignature('rar', 'application/x-rar-compressed', 'RAR Archive'),
        b'\x47\x49\x46\x38': FileSignature('gif', 'image/gif', 'GIF Image')
    }

    def analyze_file(self, file_path: str) -> Dict:
        path = Path(file_path)
        
        # Default response structure that matches schema
        default_response = {
            "declared_extension": "unknown",
            "detected_type": {
                "extension": "unknown",
                "mime_type": "unknown",
                "description": "Unknown Format"
            },
            "analysis": {
                "is_suspicious": False,
                "confidence": "none",
                "reasons": []
            }
        }

        try:
            with open(path, 'rb') as f:
                header = f.read(8)
                file_size = path.stat().st_size

            declared_ext = path.suffix.lower().lstrip('.')
            if not declared_ext:
                declared_ext = "unknown"

            # Find actual type from signature
            actual_sig = None
            for signature, file_type in self.SIGNATURES.items():
                if header.startswith(signature):
                    actual_sig = file_type
                    break

            suspicion_info = self._check_suspicion(header, file_size, declared_ext, actual_sig)

            return {
                "declared_extension": declared_ext,
                "detected_type": {
                    "extension": actual_sig.extension if actual_sig else "unknown",
                    "mime_type": actual_sig.mime_type if actual_sig else "unknown",
                    "description": actual_sig.description if actual_sig else "Unknown Format"
                },
                "analysis": {
                    "is_suspicious": bool(suspicion_info["reasons"]),
                    "confidence": suspicion_info["confidence"],
                    "reasons": suspicion_info["reasons"]
                }
            }

        except FileNotFoundError:
            default_response["analysis"]["reasons"].append("File not found")
            return default_response
        except PermissionError:
            default_response["analysis"]["reasons"].append("Access denied")
            return default_response
        except Exception as e:
            default_response["analysis"]["reasons"].append(f"Error analyzing file: {str(e)}")
            return default_response

    def _check_suspicion(self, header: bytes, file_size: int, 
                        declared_ext: str, actual_sig: FileSignature) -> Dict:
        reasons = []
        
        if not actual_sig:
            reasons.append("No known file signature detected")
        
        if header.startswith(b'\x00' * 3):
            reasons.append("File starts with null bytes")
            
        if file_size < 100 and declared_ext in ['exe', 'dll']:
            reasons.append("Suspiciously small executable")
            
        if actual_sig and declared_ext != actual_sig.extension:
            reasons.append(f"Extension mismatch: claims {declared_ext} but detected {actual_sig.extension}")

        return {
            "is_suspicious": bool(reasons),
            "confidence": "high" if actual_sig else "low",
            "reasons": reasons
        }