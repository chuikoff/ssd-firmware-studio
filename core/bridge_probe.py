import ctypes
import ctypes.wintypes
import struct
import json
import os
import sys

# Windows IOCTLs
IOCTL_SCSI_PASS_THROUGH = 0x0004D004
IOCTL_SCSI_PASS_THROUGH_DIRECT = 0x0004D014
IOCTL_STORAGE_QUERY_PROPERTY = 0x002D1400

GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
FILE_SHARE_READ = 1
FILE_SHARE_WRITE = 2
OPEN_EXISTING = 3

class SCSI_PASS_THROUGH(ctypes.Structure):
    _fields_ = [
        ('Length', ctypes.c_ushort),
        ('ScsiStatus', ctypes.c_ubyte),
        ('PathId', ctypes.c_ubyte),
        ('TargetId', ctypes.c_ubyte),
        ('Lun', ctypes.c_ubyte),
        ('CdbLength', ctypes.c_ubyte),
        ('SenseInfoLength', ctypes.c_ubyte),
        ('DataIn', ctypes.c_ubyte),
        ('DataTransferLength', ctypes.c_ulong),
        ('TimeOutValue', ctypes.c_ulong),
        ('DataBufferOffset', ctypes.c_size_t),
        ('SenseInfoOffset', ctypes.c_ulong),
        ('Cdb', ctypes.c_ubyte * 16),
    ]

class SPT_BUF_4K(ctypes.Structure):
    _fields_ = [
        ('spt', SCSI_PASS_THROUGH),
        ('SenseBuf', ctypes.c_ubyte * 32),
        ('DataBuf', ctypes.c_ubyte * 4096),
    ]

class SPT_BUF_512(ctypes.Structure):
    _fields_ = [
        ('spt', SCSI_PASS_THROUGH),
        ('SenseBuf', ctypes.c_ubyte * 32),
        ('DataBuf', ctypes.c_ubyte * 512),
    ]

def swap_ata_string(b):
    """Swap every pair of bytes in ATA string (standard ATA endianness)"""
    res = bytearray()
    for i in range(0, len(b) - 1, 2):
        res.append(b[i + 1])
        res.append(b[i])
    if len(b) % 2 == 1:
        res.append(b[-1])
    return res.decode('latin1', errors='replace').strip()

def probe_realtek_nvme(h):
    """Realtek RTL9210 NVMe identify via SCSI vendor opcode 0xE4 (CNS=1)"""
    buf = SPT_BUF_4K()
    buf.spt.Length = ctypes.sizeof(SCSI_PASS_THROUGH)
    buf.spt.CdbLength = 16
    buf.spt.DataIn = 1 # SCSI_IOCTL_DATA_IN
    buf.spt.DataTransferLength = 4096
    buf.spt.TimeOutValue = 8
    buf.spt.SenseInfoLength = 32
    buf.spt.SenseInfoOffset = SPT_BUF_4K.SenseBuf.offset
    buf.spt.DataBufferOffset = SPT_BUF_4K.DataBuf.offset

    buf.spt.Cdb[0] = 0xE4 # Realtek NVMe Read
    buf.spt.Cdb[1] = 4096 & 0xFF
    buf.spt.Cdb[2] = (4096 >> 8) & 0xFF
    buf.spt.Cdb[3] = 0x06 # Identify
    buf.spt.Cdb[4] = 0x01 # CNS = 1

    ret_bytes = ctypes.wintypes.DWORD(0)
    ok = ctypes.windll.kernel32.DeviceIoControl(
        h, IOCTL_SCSI_PASS_THROUGH,
        ctypes.byref(buf), ctypes.sizeof(buf),
        ctypes.byref(buf), ctypes.sizeof(buf),
        ctypes.byref(ret_bytes), None
    )
    if ok and buf.spt.ScsiStatus == 0:
        data = bytes(buf.DataBuf)
        if any(b != 0 for b in data[:64]):
            sn = data[4:24].decode('latin1', errors='replace').strip()
            model = data[24:64].decode('latin1', errors='replace').strip()
            fw = data[64:72].decode('latin1', errors='replace').strip()
            if model:
                return {
                    "protocol": "Realtek_0xE4_NVMe",
                    "model": model,
                    "firmware": fw,
                    "serial": sn,
                    "is_nvme": True
                }
    return None

