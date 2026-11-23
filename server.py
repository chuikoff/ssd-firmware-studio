import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any

from core.studio_api import StudioApi
from core.paths import get_ui_dir

studio = StudioApi()

UI_DIR = get_ui_dir()

app = FastAPI(title="SSD Firmware Studio API")

class DetectRequest(BaseModel):
    disk_number: int
    bus_type: Optional[str] = "SATA"
    force_rom_mode: Optional[bool] = False
    wmi_name: Optional[str] = ""
    wmi_firmware: Optional[str] = ""

class RawReportRequest(BaseModel):
    raw_text: str

class MatchRequest(BaseModel):
    detection: Optional[Dict[str, Any]] = None

class BuildFlashRequest(BaseModel):
    fw_path: str
    header_type: Optional[str] = ""
    vendor: Optional[str] = "Phison"
    controller: Optional[str] = ""
    filename: Optional[str] = ""

class LaunchFlashRequest(BaseModel):
    exe_path: str
    disk_number: Optional[int] = None

class OpenFolderRequest(BaseModel):
    folder: str

@app.get("/api/disks")
def get_disks():
    return studio.get_disks()

@app.post("/api/detect")
def probe_disk(req: DetectRequest):
    return studio.detect(
        req.disk_number,
        bus_type=req.bus_type,
        force_rom_mode=req.force_rom_mode,
        wmi_name=req.wmi_name,
        wmi_firmware=req.wmi_firmware,
    )

@app.post("/api/detect/manual")
def parse_manual_report(req: RawReportRequest):
    return studio.detect_manual(req.raw_text)

@app.post("/api/firmwares")
def get_matching_firmwares(req: MatchRequest):
    return studio.firmwares(req.detection)

@app.post("/api/flash/build")
def build_flasher(req: BuildFlashRequest):
    return studio.flash_build(
        req.fw_path,
        header_type=req.header_type,
        vendor=req.vendor,
        controller=req.controller,
        filename=req.filename or os.path.basename(req.fw_path or ""),
    )

@app.post("/api/flash/launch")
def launch_flasher(req: LaunchFlashRequest):
    return studio.flash_launch(req.exe_path, disk_number=req.disk_number)

@app.post("/api/open-folder")
def open_folder(req: OpenFolderRequest):
    return studio.open_folder(req.folder)

# Mount UI static files
app.mount("/static", StaticFiles(directory=UI_DIR), name="static")

@app.get("/")
def serve_index():
    return FileResponse(os.path.join(UI_DIR, "index.html"))

@app.get("/{filename}")
def serve_ui_file(filename: str):
    abs_ui = os.path.abspath(UI_DIR)
    abs_target = os.path.abspath(os.path.join(abs_ui, filename))
    if abs_target.startswith(abs_ui) and os.path.isfile(abs_target):
        return FileResponse(abs_target)
    return FileResponse(os.path.join(abs_ui, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=False)
