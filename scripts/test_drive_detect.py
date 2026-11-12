import subprocess
import os
import sys

tools_dir = os.path.abspath("tools")
smi_usb = os.path.join(tools_dir, "smi", "smi_flash_id-v0.569a", "smi_flash_id_usb.exe")
smi_ata = os.path.join(tools_dir, "smi", "smi_flash_id-v0.569a", "smi_flash_id_ata.exe")
smi_nvme = os.path.join(tools_dir, "smi_nvme", "smi_nvme_flash_id-0.275a", "smi_nvme_flash_id.exe")
phison_ata = os.path.join(tools_dir, "phison", "phison_flash_id845", "phison_flash_id.exe")
maxio_ata = os.path.join(tools_dir, "maxio", "jm_fid-0.271a", "jm_fid.exe")

def test_tool(tool_path, target_drive, extra="y"):
    if not os.path.exists(tool_path):
        print(f"Tool not found: {tool_path}")
        return
    print(f"\n--- Testing {os.path.basename(tool_path)} on drive {target_drive} ---")
    workdir = os.path.dirname(tool_path)
    cmd = [tool_path, f"{target_drive}{extra}"]
    try:
        res = subprocess.run(cmd, cwd=workdir, capture_output=True, timeout=8, text=False)
        stdout = res.stdout.decode('cp1251', errors='replace')
        stderr = res.stderr.decode('cp1251', errors='replace')
        print("STDOUT:")
        print(stdout[:1000])
        # Also check if a .txt log was generated in workdir
        for f in os.listdir(workdir):
            if f.endswith(".txt") and "history" not in f and "readme" not in f and "howto" not in f:
                txt_path = os.path.join(workdir, f)
                with open(txt_path, 'rb') as tf:
                    print(f"FILE {f}:")
                    print(tf.read().decode('cp1251', errors='replace')[:1500])
    except Exception as e:
        print(f"Execution error: {e}")

# Let's test drive 3 (USB SSD) with SMI USB, Phison, and Maxio
test_tool(smi_usb, 3)
test_tool(phison_ata, 3)
test_tool(maxio_ata, 3)
