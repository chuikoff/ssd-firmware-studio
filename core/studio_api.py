import os
import subprocess

from core.detector import detect_device, parse_raw_report
from core.firmware_matcher import match_firmwares
from core.flasher import execute_flasher, prepare_flasher
from core.paths import get_output_dir
from core.scanner import scan_disks


class StudioApi:
    """Methods exposed to the desktop window. Names are part of the JS bridge."""

    def get_version(self):
        from core.version import __version__, __app_name__, __build_date__
        return {
            "version": __version__,
            "app_name": __app_name__,
            "build_date": __build_date__
        }

    def get_disks(self):
        try:
            return {"disks": scan_disks()}
        except Exception as exc:
            return {"disks": [], "message": str(exc)}

    def detect(self, disk_number, bus_type="SATA", force_rom_mode=False, wmi_name="", wmi_firmware=""):
        try:
            return detect_device(
                int(disk_number),
                bus_type=bus_type or "SATA",
                force_rom_mode=bool(force_rom_mode),
                wmi_name=wmi_name or "",
                wmi_firmware=wmi_firmware or "",
            )
        except Exception as exc:
            return {"success": False, "message": str(exc)}

    def detect_manual(self, raw_text):
        try:
            data = parse_raw_report(raw_text or "")
        except Exception as exc:
            return {"success": False, "message": str(exc)}
        if data:
            return {"success": True, "data": data}
        return {
            "success": False,
            "message": "Не удалось распознать формат отчета (SMI / Phison / Maxio). Проверьте корректность текста.",
        }

    def firmwares(self, detection=None):
        try:
            return {"firmwares": match_firmwares(detection)}
        except Exception as exc:
            return {"firmwares": [], "message": str(exc)}

    def flash_build(self, fw_path, header_type="", vendor="Phison", controller="", filename=""):
        try:
            return prepare_flasher(
                fw_path,
                header_type=header_type or "",
                vendor=vendor or "Phison",
                controller=controller or "",
                filename=filename or "",
            )
        except Exception as exc:
            return {"success": False, "message": str(exc)}

    def flash_launch(self, exe_path, disk_number=None):
        try:
            number = None if disk_number in (None, "") else int(disk_number)
            return execute_flasher(exe_path, disk_number=number)
        except Exception as exc:
            return {"success": False, "message": str(exc)}

    def open_folder(self, folder="output"):
        try:
            target = get_output_dir() if not folder or folder.strip().lower() == "output" else os.path.abspath(folder)
            os.makedirs(target, exist_ok=True)
            os.startfile(target)
            return {"success": True, "opened": target}
        except Exception as exc:
            return {"success": False, "message": str(exc)}
