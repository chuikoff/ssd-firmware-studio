import urllib.request
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

targets = [
    ("SMI Flash ID", "https://www.usbdev.ru/files/smi/smiflashid/"),
    ("Phison Flash ID", "https://www.usbdev.ru/files/phison/phisonflashid/"),
    ("Maxio/JM Flash ID", "https://www.usbdev.ru/files/jmicron/jmfid/"),
    ("Phison S11 Flasher", "https://www.usbdev.ru/files/phison/phisons11flasher/"),
    ("Maxio NVMe FID", "https://www.usbdev.ru/files/maxio/maxionvmefid/")
]

for name, url in targets:
    print(f"\nTarget: {name} ({url})")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode('utf-8', errors='ignore')
            # Look for download links ending in .rar, .zip, .7z
            files = re.findall(r'href=["\']([^"\']+\.(?:rar|zip|7z|exe))["\']', html, re.I)
            for f in set(files):
                print(f"  -> File: {f}")
    except Exception as e:
        print(f"  Error: {e}")
