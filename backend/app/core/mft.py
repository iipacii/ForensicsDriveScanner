# app/core/mft.py
import pytsk3
from datetime import datetime

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

def scan_mft(drive_path):
    try:
        raw_device_path = f"\\\\.\\{drive_path.rstrip('\\')}"
        img = pytsk3.Img_Info(raw_device_path)
        fs = pytsk3.FS_Info(img)

        files = {}
        for entry in fs.open_dir("/"):
            try:
                if entry.info.name.name:
                    filename = entry.info.name.name.decode('utf-8')
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
                    files[filename] = metadata
            except AttributeError:
                continue

        return files

    except Exception as e:
        return {"error": str(e)}