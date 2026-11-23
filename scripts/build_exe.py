import os
import sys
import subprocess
import shutil

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(BASE_DIR)

print("=== Building SSD Firmware Studio Standalone EXE ===")

excludes = [
    "numpy", "matplotlib", "PIL", "IPython", "jedi", "pandas", "scipy",
    "tkinter", "PySide6", "PyQt5", "PyQt6", "pytest", "notebook", "zmq",
    "cv2", "sklearn", "torch", "tensorflow",
]
cmd = [
    sys.executable,
    "-m",
    "PyInstaller",
    "--name=SSD_Firmware_Studio",
    "--onedir",
    "--uac-admin",
    "--noconsole",
    "--noupx",
    "--add-data", f"{os.path.join(BASE_DIR, 'ui')};ui",
    "--add-data", f"{os.path.join(BASE_DIR, 'tools_and_fw_catalog.json')};.",
    "--hidden-import=re",
    "--hidden-import=re._constants",
    "--hidden-import=token",
    "--hidden-import=tokenize",
    "--hidden-import=webview",
    "--hidden-import=bottle",
    "--hidden-import=proxy_tools",
    "--hidden-import=pythonnet",
    "--hidden-import=clr",
    "--distpath", os.path.join(BASE_DIR, "dist_package"),
    "--clean",
    "-y",
    "app.py",
]
cmd.extend(f"--exclude-module={name}" for name in excludes)

print("Running PyInstaller...")
res = subprocess.run(cmd, cwd=BASE_DIR)

if res.returncode == 0:
    dist_dir = os.path.join(BASE_DIR, "dist_package", "SSD_Firmware_Studio")
    print(f"\n[OK] Build successful! Dist folder: {dist_dir}")
    
    # Copy tools and firmware folders and catalog into dist_package so it is 100% standalone
    for folder in ["tools", "firmware", "output"]:
        src = os.path.join(BASE_DIR, folder)
        dst = os.path.join(dist_dir, folder)
        if os.path.exists(src) and not os.path.exists(dst):
            print(f"Copying {folder} to dist package...")
            shutil.copytree(src, dst)
            
    cat_src = os.path.join(BASE_DIR, "tools_and_fw_catalog.json")
    cat_dst = os.path.join(dist_dir, "tools_and_fw_catalog.json")
    if os.path.exists(cat_src):
        shutil.copy2(cat_src, cat_dst)
            
    final_exe = os.path.join(dist_dir, "SSD_Firmware_Studio.exe")
    print(f"\n[READY] Standalone executable: {final_exe}")
    
    # Replace the exe the user launches. Keep tools, firmware and output already next to it.
    legacy_dist = os.path.join(BASE_DIR, "dist", "SSD_Firmware_Studio")
    os.makedirs(legacy_dist, exist_ok=True)
    shutil.copy2(final_exe, os.path.join(legacy_dist, "SSD_Firmware_Studio.exe"))
    legacy_internal = os.path.join(legacy_dist, "_internal")
    new_internal = os.path.join(dist_dir, "_internal")
    if os.path.isdir(legacy_internal):
        shutil.rmtree(legacy_internal)
    shutil.copytree(new_internal, legacy_internal)
    shutil.copy2(cat_src, os.path.join(legacy_dist, "tools_and_fw_catalog.json"))
    print(f"[SYNC] Updated exe and runtime at: {legacy_dist}")
else:
    print(f"\n[ERROR] PyInstaller failed with code {res.returncode}")
