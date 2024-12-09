from pydantic import BaseModel
from typing import Dict, Optional, List

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
    hashes: Optional[Dict[str, str]]

class ScanResponse(BaseModel):
    status: str 
    data: Dict[str, MFTMetadata]