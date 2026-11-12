import json
import subprocess

def scan_disks():
    """
    Scans physical drives in Windows and identifies their properties,
    bus types (SATA, NVMe, USB), partition letters, and flags the system drive.
    """
    ps_cmd = """
    $sysDrive = $env:SystemDrive
    $disks = Get-Disk | ForEach-Object {
        $disk = $_
        $partitions = Get-Partition -DiskNumber $disk.Number -ErrorAction SilentlyContinue
        $driveLetters = @()
        $isSystem = $false
        foreach ($p in $partitions) {
            if ($p.DriveLetter) {
                $letter = "$($p.DriveLetter):"
                $driveLetters += $letter
                if ($letter -eq $sysDrive) {
                    $isSystem = $true
                }
            }
            if ($p.IsSystem -or $p.IsBoot) {
                $isSystem = $true
            }
        }
        
        [PSCustomObject]@{
            number = [int]$disk.Number
            name = [string]$disk.FriendlyName
            bus_type = [string]$disk.BusType
            size = [int64]$disk.Size
            serial = [string]$disk.SerialNumber
            firmware = [string]$disk.FirmwareVersion
            partition_style = [string]$disk.PartitionStyle
            status = [string]$disk.OperationalStatus
            drive_letters = $driveLetters
            is_system = $isSystem
        }
    }
    $disks | ConvertTo-Json -Depth 3 -Compress
    """
    try:
        res = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd],
            capture_output=True,
            text=True,
            timeout=15,
            check=True
        )
        output = res.stdout.strip()
        if not output:
            return []
        
        data = json.loads(output)
        if isinstance(data, dict):
            disks = [data]
        else:
            disks = data

        for d in disks:
            size_gb = round(d["size"] / (1024 ** 3), 1)
            if size_gb >= 1000:
                d["size_formatted"] = f"{round(size_gb / 1024, 2)} TB"
            else:
                d["size_formatted"] = f"{size_gb} GB"

            # For USB drives, query actual SSD behind the USB bridge (Realtek 0xE4, SAT ATA, JMicron, ASMedia)
            if d.get("bus_type", "").upper() == "USB" or any(k in d.get("name", "").upper() for k in ["REALTEK", "RTL9210", "JMS5", "ASM1", "ASM2"]):
                try:
                    from core.bridge_probe import query_bridge_drive
                    binfo = query_bridge_drive(d["number"])
                    if binfo and not binfo.get("error") and binfo.get("model"):
                        d["bridge_name"] = d.get("name")
                        d["name"] = binfo["model"]
                        if binfo.get("firmware"):
                            d["firmware"] = binfo["firmware"]
                        if binfo.get("serial"):
                            d["serial"] = binfo["serial"]
                        if binfo.get("is_nvme"):
                            d["bus_type"] = "USB (NVMe)"
                        else:
                            d["bus_type"] = "USB (SATA)"
                except Exception as ex:
                    print(f"Bridge probe error for disk {d.get('number')}: {ex}")
        
        # Sort by disk number
        disks.sort(key=lambda x: x["number"])
        return disks
    except Exception as e:
        print(f"Error scanning disks: {e}")
        return []

if __name__ == "__main__":
    disks = scan_disks()
    print(json.dumps(disks, indent=2, ensure_ascii=False))
