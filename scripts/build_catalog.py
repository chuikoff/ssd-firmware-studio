import urllib.request
import re
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

pages = {
    "smi_flash_id": "https://www.usbdev.ru/files/smi/smiflashid/",
    "smi_nvme_flash_id": "https://www.usbdev.ru/files/smi/sminvmeflashid/",
    "phison_flash_id": "https://www.usbdev.ru/files/phison/phisonflashid/",
    "phison_s11_flasher": "https://www.usbdev.ru/files/phison/phisons11flasher/",
    "phison_e7_flash_id": "https://www.usbdev.ru/files/phison/phisone7flashid/",
    "maxio_flash_id": "https://www.usbdev.ru/files/jmicron/jmfid/",
    "maxio_nvme_flash_id": "https://www.usbdev.ru/files/maxio/maxionvmefid/",
    "maxio_mas0902_mptool": "https://www.usbdev.ru/files/maxio/mas0902mas0901mptool/",
    "smi_sm2258xt_mptool": "https://www.usbdev.ru/files/smi/sm2258xtmptool/",
    "smi_sm2259xt_mptool": "https://www.usbdev.ru/files/smi/sm2259xtmptool/",
    "phison_ps3111_mptool": "https://www.usbdev.ru/files/phison/ps3111ssdmptool/"
}

results = {}

for name, url in pages.items():
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode('utf-8', errors='ignore')
            # Look for ?wpfb_dl= pattern
            downloads = re.findall(r'<a[^>]+href=["\'](https?://www\.usbdev\.ru/\?wpfb_dl=\d+)["\'][^>]*>(.*?)</a>', html, re.I | re.DOTALL)
            items = []
            for dl_url, label in downloads:
                clean_label = re.sub(r'<[^<]+?>', '', label).strip()
                items.append({'url': dl_url, 'label': clean_label})
            results[name] = items
            print(f"[{name}] found {len(items)} downloads. Latest: {items[-1] if items else 'None'}")
    except Exception as e:
        print(f"[{name}] Error: {e}")

with open("tools_and_fw_catalog.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print("Saved to tools_and_fw_catalog.json")
