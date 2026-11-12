import urllib.request
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def check_section(section_name, url):
    print(f"\n=== {section_name}: {url} ===")
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode('utf-8', errors='ignore')
            links = re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html, re.I | re.DOTALL)
            found = 0
            for href, text in links:
                clean_text = re.sub(r'<[^<]+?>', '', text).strip()
                if any(k in href.lower() or k in clean_text.lower() for k in ['flash_id', 'mptool', 'sm2258', 'sm2259', 'ps3111', 'mas0902', 'vlo', 'flasher']):
                    if clean_text:
                        print(f"  * {clean_text[:50]} -> {href}")
                        found += 1
                        if found >= 15:
                            break
    except Exception as e:
        print(f"Error checking {url}: {e}")

check_section("SMI", "https://www.usbdev.ru/files/smi/")
check_section("Phison", "https://www.usbdev.ru/files/phison/")
check_section("Maxio", "https://www.usbdev.ru/files/maxio/")
