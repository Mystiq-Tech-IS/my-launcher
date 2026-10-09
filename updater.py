"""Автообновление MyLauncher через GitHub Releases.

Как работает:
  1. При старте (или по кнопке в настройках) запрашиваем latest release
     из GitHub API.
  2. Сравниваем tag_name с APP_VERSION.
  3. Если новее — качаем .exe во временную папку.
  4. Проверяем SHA256 (если в релизе есть checksums.txt).
  5. Запускаем .bat-хелпер, который дождётся выхода процесса и
     подменит .exe.
"""

import os
import sys
import json
import hashlib
import tempfile
import subprocess
import urllib.request
import urllib.error

from config import APP_VERSION, GITHUB_OWNER, GITHUB_REPO

try:
    from storage import log
except Exception:
    import logging
    log = logging.getLogger("launcher")


GITHUB_API = "https://api.github.com"
USER_AGENT = "MyLauncher-Updater/1.0"


class UpdateInfo:
    """Информация о доступном обновлении."""

    def __init__(self, version, changelog, download_url, asset_name,
                 asset_size, sha256_url=""):
        self.version = version
        self.changelog = changelog
        self.download_url = download_url
        self.asset_name = asset_name
        self.asset_size = asset_size
        self.sha256_url = sha256_url

    def is_newer_than(self, current):
        return _version_tuple(self.version) > _version_tuple(current)


def _version_tuple(v):
    """'3.2.1' → (3, 2, 1)."""
    out = []
    for part in str(v).lstrip("v").split("."):
        try:
            out.append(int(part))
        except ValueError:
            out.append(0)
    while len(out) < 3:
        out.append(0)
    return tuple(out[:3])


def _http_get(url, timeout=10):
    req = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def check_for_update(timeout=10):
    """Возвращает UpdateInfo | None | None-при-ошибке."""
    if not GITHUB_OWNER or not GITHUB_REPO:
        log.warning("updater: не задан GITHUB_OWNER / GITHUB_REPO")
        return None

    url = f"{GITHUB_API}/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
    try:
        raw = _http_get(url, timeout=timeout)
        data = json.loads(raw)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            log.info("updater: релизов пока нет")
            return None
        log.error(f"updater HTTP {e.code}: {e}")
        return None
    except Exception as e:
        log.error(f"updater check: {e}")
        return None

    tag = (data.get("tag_name") or "").lstrip("v")
    if not tag:
        return None

    if _version_tuple(tag) <= _version_tuple(APP_VERSION):
        log.info(f"updater: {tag} не новее текущей {APP_VERSION}")
        return None

    changelog = data.get("body", "") or ""
    assets = data.get("assets", []) or []

    exe_asset = None
    sha_asset = None
    for a in assets:
        name = (a.get("name") or "").lower()
        if name.endswith(".exe"):
            exe_asset = a
        elif "checksum" in name or name.endswith(".sha256"):
            sha_asset = a

    if exe_asset is None:
        log.warning("updater: в релизе нет .exe")
        return None

    return UpdateInfo(
        version=tag,
        changelog=changelog,
        download_url=exe_asset["browser_download_url"],
        asset_name=exe_asset["name"],
        asset_size=exe_asset.get("size", 0),
        sha256_url=sha_asset["browser_download_url"] if sha_asset else "",
    )


def download_update(info, progress_callback=None, timeout=120):
    """Скачивает .exe во временную папку. Возвращает путь или ''."""
    if info is None:
        return ""

    tmp_dir = os.path.join(tempfile.gettempdir(), "mylauncher_update")
    try:
        os.makedirs(tmp_dir, exist_ok=True)
    except Exception as e:
        log.error(f"updater mkdir: {e}")
        return ""

    dst = os.path.join(tmp_dir, info.asset_name)

    try:
        req = urllib.request.Request(
            info.download_url, headers={"User-Agent": USER_AGENT}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            total = int(resp.headers.get("Content-Length", 0)) \
                or info.asset_size
            chunk = 64 * 1024
            downloaded = 0
            with open(dst, "wb") as f:
                while True:
                    buf = resp.read(chunk)
                    if not buf:
                        break
                    f.write(buf)
                    downloaded += len(buf)
                    if progress_callback and total:
                        progress_callback(downloaded, total)
    except Exception as e:
        log.error(f"updater download: {e}")
        return ""

    # Проверка SHA256
    if info.sha256_url:
        try:
            sha_raw = _http_get(info.sha256_url).decode("utf-8")
            expected = sha_raw.strip().split()[0].lower()
            actual = _sha256(dst)
            if actual != expected:
                log.error(
                    f"updater: SHA256 не совпал! "
                    f"expected={expected} actual={actual}"
                )
                try:
                    os.remove(dst)
                except Exception:
                    pass
                return ""
            log.info("updater: SHA256 подтверждён")
        except Exception as e:
            log.error(f"updater checksum: {e}")

    return dst


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def apply_update_and_restart(new_exe_path):
    """Запускает .bat-хелпер, который подменит .exe и перезапустит.

    Возвращает True если хелпер запущен.
    """
    if not getattr(sys, "frozen", False):
        log.warning("updater: не frozen — автоустановка недоступна")
        return False

    if not new_exe_path or not os.path.exists(new_exe_path):
        return False

    current_exe = sys.executable
    if not current_exe.lower().endswith(".exe"):
        return False

    helper_dir = os.path.dirname(new_exe_path)
    helper_path = os.path.join(helper_dir, "apply_update.bat")

    bat = f"""@echo off
chcp 65001 >nul
setlocal

set "TARGET={current_exe}"
set "NEW={new_exe_path}"
set "BACKUP=%TARGET%.old"

echo Waiting for launcher to close...
:waitloop
tasklist /FI "PID eq {os.getpid()}" 2>nul | find "{os.getpid()}" >nul
if not errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto waitloop
)

echo Backing up...
if exist "%BACKUP%" del /f /q "%BACKUP%"
move /y "%TARGET%" "%BACKUP%" >nul

echo Installing update...
move /y "%NEW%" "%TARGET%" >nul

if errorlevel 1 (
    echo Failed, rolling back...
    move /y "%BACKUP%" "%TARGET%" >nul
    pause
    exit /b 1
)

echo Restarting...
start "" "%TARGET%"

timeout /t 2 /nobreak >nul
del /f /q "%BACKUP%" 2>nul
exit /b 0
"""

    try:
        with open(helper_path, "w", encoding="utf-8") as f:
            f.write(bat)
    except Exception as e:
        log.error(f"updater write helper: {e}")
        return False

    try:
        subprocess.Popen(
            ["cmd", "/c", helper_path],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            close_fds=True,
        )
        return True
    except Exception as e:
        log.error(f"updater spawn helper: {e}")
        return False