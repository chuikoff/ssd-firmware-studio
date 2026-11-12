import os
import re
import subprocess
import time

from core.paths import get_tools_dir

def get_tools_map():
    tools_dir = get_tools_dir()
    return {
        "smi_ata": os.path.join(tools_dir, "smi", "smi_flash_id-v0.569a", "smi_flash_id_ata.exe"),
        "smi_usb": os.path.join(tools_dir, "smi", "smi_flash_id-v0.569a", "smi_flash_id_usb.exe"),
        "smi_nvme": os.path.join(tools_dir, "smi_nvme", "smi_nvme_flash_id-0.275a", "smi_nvme_flash_id.exe"),
        "phison": os.path.join(tools_dir, "phison", "phison_flash_id845", "phison_flash_id.exe"),
        "maxio": os.path.join(tools_dir, "maxio", "jm_fid-0.271a", "jm_fid.exe"),
        "maxio_nvme": os.path.join(tools_dir, "maxio_nvme", "maxio_nvme_fid-0.382a", "maxio_nvme_fid.exe"),
    }

def _is_admin():
    """Check if the current process has Administrator privileges."""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def run_elevated_tool(tool_path, arg_str, workdir, timeout_sec=8):
    """
    Executes a hardware utility.
    If running as admin, runs directly. Otherwise elevates via PowerShell Start-Process -Verb RunAs.
    """
    if _is_admin():
        try:
            cmd = [tool_path, arg_str]
            res = subprocess.run(
                cmd,
                cwd=workdir,
                capture_output=True,
                timeout=timeout_sec,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            return True, res.stdout.decode('cp1251', errors='replace')
        except subprocess.TimeoutExpired:
            return False, "Timeout waiting for utility response"
        except Exception as e:
            return False, str(e)
    else:
        # Not admin — must elevate via RunAs
        ps_cmd = f"Start-Process -FilePath '{tool_path}' -ArgumentList '{arg_str}' -WorkingDirectory '{workdir}' -Verb RunAs -WindowStyle Hidden -Wait"
        try:
            subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd],
                capture_output=True,
                timeout=timeout_sec + 4,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            return True, "Executed elevated"
        except subprocess.TimeoutExpired:
            return False, "Timeout waiting for elevated utility response"
        except Exception as ps_err:
            return False, str(ps_err)

def _extract_flash_info(text):
    """Unified FID and Flash description extractor across SMI, Phison, and Maxio."""
    clean = text.replace('\r\n', '\n')
    fid = None
    desc = None

    # Line format: FlashID: 0xad,0x5e... - Hynix 3dv4...
    m = re.search(r'^(?:Flash\s*ID|FlashID|FID)\s*:\s*([0-9a-fxA-FX,\s]+?)(?:\s*-\s*(.+))?$', clean, re.M | re.I)
    if m:
        fid = m.group(1).strip()
        if m.group(2):
            desc = m.group(2).strip()

    if not fid:
        alt = re.search(r'(?:Flash\s*ID|FlashID|FID)\s*:\s*([0-9a-fxA-FX,\s]+)', clean, re.I)
        if alt:
            fid = alt.group(1).strip()

    if not desc:
        dm = re.search(r'^(?:FlashCE|Flash)\s*:\s*(.*)', clean, re.M | re.I)
        if dm:
            desc = dm.group(1).strip()

    return fid, desc

