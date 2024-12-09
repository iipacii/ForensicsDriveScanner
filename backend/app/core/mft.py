# app/core/mft.py
import pytsk3
from datetime import datetime
import logging


logger = logging.getLogger("api.mft")

def convert_timestamp(timestamp):
    if timestamp == 0:
        return "N/A"
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def convert_file_type(file_type):
    types = {
        pytsk3.TSK_FS_META_TYPE_REG: "File",
        pytsk3.TSK_FS_META_TYPE_DIR: "Directory",
        pytsk3.TSK_FS_META_TYPE_LNK: "Symbolic Link",
        pytsk3.TSK_FS_META_TYPE_SOCK: "Socket",
        pytsk3.TSK_FS_META_TYPE_FIFO: "FIFO",
        pytsk3.TSK_FS_META_TYPE_CHR: "Character Device",
        pytsk3.TSK_FS_META_TYPE_BLK: "Block Device",
        pytsk3.TSK_FS_META_TYPE_SHAD: "Shadow File",
        pytsk3.TSK_FS_META_TYPE_WHT: "Whiteout File",
        pytsk3.TSK_FS_META_TYPE_VIRT: "Virtual File",
        pytsk3.TSK_FS_META_TYPE_UNDEF: "Undefined",
    }
    return types.get(file_type, "Unknown")

def convert_flags(flags):
    flag_descriptions = []
    if flags & pytsk3.TSK_FS_META_FLAG_ALLOC:
        flag_descriptions.append("Allocated")
    if flags & pytsk3.TSK_FS_META_FLAG_UNALLOC:
        flag_descriptions.append("Unallocated")
    if flags & pytsk3.TSK_FS_META_FLAG_USED:
        flag_descriptions.append("Used")
    if flags & pytsk3.TSK_FS_META_FLAG_UNUSED:
        flag_descriptions.append("Unused")
    if flags & pytsk3.TSK_FS_META_FLAG_COMP:
        flag_descriptions.append("Compressed")
    if flags & pytsk3.TSK_FS_META_FLAG_ORPHAN:
        flag_descriptions.append("Orphan")
    return ", ".join(flag_descriptions) if flag_descriptions else "None"

def convert_permissions(permissions):
    return oct(permissions)

def scan_directory(fs, directory_path="/"):
    files = {}
    try:
        directory = fs.open_dir(directory_path)
        for entry in directory:
            try:
                # Skip . and .. entries
                name = entry.info.name.name.decode('utf-8')
                if name in [".", ".."]:
                    continue
                    
                full_path = f"{directory_path}/{name}".replace("//", "/")
                
                metadata = {
                    "size": entry.info.meta.size,
                    "created": convert_timestamp(entry.info.meta.crtime),
                    "modified": convert_timestamp(entry.info.meta.mtime),
                    "accessed": convert_timestamp(entry.info.meta.atime),
                    "type": convert_file_type(entry.info.meta.type),
                    "flags": convert_flags(entry.info.meta.flags),
                    "file_id": entry.info.meta.addr,
                    "permissions": convert_permissions(entry.info.meta.mode),
                    "uid": entry.info.meta.uid,
                    "gid": entry.info.meta.gid,
                }
                
                files[full_path] = metadata
                
                # Recursively scan subdirectories
                if entry.info.meta.type == pytsk3.TSK_FS_META_TYPE_DIR:
                    sub_files = scan_directory(fs, full_path)
                    files.update(sub_files)
                    
            except AttributeError as ae:
                logger.error(f"AttributeError reading entry", exc_info=True)
                continue
                
        return files
    except Exception as e:
        logger.error(f"Error scanning directory {directory_path}: {e}")
        return files

def scan_mft(drive_path):
    try:
        raw_device_path = f"\\\\.\\{drive_path.rstrip('\\')}"
        img = pytsk3.Img_Info(raw_device_path)
        fs = pytsk3.FS_Info(img)
        return scan_directory(fs)
    except Exception as e:
        return {"error": str(e)}