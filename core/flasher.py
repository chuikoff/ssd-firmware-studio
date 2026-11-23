import os
import shutil
import subprocess
import datetime

from core.paths import get_tools_dir, get_output_dir

SUPPORTED_FW_SIZES = (1479168, 1544704, 1547776)

def get_s11_flasher_dir():
    return os.path.join(get_tools_dir(), "phison_s11", "s11-flasher2.15")

class FlasherError(Exception):
    pass

def normalize_header(header_type):
    """Map a UI value to the Toshiba (t), Micron (m) or Micron-new (n) stub."""
    kind = (header_type or "").strip().lower()
    if kind in ("0t", "t", "toshiba", "ts"):
        return "t"
    if kind in ("0m", "m", "micron", "ms"):
        return "m"
    if kind in ("0n", "n", "micron-new", "ns"):
        return "n"
    raise FlasherError(
        "Не задан тип заголовка S11. Выберите Toshiba / Kioxia / Hynix (0t), "
        "Intel / Micron (0m) или новые прошивки Intel / Micron (0n)."
    )

def prepare_phison_s11_flasher(fw_bin_path, header_type="0t"):
    """
    Builds a standalone fw.exe flasher for Phison PS3111-S11
    by joining the binary header, firmware payload, and footer.
    """
    if not os.path.exists(fw_bin_path):
        raise FlasherError(f"Файл прошивки не найден: {fw_bin_path}")
    
    fw_size = os.path.getsize(fw_bin_path)
    if fw_size not in SUPPORTED_FW_SIZES:
        raise FlasherError(
            f"Размер прошивки {fw_size} байт не поддерживается сборщиком S11. "
            "Допустимы только 1479168, 1544704 и 1547776 байт. "
            "Файл не собирается по общему правилу."
        )

    kind = normalize_header(header_type)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = get_output_dir()
    s11_flasher_dir = get_s11_flasher_dir()
    target_dir = os.path.join(output_dir, f"phison_s11_{timestamp}")
    os.makedirs(target_dir, exist_ok=True)
    out_exe = os.path.join(target_dir, "fw.exe")

    # 1479168: short stub + fw.bin + 64k + footer
    # 1544704: long stub + fw.bin + footer
    # 1547776: Seagate image, convert to 1544704 first
    if fw_size == 1479168:
        head_file = {"t": "0ts", "m": "0ms", "n": "0ns"}[kind]
        need_64k = True
    elif fw_size == 1547776:
        convert_exe = os.path.join(s11_flasher_dir, "phison_fw_convert.exe")
        if not os.path.exists(convert_exe):
            raise FlasherError(f"Не найден конвертер Seagate: {convert_exe}")
        staged = os.path.join(target_dir, "fw.bin")
        converted = os.path.join(target_dir, "fwr.bin")
        shutil.copyfile(fw_bin_path, staged)
        subprocess.run([convert_exe, staged, converted], cwd=target_dir, check=False)
        if not os.path.exists(converted) or os.path.getsize(converted) != 1544704:
            raise FlasherError("Конвертация образа Seagate не дала файл размером 1544704 байт.")
        fw_bin_path = converted
        head_file = {"t": "0t", "m": "0m", "n": "0n"}[kind]
        need_64k = False
    else:
        head_file = {"t": "0t", "m": "0m", "n": "0n"}[kind]
        need_64k = False

    head_path = os.path.join(s11_flasher_dir, head_file)
    footer_path = os.path.join(s11_flasher_dir, "2")
    pad_64k_path = os.path.join(s11_flasher_dir, "64k")

    if not os.path.exists(head_path) or not os.path.exists(footer_path):
        raise FlasherError(f"Базовые бинарные компоненты флешера не найдены в {s11_flasher_dir}")
    if need_64k and (not os.path.exists(pad_64k_path) or os.path.getsize(pad_64k_path) != 65536):
        raise FlasherError("Файл 64k не найден или имеет размер, отличный от 65536 байт.")

    # Concatenate binary pieces: head + fw + [64k] + footer
    with open(out_exe, "wb") as out_f:
        with open(head_path, "rb") as h_f:
            out_f.write(h_f.read())
        with open(fw_bin_path, "rb") as fw_f:
            out_f.write(fw_f.read())
        if need_64k and os.path.exists(pad_64k_path):
            with open(pad_64k_path, "rb") as pad_f:
                out_f.write(pad_f.read())
        with open(footer_path, "rb") as foot_f:
            out_f.write(foot_f.read())

    # Copy howto & readme for reference
    for doc in ["s11-flasher2-howto.txt", "s11-flasher2-readme.txt"]:
        doc_src = os.path.join(s11_flasher_dir, doc)
        if os.path.exists(doc_src):
            shutil.copyfile(doc_src, os.path.join(target_dir, doc))

    return {
        "success": True,
        "output_dir": target_dir,
        "flasher_exe": out_exe,
        "fw_used": os.path.basename(fw_bin_path),
        "size_bytes": os.path.getsize(out_exe)
    }

