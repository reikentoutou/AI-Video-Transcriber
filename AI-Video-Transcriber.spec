# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, collect_submodules


root = Path(SPECPATH).resolve()
ffmpeg_bin = root / "build" / "ffmpeg" / "bin"

datas = [
    (str(root / "backend"), "backend"),
    (str(root / "static"), "static"),
]
datas += collect_data_files("faster_whisper")

binaries = []
for exe_name in ("ffmpeg.exe", "ffprobe.exe"):
    exe_path = ffmpeg_bin / exe_name
    if exe_path.exists():
        binaries.append((str(exe_path), "bin"))

for package_name in ("av", "ctranslate2", "onnxruntime"):
    binaries += collect_dynamic_libs(package_name)

hiddenimports = []
for package_name in (
    "uvicorn",
    "uvicorn.protocols",
    "uvicorn.lifespan",
    "webview",
    "faster_whisper",
    "ctranslate2",
    "onnxruntime",
    "openai",
    "pythonnet",
    "clr_loader",
    "tokenizers",
    "yt_dlp",
):
    hiddenimports += collect_submodules(package_name)
hiddenimports += ["clr"]


a = Analysis(
    [str(root / "desktop.py")],
    pathex=[str(root), str(root / "backend")],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="AI Video Transcriber",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="AI Video Transcriber",
)
