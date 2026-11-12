import os
import sys

def is_frozen():
    return getattr(sys, 'frozen', False)

def get_base_dir():
    if is_frozen():
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def get_bundle_dir():
    if is_frozen() and hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return get_base_dir()

def _resolve_dir(name):
    # Prefer folder next to exe if present, else bundled
    exe_path = os.path.join(get_base_dir(), name)
    if os.path.exists(exe_path):
        return exe_path
    bundle_path = os.path.join(get_bundle_dir(), name)
    return bundle_path if os.path.exists(bundle_path) else exe_path

def get_ui_dir():
    return _resolve_dir("ui")

def get_tools_dir():
    return _resolve_dir("tools")

def get_firmware_dir():
    return _resolve_dir("firmware")

def get_output_dir():
    out = os.path.join(get_base_dir(), "output")
    os.makedirs(out, exist_ok=True)
    return out

def get_catalog_path():
    return _resolve_dir("tools_and_fw_catalog.json")
