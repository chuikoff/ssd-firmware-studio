import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

import urllib.request
import json
import threading
import time
import uvicorn

def run_test():
    base_url = "http://127.0.0.1:8000"
    print("\n--- 1. Testing GET /api/disks ---")
    req = urllib.request.Request(f"{base_url}/api/disks")
    with urllib.request.urlopen(req, timeout=10) as r:
        data = json.loads(r.read().decode('utf-8'))
        print(f"Disks count: {len(data['disks'])}")
        for d in data['disks']:
            print(f"  * Disk {d['number']}: {d['name']} ({d['size_formatted']}, {d['bus_type']}) [System: {d['is_system']}]")

    print("\n--- 2. Testing POST /api/firmwares ---")
    payload = json.dumps({
        "detection": {
            "controller": "PS3111-S11",
            "flash_desc": "Toshiba BiCS3 64L TLC",
            "fw_version": "SBFG61.2"
        }
    }).encode('utf-8')
    req = urllib.request.Request(f"{base_url}/api/firmwares", data=payload, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=10) as r:
        data = json.loads(r.read().decode('utf-8'))
        fw_list = data.get('firmwares', [])
        print(f"Matched firmwares count: {len(fw_list)}")
        for f in fw_list[:3]:
            print(f"  * [{f.get('badge')}] {f['filename']} ({f['size_str']}) -> {f.get('target_nand')}")

    print("\n--- 3. Testing Static UI Assets ---")
    for path in ["/", "/style.css", "/app.js"]:
        req = urllib.request.Request(f"{base_url}{path}")
        with urllib.request.urlopen(req, timeout=5) as r:
            print(f"Asset {path}: HTTP {r.status}, Length: {len(r.read())}")

    print("\n[ALL TESTS PASSED SUCCESSFULLY!]")

if __name__ == "__main__":
    from server import app
    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="error")
    server = uvicorn.Server(config)
    
    t = threading.Thread(target=server.run, daemon=True)
    t.start()
    time.sleep(1.5)
    
    try:
        run_test()
    finally:
        server.should_exit = True
