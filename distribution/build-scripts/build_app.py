#!/usr/bin/env python3
"""Repeatable standalone-build script for the customized OpenLP 3.1.7 (Windows x64, PyInstaller one-folder).

Run with the dedicated build venv:
    D:\\OpenLPxx\\distribution\\build-env\\Scripts\\python.exe D:\\OpenLPxx\\distribution\\build-scripts\\build_app.py

Steps: (1) PyInstaller build from OpenLP.spec, (2) place plugin sources, core data files, .version and the
native VLC runtime beside OpenLP.exe (the layout OpenLP's frozen-mode path logic expects).
Nothing is written inside the OpenLP source tree.
"""
import shutil
import subprocess
import sys
from pathlib import Path

SRC = Path(r'D:\OpenLPxx\openlp-source')
DIST_ROOT = Path(r'D:\OpenLPxx\distribution')
APP_BUILD = DIST_ROOT / 'app-build'
WORK = DIST_ROOT / 'build-work'
SPEC = DIST_ROOT / 'build-scripts' / 'OpenLP.spec'
VLC_HOST = Path(r'C:\Program Files\VideoLAN\VLC')
APP_DIR = APP_BUILD / 'OpenLP'


def _copy_tree_filtered(src: Path, dest: Path, skip_suffixes=('.pyc',), only_non_py=False) -> int:
    count = 0
    for file in src.rglob('*'):
        if not file.is_file() or '__pycache__' in file.parts or file.suffix in skip_suffixes:
            continue
        if only_non_py and file.suffix == '.py':
            continue
        target = dest / file.relative_to(src)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file, target)
        count += 1
    return count


def main() -> int:
    if APP_BUILD.exists() and any(APP_BUILD.iterdir()):
        print(f'Refusing to overwrite non-empty {APP_BUILD}', file=sys.stderr)
        return 1
    if not (VLC_HOST / 'libvlc.dll').exists():
        print(f'Native VLC runtime not found in {VLC_HOST}', file=sys.stderr)
        return 1

    subprocess.run(
        [sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean',
         '--distpath', str(APP_BUILD), '--workpath', str(WORK), str(SPEC)],
        check=True, cwd=str(DIST_ROOT / 'build-scripts'))

    plugin_files = _copy_tree_filtered(SRC / 'openlp' / 'plugins', APP_DIR / 'plugins')
    core_files = _copy_tree_filtered(SRC / 'openlp' / 'core', APP_DIR / 'core', only_non_py=True)
    shutil.copy2(SRC / 'openlp' / '.version', APP_DIR / '.version')
    shutil.copy2(SRC / 'resources' / 'images' / 'OpenLP.ico', APP_DIR / 'OpenLP.ico')
    shutil.copy2(SRC / 'LICENSE', APP_DIR / 'LICENSE.txt')
    (APP_DIR / 'i18n').mkdir(exist_ok=True)

    vlc_dest = APP_DIR / 'vlc'
    vlc_dest.mkdir(exist_ok=True)
    for dll in ('libvlc.dll', 'libvlccore.dll'):
        shutil.copy2(VLC_HOST / dll, vlc_dest / dll)
    shutil.copytree(VLC_HOST / 'plugins', vlc_dest / 'plugins')

    print(f'Assembled: {plugin_files} plugin files, {core_files} core data files, VLC runtime -> {APP_DIR}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