def parse_smi_report(text):
    """Parses output from smi_flash_id or smi_nvme_flash_id"""
    if any(k in text for k in ["Compatible SSD not found", "SSD not found", "Drive not found"]):
        return None
    
    result = {
        "vendor": "Silicon Motion",
        "controller": None,
        "flash_id": None,
        "flash_desc": None,
        "nand_part": None,
        "fw_version": None,
        "raw": text
    }

    # Search controller (handling 'bufferless' -> XT and SMART codes)
    smart_match = re.search(r'From smart\s*:\s*\[([A-Za-z0-9]+)\]', text, re.I)
    ctrl_match = re.search(r'Controller\s*:\s*([^\r\n]+)', text, re.I)
    upper_text = text.upper()

    controller_str = ""
    if smart_match:
        controller_str = smart_match.group(1).strip()
    elif ctrl_match:
        controller_str = ctrl_match.group(1).strip()

    if "2258XT" in controller_str.upper() or ("SM2258" in upper_text and "BUFFERLESS" in upper_text):
        result["controller"] = "SM2258XT"
    elif "2259XT" in controller_str.upper() or ("SM2259" in upper_text and "BUFFERLESS" in upper_text):
        result["controller"] = "SM2259XT"
    elif "SM2258" in upper_text:
        result["controller"] = "SM2258"
    elif "SM2259" in upper_text:
        result["controller"] = "SM2259"
    elif "SM2246XT" in upper_text or ("SM2246" in upper_text and "BUFFERLESS" in upper_text):
        result["controller"] = "SM2246XT"
    elif "SM2246" in upper_text:
        result["controller"] = "SM2246EN"
    elif "SM2262" in upper_text or "SM2263" in upper_text:
        result["controller"] = "SM2262/SM2263"
    elif ctrl_match:
        result["controller"] = ctrl_match.group(1).split()[0].strip()

    result["flash_id"], result["flash_desc"] = _extract_flash_info(text)
    if not result["flash_desc"]:
        if "HYNV4" in upper_text or "HY3D-V4" in upper_text:
            result["flash_desc"] = "Hynix 3D-V4 72L TLC"
        elif "HYNV3" in upper_text:
            result["flash_desc"] = "Hynix 3D-V3 TLC"
        elif "HYNV6" in upper_text:
            result["flash_desc"] = "Hynix 3D-V6 128L TLC"

    fw_match = re.search(r'Fw\s*:\s*([A-Za-z0-9\._\-]+)', text, re.I)
    if fw_match:
        result["fw_version"] = fw_match.group(1).strip()

    return result if (result["controller"] or result["flash_id"]) else None

def parse_phison_report(text):
    """Parses output from phison_flash_id"""
    if "Identify data empty" in text or "Compatible SSD not found" in text:
        return None
    
    result = {
        "vendor": "Phison",
        "controller": None,
        "flash_id": None,
        "flash_desc": None,
        "nand_part": None,
        "fw_version": None,
        "rom_mode": False,
        "raw": text
    }

    if "SATFIRM" in text or "PS3111" in text or "S11" in text:
        result["controller"] = "PS3111-S11"
        if "SATFIRM" in text:
            result["rom_mode"] = True
    elif "PS5012" in text or "E12" in text:
        result["controller"] = "PS5012-E12"
    elif "PS5013" in text or "E13" in text:
        result["controller"] = "PS5013-E13"
    elif "PS3110" in text or "S10" in text:
        result["controller"] = "PS3110-S10"

    result["flash_id"], result["flash_desc"] = _extract_flash_info(text)

    # Search Firmware version
    fw_match = re.search(r'(?:S11fw|Firmware)\s*:\s*([A-Za-z0-9\.\_]+)', text, re.I)
    if fw_match:
        result["fw_version"] = fw_match.group(1).strip()

    return result if (result["controller"] or result["flash_id"] or result["fw_version"]) else None

