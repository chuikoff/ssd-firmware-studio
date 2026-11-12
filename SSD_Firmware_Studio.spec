# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[('C:/Users/chuik/.gemini/antigravity-ide/scratch/ssd-flasher-gui/ui', 'ui'), ('C:/Users/chuik/.gemini/antigravity-ide/scratch/ssd-flasher-gui/tools_and_fw_catalog.json', '.')],
    hiddenimports=['webview', 'bottle', 'proxy_tools', 'pythonnet', 'clr'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['numpy', 'matplotlib', 'PIL', 'IPython', 'jedi', 'pandas', 'scipy', 'tkinter', 'PySide6', 'PyQt5', 'PyQt6', 'pytest', 'notebook', 'zmq', 'cv2', 'sklearn', 'torch', 'tensorflow'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SSD_Firmware_Studio',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=True,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='SSD_Firmware_Studio',
)
