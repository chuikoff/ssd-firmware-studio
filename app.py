import ctypes
import os
import socket
import sys
import threading
import time
import webbrowser

from core.paths import get_base_dir, get_ui_dir
from core.version import __version__, __app_name__


def _log(message):
    try:
        path = os.path.join(get_base_dir(), "SSD_Firmware_Studio.log")
        stamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(f"{stamp} {message}\n")
    except Exception:
        pass


def _fail(message):
    _log("ERROR " + message)
    try:
        ctypes.windll.user32.MessageBoxW(0, message, f"{__app_name__} v{__version__}", 0x10)
    except Exception:
        print(message, file=sys.stderr)


def run_desktop():
    """Open the UI from disk and call Python directly. No localhost server."""
    ui_path = os.path.join(get_ui_dir(), "index.html")
    if not os.path.isfile(ui_path):
        _fail(f"Не найден интерфейс:\n{ui_path}")
        return

    try:
        import webview
    except Exception as exc:
        _fail(
            "Не удалось загрузить встроенное окно WebView2.\n"
            f"{exc}\n\nУстановите Microsoft Edge WebView2 Runtime и запустите программу снова."
        )
        return

    from core.studio_api import StudioApi

    _log(f"desktop ui={ui_path} version={__version__}")
    try:
        webview.create_window(
            f"{__app_name__} v{__version__} — Phison / SMI / Maxio",
            url=ui_path,
            js_api=StudioApi(),
            width=1340,
            height=900,
            min_size=(1020, 680),
        )
        webview.start(gui="edgechromium")
        _log("desktop closed")
    except Exception as exc:
        _fail(
            "Окно программы не открылось.\n"
            f"{exc}\n\nНужен Microsoft Edge WebView2 Runtime. "
            "Отдельный Python ставить не нужно: он уже внутри этой программы."
        )


def _port_open(port):
    try:
        with socket.create_connection(("127.0.0.1", port), 0.3):
            return True
    except OSError:
        return False


def run_web(port=8000):
    """Optional browser mode. The window opens only after the port accepts connections."""
    from server import app
    import uvicorn

    errors = []

    def serve():
        try:
            config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
            uvicorn.Server(config).run()
        except Exception as exc:
            errors.append(exc)
            _log(f"web server failed: {exc}")

    threading.Thread(target=serve, daemon=True).start()
    for _ in range(150):
        if errors:
            break
        if _port_open(port):
            url = f"http://127.0.0.1:{port}"
            _log(f"web {url}")
            print(f"[OK] {__app_name__} v{__version__} is running at {url}")
            webbrowser.open(url)
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nShutting down.")
            return
        time.sleep(0.2)

    detail = str(errors[0]) if errors else f"порт {port} не открылся"
    _fail(f"Режим браузера не запустился: {detail}")


def run_check():
    from core.studio_api import StudioApi

    print(f"{__app_name__} v{__version__}")
    api = StudioApi()
    disks = api.get_disks()
    print(f"disks {len(disks.get('disks') or [])}")
    ranked = api.firmwares({
        "controller": "PS3111-S11",
        "flash_desc": "Toshiba BiCS3 64L TLC",
        "fw_version": "SBFG61.2",
    })
    print("top:")
    for item in (ranked.get("firmwares") or [])[:5]:
        print(f"  {item.get('match_score')} {item.get('badge')} {item.get('filename')} header={item.get('header_type')}")
    print("OK")


def main():
    _log(f"start {__app_name__} v{__version__} " + " ".join(sys.argv))
    if "--check" in sys.argv:
        run_check()
    elif "--web" in sys.argv:
        run_web()
    else:
        run_desktop()


if __name__ == "__main__":
    main()