def parse_maxio_report(text):
    """Parses output from jm_fid or maxio_nvme_fid (MAS0902, MAS1102, MAP1202, MAP1602, etc.)"""
    if any(k in text for k in ["Compatible SSD not found", "No drive found", "Identify failed", "Open gdp.bin error"]):
        return None
    
    result = {
        "vendor": "Maxio",
        "controller": None,
        "flash_id": None,
        "flash_desc": None,
        "nand_part": None,
        "fw_version": None,
        "rom_mode": False,
        "raw": text
    }

    upper_text = text.upper()

    # Search controller
    if "MAS0902" in upper_text or "MK8215" in upper_text or "CS1802" in upper_text or "DM9343" in upper_text:
        result["controller"] = "MAS0902"
    elif "MAS1102" in upper_text:
        result["controller"] = "MAS1102"
    elif "MAP1602" in upper_text:
        result["controller"] = "MAP1602"
    elif "MAP1202" in upper_text:
        result["controller"] = "MAP1202"
    elif "MAP1001" in upper_text or "MAP1002" in upper_text:
        result["controller"] = "MAP1002"
    elif "MK8115" in upper_text:
        result["controller"] = "MK8115"
    elif "JMF670" in upper_text:
        result["controller"] = "JMF670"
    elif "JMF662" in upper_text:
        result["controller"] = "JMF662"
    elif "JMF661" in upper_text:
        result["controller"] = "JMF661"
    else:
        ctrl_match = re.search(r'Controller\s*:\s*([^\r\n]+)', text, re.I)
        if ctrl_match:
            cand = ctrl_match.group(1).split()[0].strip()
            if cand.lower() not in ["unknown", "none", "—"]:
                result["controller"] = cand

    result["flash_id"], result["flash_desc"] = _extract_flash_info(text)

    # Search NAND string (critical for Maxio MPTool flash lookup)
    nand_str_match = re.search(r'NAND\s*string\s*:\s*([^\r\n]+)', text, re.I)
    if nand_str_match:
        result["nand_part"] = nand_str_match.group(1).strip()
        if not result["flash_desc"]:
            result["flash_desc"] = f"Part: {result['nand_part']}"

    # Search Firmware
    fw_match = re.search(r'Fw\s*:\s*([A-Za-z0-9\._\-]+)', text, re.I)
    if fw_match:
        result["fw_version"] = fw_match.group(1).strip()

    # Detect ROM Mode / Loader Mode
    if any(k in upper_text for k in ["ROM MODE", "LOADER MODE", "SWITCH TO ROM MODE.. OK", "SAFE MODE"]):
        result["rom_mode"] = True

    return result if (result["controller"] or result["flash_id"] or result["nand_part"]) else None

def parse_raw_report(text):
    """
    Universal parser for arbitrary raw diagnostic text pasted by the user.
    Auto-detects whether the log belongs to SMI, Phison, or Maxio.
    """
    if not text or not text.strip():
        return None
    
    # Try SMI first
    if any(k in text.upper() for k in ["SMI", "SM22", "HYNV", "HY3D", "FLASHID:"]):
        res = parse_smi_report(text)
        if res and (res["controller"] or res["flash_id"]):
            return res
            
    # Try Phison
    if any(k in text.upper() for k in ["PHISON", "PS31", "PS50", "S11", "SATFIRM"]):
        res = parse_phison_report(text)
        if res and (res["controller"] or res["flash_id"]):
            return res
            
    # Try Maxio
    if any(k in text.upper() for k in ["MAXIO", "MAS0", "MAS1", "MAP1", "MK81"]):
        res = parse_maxio_report(text)
        if res and (res["controller"] or res["flash_id"]):
            return res

    # General fallback: try each parser in order
    for parser in [parse_smi_report, parse_phison_report, parse_maxio_report]:
        res = parser(text)
        if res and (res["controller"] or res["flash_id"]):
            return res
            
    return None


def extract_inquiry_info(text):
    """Extracts base ATA/SCSI inquiry information (Model, Firmware, Size) from diagnostic log."""
    info = {}
    m_model = re.search(r'^[ \t]*Model[ \t]*:[ \t]*(\S.*)$', text, re.M | re.I)
    if m_model:
        val = m_model.group(1).strip()
        if val and not any(k in val.lower() for k in ["fw", "firmware", "size", "unknown"]):
            info["model"] = val

    m_fw = re.search(r'^[ \t]*(?:Fw|Firmware|S11fw)[ \t]*:[ \t]*([A-Za-z0-9\._\-]+)', text, re.M | re.I)
    if m_fw:
        val = m_fw.group(1).strip()
        if val and not any(k in val.lower() for k in ["size", "model", "drive"]):
            info["fw_version"] = val

    m_size = re.search(r'^[ \t]*Size[ \t]*:[ \t]*(\S.*)$', text, re.M | re.I)
    if m_size:
        info["size"] = m_size.group(1).strip()

    return info

