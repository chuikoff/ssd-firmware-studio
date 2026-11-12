import urllib.request
import urllib.parse
import re
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

candidates = [
    'https://www.usbdev.ru/files/smi/',
    'https://www.usbdev.ru/files/phison/',
    'https://www.usbdev.ru/files/maxio/',
    'http://vlo.moy.su/index/ssd_tools/0-12',
    'https://github.com/search?q=smi_flash_id&type=repositories',
    'https://github.com/search?q=phison_flash_id&type=repositories'
]

for url in candidates:
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            print(f"[OK] {url} -> {resp.status}")
    except Exception as e:
        print(f"[ERR] {url} -> {e}")
