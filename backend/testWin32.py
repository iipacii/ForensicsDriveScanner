import win32api

try:
    drives = win32api.GetLogicalDriveStrings().split('\000')[:-1]
    for drive in drives:
        print(f"Drive: {drive}, Type: {win32api.GetDriveType(drive)}")
except AttributeError as e:
    print("AttributeError:", e)
except Exception as ex:
    print("An error occurred:", ex)