def detect_device(disk_number, bus_type="SATA", force_rom_mode=False, wmi_name="", wmi_firmware=""):
    """
    Runs diagnostic probes against the specified disk number and returns
    identified controller, flash memory type, and raw diagnostics.
    wmi_name and wmi_firmware are Windows-reported FriendlyName and FirmwareVersion
    used as fallback when low-level tools cannot access the drive.
    """
    is_usb = "USB" in (bus_type or "").upper()
    is_nvme = "NVME" in (bus_type or "").upper()
    tools = get_tools_map()

    # Ask the USB bridge what sits behind it before choosing SATA or NVMe tools.
    best_inquiry = {}
    bridge_name = any(k in (wmi_name or "").upper() for k in ["REALTEK", "RTL9210", "JMS5", "ASM1", "ASM2"])
    if is_usb or bridge_name:
        try:
            from core.bridge_probe import query_bridge_drive
            binfo = query_bridge_drive(disk_number)
            if binfo and not binfo.get("error") and binfo.get("model"):
                best_inquiry["model"] = binfo["model"]
                best_inquiry["fw_version"] = binfo.get("firmware", "")
                best_inquiry["serial"] = binfo.get("serial", "")
                best_inquiry["protocol"] = binfo.get("protocol", "")
                if "is_nvme" in binfo:
                    is_nvme = bool(binfo.get("is_nvme"))
        except Exception as ex:
            print(f"Bridge probe error: {ex}")

    probes = []
    if is_nvme:
        probes.append(("smi_nvme", tools["smi_nvme"], f"{disk_number}y", parse_smi_report))
        probes.append(("maxio_nvme", tools["maxio_nvme"], f"{disk_number}y", parse_maxio_report))
    else:
        smi_args = f"{disk_number}y" + ("u" if force_rom_mode else "")
        if is_usb:
            probes.append(("smi_usb", tools["smi_usb"], smi_args, parse_smi_report))
        probes.append(("smi_ata", tools["smi_ata"], smi_args, parse_smi_report))
        probes.append(("phison", tools["phison"], f"{disk_number}y", parse_phison_report))
        probes.append(("maxio", tools["maxio"], f"{disk_number}y", parse_maxio_report))

    if not best_inquiry.get("model"):
        if wmi_name and wmi_name.strip():
            best_inquiry["model"] = wmi_name.strip()
        if wmi_firmware and wmi_firmware.strip():
            best_inquiry["fw_version"] = wmi_firmware.strip()
    best_raw_report = ""

    for name, tool_path, args, parser in probes:
        if not os.path.exists(tool_path):
            continue
        workdir = os.path.dirname(tool_path)
        
        # Clean previous report file in workdir
        for f in os.listdir(workdir):
            if f.endswith(".txt") and not any(k in f for k in ["history", "readme", "howto"]):
                try:
                    os.remove(os.path.join(workdir, f))
                except OSError:
                    pass

        run_elevated_tool(tool_path, args, workdir, timeout_sec=8)

        # Wait and poll for generated report
        report_text = ""
        for _ in range(6):
            time.sleep(0.4)
            for f in os.listdir(workdir):
                if f.endswith(".txt") and not any(k in f for k in ["history", "readme", "howto"]):
                    txt_path = os.path.join(workdir, f)
                    try:
                        with open(txt_path, 'rb') as rf:
                            content = rf.read().decode('cp1251', errors='replace')
                            if content.strip():
                                report_text = content
                                break
                    except Exception:
                        pass
            if report_text:
                break

        if report_text:
            inq = extract_inquiry_info(report_text)
            if inq.get("model") and not best_inquiry.get("model"):
                best_inquiry = inq
                best_raw_report = report_text
            elif not best_raw_report:
                best_raw_report = report_text
            elif len(report_text) > len(best_raw_report) and not any(k in report_text for k in ["failed", "error", "Identify failed"]):
                best_raw_report = report_text

            parsed = parser(report_text)
            if parsed:
                parsed["probe_used"] = name
                if inq.get("model"):
                    parsed["real_model"] = inq["model"]
                return {"success": True, "data": parsed}

    # If MPTool controllers (SMI/Phison/Maxio) weren't matched, check if an inquiry succeeded
    if best_inquiry.get("model"):
        model_str = best_inquiry.get("model", "").upper()
        fw_str = best_inquiry.get("fw_version", "—")

        # Determine brand and proprietary architecture
        vendor = "Неизвестный производитель"
        ctrl = "Проприетарный OEM контроллер"
        
        is_bridge = any(k in model_str for k in ["REALTEK", "RTL9210", "JMS57", "JMS58", "ASM115", "ASM235", "ASM236", "INITIO"])
        if is_bridge:
            vendor = "USB-мост адаптера"
            ctrl = "Накопитель внутри моста не отвечает"
            return {
                "success": False,
                "raw": best_raw_report,
                "data": {
                    "vendor": "USB-мост",
                    "controller": best_inquiry.get("model"),
                    "flash_id": "Команды перехвачены мостом",
                    "flash_desc": "Мост Realtek/JMicron возвращает свое имя вместо SSD",
                    "fw_version": fw_str,
                    "raw": best_raw_report
                },
                "message": f"Внимание: переходник ({best_inquiry.get('model')}) вернул собственное имя и прошивку моста ({fw_str}), "
                           "так как SSD внутри не ответил на низкоуровневые ATA-команды. "
                           "Возможные причины: 1) Внутри установлен диск Toshiba/Samsung, не поддерживающий эти команды; "
                           "2) Включена галочка 'Принудительный ROM Mode' без физической перемычки; "
                           "3) Диск завис или требует прямого подключения по SATA."
            }

        is_known_oem = any(k in model_str for k in ["TOSHIBA", "THNSN", "KIOXIA", "KBG", "KXG",
                                                     "SAMSUNG", "MZ-", "EVO", "PRO",
                                                     "WDC", "WD ", "SANDISK", "WDS",
                                                     "INTEL", "SSDSC", "MEMPE",
                                                     "MICRON", "CRUCIAL", "CT"])
        if any(k in model_str for k in ["TOSHIBA", "THNSN", "KIOXIA", "KBG", "KXG"]):
            vendor = "Toshiba / Kioxia"
            ctrl = "Toshiba TC58NC / Marvell"
        elif any(k in model_str for k in ["SAMSUNG", "MZ-", "EVO", "PRO"]):
            vendor = "Samsung"
            ctrl = "Samsung Phoenix / Elpis / Pablo"
        elif any(k in model_str for k in ["WDC", "WD ", "SANDISK", "WDS"]):
            vendor = "Western Digital / SanDisk"
            ctrl = "SanDisk / Marvell Proprietary"
        elif any(k in model_str for k in ["INTEL", "SSDSC", "MEMPE"]):
            vendor = "Intel"
            ctrl = "Intel Proprietary"
        elif any(k in model_str for k in ["MICRON", "CRUCIAL", "CT"]):
            vendor = "Micron / Crucial"
            ctrl = "Micron / Marvell"
        else:
            vendor = "SSD (SMI / Phison / Maxio)"
            ctrl = "Требуется ROM Mode или ручной выбор"

        oem_data = {
            "vendor": vendor,
            "controller": ctrl,
            "real_model": best_inquiry.get("model"),
            "flash_id": "Фирменный протокол производителя" if is_known_oem else "Не прочитан через текущий порт",
            "flash_desc": f"Заводской OEM SSD ({best_inquiry.get('model')})" if is_known_oem else f"Накопитель {best_inquiry.get('model')}",
            "fw_version": fw_str,
            "is_oem_unsupported": is_known_oem,
            "probe_used": "wmi_or_inquiry",
            "raw": best_raw_report
        }

        if is_known_oem:
            msg = (f"Накопитель обнаружен: {best_inquiry.get('model')} (FW: {fw_str}). "
                   f"Контроллер: {ctrl}. Для брендовых заводских накопителей {vendor} сервисные утилиты MPTool не применяются.")
        else:
            msg = (f"Накопитель обнаружен: {best_inquiry.get('model')} (FW: {fw_str}). "
                   "Низкоуровневые утилиты не смогли прочитать чип памяти напрямую. "
                   "Если накопитель завис или требует прошивки, переведите его в ROM Mode (замыкание контактов) или выберите прошивку вручную.")

        return {
            "success": True,
            "data": oem_data,
            "message": msg
        }

    return {
        "success": False,
        "raw": best_raw_report,
        "data": {
            "vendor": "Не определен",
            "controller": "Не ответил на опрос",
            "real_model": None,
            "flash_id": "—",
            "flash_desc": "Опрос не вернул данных",
            "fw_version": "—",
            "raw": best_raw_report
        },
        "message": f"Не удалось автоматически определить чипы на Диске {disk_number}. "
                   "Возможно, накопитель требует перевода в Safe/ROM Mode (замыкание тестовых контактов) "
                   "или прямого подключения по SATA без переходника."
    }

if __name__ == "__main__":
    import sys
    target = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    res = detect_device(target, bus_type="USB")
    print(res)
