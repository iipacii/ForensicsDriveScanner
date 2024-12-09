from pydantic import BaseModel
from typing import Dict, Optional, List, Any

class FileTypeAnalysis(BaseModel):
    is_suspicious: bool
    confidence: str
    reasons: List[str]

class DetectedType(BaseModel):
    extension: str
    mime_type: str 
    description: str

class FileTypeInfo(BaseModel):
    declared_extension: str
    detected_type: DetectedType
    analysis: FileTypeAnalysis

class VirusScanResult(BaseModel):
    data: Optional[Dict] = None
    error: Optional[str] = None
    message: Optional[str] = None

class HashData(BaseModel):
    md5: Optional[str] = None
    sha256: Optional[str] = None
    virus_scan: Optional[VirusScanResult] = None

class HiddenAnalysis(BaseModel):
    is_hidden: bool
    hidden_type: str
    reasons: List[str]
    
class MFTMetadata(BaseModel):
    size: int
    created: str
    modified: str
    accessed: str
    type: str
    flags: str
    file_id: int
    permissions: str
    uid: int
    gid: int
    hidden_status: Optional[HiddenAnalysis] = None
    hashes: Optional[HashData] = None
    file_type: Optional[FileTypeInfo] = None

class ScanResponse(BaseModel):
    status: str
    data: Dict[str, MFTMetadata]