def probe_sat_ata(h):
    """SAT ATA Identify (Opcode 0x85 / 0xA1) for SATA SSDs behind USB bridges"""
    for is_16 in [True, False]:
        buf = SPT_BUF_512()
        buf.spt.Length = ctypes.sizeof(SCSI_PASS_THROUGH)
        buf.spt.CdbLength = 16 if is_16 else 12
        buf.spt.DataIn = 1
        buf.spt.DataTransferLength = 512
        buf.spt.TimeOutValue = 8
        buf.spt.SenseInfoLength = 32
        buf.spt.SenseInfoOffset = SPT_BUF_512.SenseBuf.offset
        buf.spt.DataBufferOffset = SPT_BUF_512.DataBuf.offset

        if is_16:
            buf.spt.Cdb[0] = 0x85 # SAT ATA PASS THROUGH 16
            buf.spt.Cdb[1] = (4 << 1) # PIO Data-In
            buf.spt.Cdb[2] = 0x0E # T_DIR=1, BYTE_BLOCK=1, T_LENGTH=2 (sectors)
            buf.spt.Cdb[6] = 1    # Sector count
            buf.spt.Cdb[13] = 0xA0 # Device
            buf.spt.Cdb[14] = 0xEC # IDENTIFY DEVICE
        else:
            buf.spt.Cdb[0] = 0xA1 # SAT ATA PASS THROUGH 12
            buf.spt.Cdb[1] = (4 << 1) # PIO Data-In
            buf.spt.Cdb[2] = 0x0E
            buf.spt.Cdb[4] = 1    # Sector count
            buf.spt.Cdb[8] = 0xA0 # Device
            buf.spt.Cdb[9] = 0xEC # IDENTIFY DEVICE

        ret_bytes = ctypes.wintypes.DWORD(0)
        in_len = SPT_BUF_512.DataBuf.offset + 512
        ok = ctypes.windll.kernel32.DeviceIoControl(
            h, IOCTL_SCSI_PASS_THROUGH,
            ctypes.byref(buf), in_len,
            ctypes.byref(buf), ctypes.sizeof(buf),
            ctypes.byref(ret_bytes), None
        )
        if ok and buf.spt.ScsiStatus == 0:
            data = bytes(buf.DataBuf)
            if any(b != 0 for b in data[:64]):
                sn = swap_ata_string(data[20:40])
                fw = swap_ata_string(data[46:54])
                model = swap_ata_string(data[54:94])
                if model:
                    return {
                        "protocol": f"SAT_{16 if is_16 else 12}_ATA",
                        "model": model,
                        "firmware": fw,
                        "serial": sn,
                        "is_nvme": False
                    }
    return None

def probe_jmicron_nvme(h):
    """JMicron JMS583/586 NVMe identify via SCSI opcode 0xA1"""
    buf = SPT_BUF_4K()
    buf.spt.Length = ctypes.sizeof(SCSI_PASS_THROUGH)
    buf.spt.CdbLength = 12
    buf.spt.DataIn = 1
    buf.spt.DataTransferLength = 4096
    buf.spt.TimeOutValue = 8
    buf.spt.SenseInfoLength = 32
    buf.spt.SenseInfoOffset = SPT_BUF_4K.SenseBuf.offset
    buf.spt.DataBufferOffset = SPT_BUF_4K.DataBuf.offset

    buf.spt.Cdb[0] = 0xA1 # JMicron NVMe Pass Through
    buf.spt.Cdb[1] = 0x06 # Identify
    buf.spt.Cdb[2] = 0x01 # CNS = 1
    buf.spt.Cdb[8] = (4096 >> 8) & 0xFF
    buf.spt.Cdb[9] = 4096 & 0xFF

    ret_bytes = ctypes.wintypes.DWORD(0)
    ok = ctypes.windll.kernel32.DeviceIoControl(
        h, IOCTL_SCSI_PASS_THROUGH,
        ctypes.byref(buf), ctypes.sizeof(buf),
        ctypes.byref(buf), ctypes.sizeof(buf),
        ctypes.byref(ret_bytes), None
    )
    if ok and buf.spt.ScsiStatus == 0:
        data = bytes(buf.DataBuf)
        if any(b != 0 for b in data[:64]):
            sn = data[4:24].decode('latin1', errors='replace').strip()
            model = data[24:64].decode('latin1', errors='replace').strip()
            fw = data[64:72].decode('latin1', errors='replace').strip()
            if model:
                return {
                    "protocol": "JMicron_0xA1_NVMe",
                    "model": model,
                    "firmware": fw,
                    "serial": sn,
                    "is_nvme": True
                }
    return None

