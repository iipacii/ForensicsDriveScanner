from pydantic import BaseModel
from typing import Dict, Optional, List

class VirusScanResult(BaseModel):
    data: Optional[Dict] = None
    error: Optional[str] = None
    message: Optional[str] = None

class HashData(BaseModel):
    md5: Optional[str] = None
    sha256: Optional[str] = None
    virus_scan: Optional[VirusScanResult] = None

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
    hashes: Optional[HashData] = None

class ScanResponse(BaseModel):
    status: str
    data: Dict[str, MFTMetadata]