def prepare_mptool_package(pkg_path, vendor="Maxio"):
    """Prepares an MPTool factory package for Maxio or SMI."""
    if not os.path.exists(pkg_path):
        raise FlasherError(f"Файл пакета не найден: {pkg_path}")
        
    output_dir = get_output_dir()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    target_dir = os.path.join(output_dir, f"{vendor.lower()}_mptool_{timestamp}")
    os.makedirs(target_dir, exist_ok=True)
    
    # If it's already an executable
    if pkg_path.lower().endswith(".exe"):
        target_exe = os.path.join(target_dir, os.path.basename(pkg_path))
        shutil.copy2(pkg_path, target_exe)
        return {
            "success": True,
            "output_dir": target_dir,
            "flasher_exe": target_exe,
            "size_bytes": os.path.getsize(target_exe),
            "vendor": vendor
        }
        
    # If it's an archive or directory, copy into target_dir
    dest_file = os.path.join(target_dir, os.path.basename(pkg_path))
    shutil.copy2(pkg_path, dest_file)
    
    # Look for existing exe inside target_dir if extracted
    exe_found = None
    for root, dirs, files in os.walk(target_dir):
        for f in files:
            if f.lower().endswith(".exe") and not any(k in f.lower() for k in ["unins", "setup"]):
                exe_found = os.path.join(root, f)
                break
        if exe_found:
            break

    return {
        "success": True,
        "output_dir": target_dir,
        "flasher_exe": exe_found or dest_file,
        "archive_copied": dest_file,
        "vendor": vendor,
        "message": f"Заводской пакет {vendor} MPTool подготовлен в: {target_dir}"
    }

def prepare_flasher(fw_path, header_type="0t", vendor="Phison", controller="", filename=""):
    """
    Unified flasher preparation for Phison, SMI, and Maxio.
    """
    vendor_name = vendor or "Phison"
    source = fw_path or ""

    if source.startswith("http://") or source.startswith("https://"):
        raise FlasherError("Прошивка берётся только из локальной папки firmware. Ссылки на сайты не используются.")

    if not os.path.exists(source):
        raise FlasherError(f"Локальный файл прошивки не найден: {source}")

    lowered = source.lower()
    if vendor_name.lower() == "maxio" or "mas0902" in lowered or "maxio" in lowered:
        return prepare_mptool_package(source, vendor="Maxio")

    if vendor_name.lower() == "silicon motion" or "smi" in lowered or "sm225" in lowered:
        return prepare_mptool_package(source, vendor="SMI")

    return prepare_phison_s11_flasher(source, header_type=header_type)

def execute_flasher(exe_path, disk_number=None):
    """
    Launches the flasher executable with elevation and returns process info.
    """
    if not os.path.exists(exe_path):
        raise FlasherError(f"Исполняемый файл не найден: {exe_path}")

    workdir = os.path.dirname(exe_path)
    
    # If user selected an archive, open folder in Explorer
    if exe_path.lower().endswith((".rar", ".zip", ".7z")):
        os.startfile(workdir)
        return {"success": True, "message": f"Открыта папка с архивом {os.path.basename(exe_path)}. Распакуйте и запустите MPTool."}

    import ctypes
    ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", exe_path, None, workdir, 1)
    if ret > 32:
        return {"success": True, "message": f"Прошивальщик {os.path.basename(exe_path)} запущен с правами Администратора."}

    last_err = ctypes.GetLastError()
    # 5 = Access Denied / 1223 = ERROR_CANCELLED (user clicked "No" on UAC prompt)
    if ret == 5 or last_err in (5, 1223):
        return {"success": False, "message": "Запуск прошивальщика отменен пользователем (UAC)."}

    clean_exe = exe_path.replace("'", "''")
    clean_workdir = workdir.replace("'", "''")
    ps_cmd = f"Start-Process -FilePath '{clean_exe}' -WorkingDirectory '{clean_workdir}' -Verb RunAs"
    subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], check=True)
    return {"success": True, "message": f"Прошивальщик {os.path.basename(exe_path)} запущен с правами Администратора."}