def probe_asmedia_nvme(h):
    """ASMedia ASM2362 NVMe identify via SCSI opcode 0xE6"""
    buf = SPT_BUF_4K()
    buf.spt.Length = ctypes.sizeof(SCSI_PASS_THROUGH)
    buf.spt.CdbLength = 16
    buf.spt.DataIn = 1
    buf.spt.DataTransferLength = 4096
    buf.spt.TimeOutValue = 8
    buf.spt.SenseInfoLength = 32
    buf.spt.SenseInfoOffset = SPT_BUF_4K.SenseBuf.offset
    buf.spt.DataBufferOffset = SPT_BUF_4K.DataBuf.offset

    buf.spt.Cdb[0] = 0xE6 # ASMedia NVMe Pass Through
    buf.spt.Cdb[1] = 0x01 # CNS = 1
    buf.spt.Cdb[2] = 0x06 # Identify
    buf.spt.Cdb[8] = (4096 >> 8) & 0xFF
    buf.spt.Cdb[9] = 4096 & 0xFF

    ret_bytes = ctypes.wintypes.DWORD(0)
    ok = ctypes.windll.kernel32.DeviceIoControl(
        h, IOCTL_SCSI_PASS_THROUGH,
        ctypes.byref(buf), ctypes.sizeof(buf),
        ctypes.byref(buf), ctypes.sizeof(buf),
        ctypes.byref(ret_bytes), None
    )
    if ok and buf.spt.ScsiStatus == 0:
        data = bytes(buf.DataBuf)
        if any(b != 0 for b in data[:64]):
            sn = data[4:24].decode('latin1', errors='replace').strip()
            model = data[24:64].decode('latin1', errors='replace').strip()
            fw = data[64:72].decode('latin1', errors='replace').strip()
            if model:
                return {
                    "protocol": "ASMedia_0xE6_NVMe",
                    "model": model,
                    "firmware": fw,
                    "serial": sn,
                    "is_nvme": True
                }
    return None

def probe_bridge_drive(disk_number):
    """
    Attempts all SCSI Pass-Through protocols (Realtek, SAT ATA, JMicron, ASMedia)
    to query the actual SSD behind the USB bridge.
    """
    dev_path = f"\\\\.\\PhysicalDrive{disk_number}"
    h = ctypes.windll.kernel32.CreateFileW(
        dev_path,
        GENERIC_READ | GENERIC_WRITE,
        FILE_SHARE_READ | FILE_SHARE_WRITE,
        None,
        OPEN_EXISTING,
        0,
        None
    )
    if h == -1 or h == 0xFFFFFFFFFFFFFFFF:
        return {"error": f"CreateFile failed (Err {ctypes.windll.kernel32.GetLastError()})"}

    try:
        # 1. SAT ATA (common for SATA SSDs in RTL9210B dual enclosures)
        res = probe_sat_ata(h)
        if res:
            return res

        # 2. Realtek NVMe 0xE4 (for NVMe SSDs in RTL9210 enclosures)
        res = probe_realtek_nvme(h)
        if res:
            return res

        # 3. JMicron JMS583 NVMe 0xA1
        res = probe_jmicron_nvme(h)
        if res:
            return res

        # 4. ASMedia ASM2362 NVMe 0xE6
        res = probe_asmedia_nvme(h)
        if res:
            return res

        return None
    finally:
        ctypes.windll.kernel32.CloseHandle(h)

def _is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def query_bridge_drive(disk_number):
    """
    Main entry point. If running as admin, probes directly.
    A frozen exe must not relaunch itself: that opens a second copy of the GUI.
    From source, an unelevated call elevates this script via PowerShell.
    """
    from core.paths import is_frozen

    if _is_admin() or is_frozen():
        result = probe_bridge_drive(disk_number)
        if is_frozen() and not _is_admin():
            if not isinstance(result, dict):
                return {"error": "Нужны права администратора для опроса USB-моста."}
            if result.get("error"):
                result["error"] = "Нужны права администратора для опроса USB-моста. " + str(result["error"])
            elif not result.get("model"):
                return {"error": "Нужны права администратора для опроса USB-моста."}
        return result

    import tempfile, subprocess
    temp_json = os.path.join(tempfile.gettempdir(), f"bridge_probe_{disk_number}_{os.getpid()}.json")
    if os.path.exists(temp_json):
        try:
            os.remove(temp_json)
        except OSError:
            pass

    script_path = os.path.abspath(__file__)
    py_exe = sys.executable

    ps_cmd = f"Start-Process -FilePath '{py_exe}' -ArgumentList '\"{script_path}\" {disk_number} \"{temp_json}\"' -Verb RunAs -WindowStyle Hidden -Wait"
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True,
            timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        if os.path.exists(temp_json):
            with open(temp_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            try:
                os.remove(temp_json)
            except OSError:
                pass
            return data
    except Exception:
        pass

    return probe_bridge_drive(disk_number)

if __name__ == "__main__":
    disk_num = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    out_file = sys.argv[2] if len(sys.argv) > 2 else None
    result = probe_bridge_drive(disk_num)
    if out_file:
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps(result, ensure_ascii=False, indent=2))

