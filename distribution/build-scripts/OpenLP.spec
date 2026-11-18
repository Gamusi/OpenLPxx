# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for the customized OpenLP 3.1.7 standalone Windows build (one-folder).
# Kept outside the OpenLP source tree. Run via build_app.py.
import pathlib
import sys

from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_submodules

SRC = pathlib.Path(r'D:\OpenLPxx\openlp-source')
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
PKG = SRC / 'openlp'

pmi_datas, pmi_binaries, pmi_hidden = collect_all('pymediainfo')

hiddenimports = collect_submodules('openlp') + pmi_hidden + [
    'alembic', 'bs4', 'chardet', 'flask', 'flask_cors', 'lxml', 'lxml.etree', 'lxml.objectify',
    'mako', 'packaging', 'platformdirs', 'pymediainfo', 'qrcode', 'qtawesome', 'requests',
    'sqlalchemy', 'sqlalchemy.dialects.sqlite', 'waitress', 'websockets',
    'pythoncom', 'pywintypes', 'win32api', 'win32com', 'win32com.client', 'win32con', 'win32gui', 'win32ui',
    'vlc',
    'PyQt5.QtWebEngineWidgets', 'PyQt5.QtMultimedia', 'PyQt5.QtSvg', 'PyQt5.QtOpenGL', 'PyQt5.QtPrintSupport',
]

datas = collect_data_files('qtawesome') + pmi_datas
binaries = pmi_binaries

a = Analysis(
    [str(SRC / 'run_openlp.py')],
    pathex=[str(SRC)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=['tkinter', 'pytest', 'IPython', 'matplotlib', 'numpy'],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='OpenLP',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon=str(SRC / 'resources' / 'images' / 'OpenLP.ico'),
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='OpenLP',
)
