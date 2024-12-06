import os
import pytsk3
import ctypes
import traceback
import pymft

def get_removable_drives():
    """
    Detects removable drives using ctypes.
    """
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
        print(traceback.format_exc())
    return drives

def scan_ntfs_drive(drive_path):
    """
    Scans an NTFS removable drive and parses the MFT.
    """
    try:
        # Use the pytsk3 Volume_Info to open the raw device
        raw_device_path = f"\\\\.\\{drive_path.rstrip('\\')}"
        print(f"Accessing raw device path: {raw_device_path}...")

        img = pytsk3.Img_Info(raw_device_path)
        fs = pytsk3.FS_Info(img)

        print("MFT entries:")
        for f in fs.open_dir("/"):
            try:
                print(f"File: {f.info.name.name.decode()}, Size: {f.info.meta.size}")
            except AttributeError:
                continue

    except Exception as e:
        print(f"Error scanning drive: {e}")
        print(traceback.format_exc())

def main():
    try:
        drives = get_removable_drives()
        if not drives:
            print("No removable drives detected.")
            return

        print("Detected removable drives:")
        for i, drive in enumerate(drives, 1):
            print(f"{i}. {drive}")
        
        choice = int(input("Select a drive to scan (1/2/...): ")) - 1
        if 0 <= choice < len(drives):
            scan_ntfs_drive(drives[choice])
        else:
            print("Invalid choice. Please select a valid option.")
    except ValueError as ve:
        print(f"ValueError: {ve}. Please enter a valid number for drive selection.")
        print(traceback.format_exc())
    except Exception as e:
        print(f"Unexpected error in main function: {e}")
        print(traceback.format_exc())

if __name__ == "__main__":
    main()
