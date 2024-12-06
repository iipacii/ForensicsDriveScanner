from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mft_parser import get_removable_drives, scan_mft

app = FastAPI()

class ScanResponse(BaseModel):
    status: str
    data: dict

@app.get("/drives", response_model=list)
def list_drives():
    try:
        drives = get_removable_drives()
        if not drives:
            raise HTTPException(status_code=404, detail="No removable drives detected.")
        return drives
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scan", response_model=ScanResponse)
def scan_drive(drive: str):
    try:
        files = scan_mft(drive)
        if "error" in files:
            raise HTTPException(status_code=500, detail=files["error"])
        return ScanResponse(status="success", data=files)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
