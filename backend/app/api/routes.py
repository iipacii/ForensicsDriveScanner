import logging
from ..core.virus_scanner import VirusScanner
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

# routes.py modifications
@router.get("/scan", response_model=ScanResponse)
async def scan_drive(drive: str):
    logger = logging.getLogger("api.scan")
    logger.info(f"Starting scan for drive: {drive}")
    
    try:
        mft_data = scan_mft(drive)
        logger.info(f"MFT scan completed for drive {drive}")
        
        virus_scanner = None
        try:
            virus_scanner = VirusScanner()
        except Exception as e:
            logger.error(f"Failed to initialize VirusScanner: {e}")
        
        total_files = len(mft_data)
        processed = 0
        
        for filename, metadata in mft_data.items():
            processed += 1
            logger.info(f"Processing file {processed}/{total_files}: {filename}")
            
            if (filename.startswith('$') or 
                filename in ['.', 'System Volume Information'] or
                metadata['type'] == 'Directory'):
                logger.debug(f"Skipping system file/directory: {filename}")
                metadata["hashes"] = {"md5": None, "sha256": None}
                continue

            try:
                analyzer = FileAnalyzer(f"{drive}{filename}")
                hash_result = analyzer.calculate_hashes()
                
                if "error" in hash_result:
                    logger.error(f"Hash calculation error for {filename}: {hash_result['error']}")
                    metadata["hashes"] = {"md5": None, "sha256": None}
                else:
                    if virus_scanner and hash_result.get("sha256"):
                        try:
                            logger.info(f"Scanning file: {filename} with hash: {hash_result['sha256']}")
                            scan_result = virus_scanner.check_hash(hash_result["sha256"])
                            hash_result["virus_scan"] = scan_result
                            logger.info(f"Scan completed for {filename}: {scan_result['message']}")
                        except Exception as e:
                            logger.error(f"Virus scan failed for {filename}: {e}")
                            hash_result["virus_scan"] = None
                            
                    metadata["hashes"] = hash_result
                    
            except Exception as e:
                logger.error(f"Failed to analyze {filename}: {str(e)}")
                metadata["hashes"] = {"md5": None, "sha256": None}
        
        logger.info(f"Scan completed for drive {drive}")
        return {
            "status": "success",
            "data": mft_data
        }
        
    except Exception as e:
        logger.exception(f"Scan failed for drive {drive}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))