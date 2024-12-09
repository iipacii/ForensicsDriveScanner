import ctypes
from typing import List

def get_removable_drives() -> List[str]:
    DRIVE_REMOVABLE = 2
    drives = []
    
    try:
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            if bitmask & 1:
                drive = f"{letter}:\\"
                drive_type = ctypes.windll.kernel32.GetDriveTypeW(ctypes.c_wchar_p(drive))
                if drive_type == DRIVE_REMOVABLE:
                    drives.append(drive)
            bitmask >>= 1
    except Exception as e:
        print(f"Error detecting drives: {e}")
    return drives