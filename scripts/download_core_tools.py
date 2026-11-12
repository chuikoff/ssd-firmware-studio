import os
import json
import urllib.request
import subprocess

seven_zip = r"C:\Program Files\7-Zip\7z.exe"
tools_dir = os.path.abspath("tools")
os.makedirs(tools_dir, exist_ok=True)

with open("tools_and_fw_catalog.json", "r", encoding="utf-8") as f:
    catalog = json.load(f)

targets = [
    ("smi_flash_id", catalog.get("smi_flash_id", [])[-1]["url"], "https://www.usbdev.ru/files/smi/smiflashid/", "smi_flash_id.rar", "smi"),
    ("smi_nvme_flash_id", catalog.get("smi_nvme_flash_id", [])[-1]["url"], "https://www.usbdev.ru/files/smi/sminvmeflashid/", "smi_nvme_flash_id.rar", "smi_nvme"),
    ("phison_flash_id", catalog.get("phison_flash_id", [])[-1]["url"], "https://www.usbdev.ru/files/phison/phisonflashid/", "phison_flash_id.rar", "phison"),
    ("phison_s11_flasher", catalog.get("phison_s11_flasher", [])[-1]["url"], "https://www.usbdev.ru/files/phison/phisons11flasher/", "s11_flasher.rar", "phison_s11"),
    ("maxio_flash_id", catalog.get("maxio_flash_id", [])[-1]["url"], "https://www.usbdev.ru/files/jmicron/jmfid/", "jm_fid.rar", "maxio"),
    ("maxio_nvme_flash_id", catalog.get("maxio_nvme_flash_id", [])[-1]["url"], "https://www.usbdev.ru/files/maxio/maxionvmefid/", "maxio_nvme_fid.rar", "maxio_nvme")
]

for name, url, referer, archive_name, extract_folder in targets:
    archive_path = os.path.join(tools_dir, archive_name)
    extract_path = os.path.join(tools_dir, extract_folder)
    print(f"\nDownloading {name} from {url} (Referer: {referer})...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': referer
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
            with open(archive_path, "wb") as out_f:
                out_f.write(data)
            print(f"Downloaded {len(data)} bytes -> {archive_path}")
        
        # Check if it starts with Rar! or 7z or PK
        if data.startswith(b'Rar!') or data.startswith(b'7z') or data.startswith(b'PK'):
            os.makedirs(extract_path, exist_ok=True)
            res = subprocess.run([seven_zip, "x", archive_path, f"-o{extract_path}", "-y"], capture_output=True, text=True)
            if res.returncode == 0:
                print(f"Successfully extracted to {extract_path}")
            else:
                print(f"Extract error: {res.stderr}")
        else:
            print(f"Warning: File header is not an archive: {data[:20]}")
    except Exception as e:
        print(f"Failed {name}: {e}")

print("\n--- Summary of executable tools in tools/ ---")
for root, dirs, files in os.walk(tools_dir):
    for file in files:
        if file.endswith(".exe"):
            print("  *", os.path.relpath(os.path.join(root, file), tools_dir))
