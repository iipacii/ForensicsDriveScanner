from fastapi import APIRouter, HTTPException
from ..core.scanner import get_removable_drives
from ..core.mft import scan_mft
from ..core.analyzer import FileAnalyzer
from ..models.schemas import ScanResponse

router = APIRouter()

@router.get("/drives")
async def list_drives():
    drives = get_removable_drives()
    if not drives:
        raise HTTPException(status_code=404, detail="No removable drives detected")
    return drives

@router.get("/scan", response_model=ScanResponse)
async def scan_drive(drive: str):
    try:
        # Get MFT data
        mft_data = scan_mft(drive)
        
        # Add hashes for each file
        for filename, metadata in mft_data.items():
            try:
                analyzer = FileAnalyzer(f"{drive}{filename}")
                metadata["hashes"] = analyzer.calculate_hashes()
            except:
                metadata["hashes"] = None
                
        return {
            "status": "success",
            "data": mft_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))