import os
import shutil
import subprocess

PROJECT_NAME = "LawranZip"
ENTRY_POINT = "main.py"


def get_project_files():
    """Gathers all necessary project files."""
    py_files = [f for f in os.listdir('.') if f.endswith('.py') and f != 'build.py']
    assets = [os.path.join('assets', 'icons', f) for f in os.listdir(os.path.join('assets', 'icons'))]
    translations = [os.path.join('translations', f) for f in os.listdir('translations')]
    return py_files, assets, translations

def create_spec_file(py_files, assets, translations):
    """Creates a PyInstaller spec file."""
    # Convert asset and translation paths to a format suitable for the spec file
    datas_assets = [(os.path.join('assets', 'icons', f), os.path.join('assets', 'icons')) for f in os.listdir(os.path.join('assets', 'icons'))]
    datas_translations = [(os.path.join('translations', f), 'translations') for f in os.listdir('translations')]
    all_datas = datas_assets + datas_translations

    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['{ENTRY_POINT}'],
             pathex=['.'],
             binaries=[],
             datas={all_datas},
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='{PROJECT_NAME}',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False, # This is equivalent to --windowed
          icon='LawranZip.ico')

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='{PROJECT_NAME}')
"""
    # The spec file for a one-file build does not use COLLECT.
    # We define the EXE and that's it.
    spec_content_onefile = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['{ENTRY_POINT}'],
             pathex=['.'],
             binaries=[],
             datas={all_datas},
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.datas,
          name='{PROJECT_NAME}',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False, # --windowed
          icon='LawranZip.ico')
"""

    with open("main.spec", "w") as f:
        f.write(spec_content_onefile)


def run_build():
    """Runs the PyInstaller build process."""
    py_files, assets, translations = get_project_files()
    create_spec_file(py_files, assets, translations)

    print("Running PyInstaller...")
    # The --onefile and --windowed flags are set within the .spec file
    # by having an EXE object and setting console=False.
    subprocess.run(["pyinstaller", "main.spec"], check=True)
    print("Build completed successfully!")

if __name__ == "__main__":
    # Clean up previous builds
    if os.path.isdir('build'):
        shutil.rmtree('build')
    if os.path.isdir('dist'):
        shutil.rmtree('dist')
    if os.path.exists('main.spec'):
        os.remove('main.spec')
        
    run_build()
