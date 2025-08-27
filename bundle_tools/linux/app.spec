# -*- mode: python ; coding: utf-8 -*-

#--------- custom -----------------------------------------------------------------

import os
import sys
import glob
from pathlib import Path

SOURCE_DIR = Path("./").resolve()
print("SOURCE_DIR", SOURCE_DIR)

from PyInstaller.utils.hooks import collect_dynamic_libs

python_dir = os.path.dirname(sys.executable)
venv_dir = os.path.dirname(python_dir)
# Get Python version dynamically
python_version = f"python{sys.version_info.major}.{sys.version_info.minor}"
site_packages = os.path.join(venv_dir, 'lib', python_version, 'site-packages')

def check_extension(item):
    exts = ['pyc', '__pycache__']
    for ext in exts:
        if ext in item:
            return True
    return False

def get_all_files(dirName):
    listOfFile = os.listdir(dirName)
    allFiles = []
    for entry in listOfFile:
        fullPath = os.path.join(dirName, entry)
        if os.path.isdir(fullPath):
            allFiles = allFiles + get_all_files(fullPath)
        else:
            allFiles.append(fullPath)
    return allFiles

libraries = []

# Collect all VTK files
vtk_files = get_all_files(os.path.join(site_packages, 'vtkmodules'))
libraries.append((os.path.join(site_packages, 'vtk.py'), '.'))

for v in vtk_files:
    if not check_extension(v):
        dest_dir = os.path.dirname(v.replace(site_packages, ''))[1:]
        libraries.append((v, dest_dir))

# Add interpolation module (.so for Linux)
libraries.append((glob.glob(os.path.join(SOURCE_DIR, 'invesalius_cy',
    'interpolation.*.so'))[0], 'invesalius_cy'))

# -- data files -----
data_files = []

# Add AI weights
ai_data = get_all_files(os.path.join('ai'))
for ai in ai_data:
    dest_dir = os.path.dirname(ai)
    data_files.append((ai, dest_dir))

# Licenses
data_files.append(('LICENSE.pt.txt', '.'))
data_files.append(('LICENSE.txt', '.'))

# User guides
data_files.append(('docs/user_guide_en.pdf', 'docs'))
data_files.append(('docs/user_guide_pt_BR.pdf', 'docs'))

# Icons (Linux typically uses .png/.svg)
icons_files = glob.glob(os.path.join(SOURCE_DIR, 'icons', '*'))
for ic in icons_files:
    data_files.append((ic, 'icons'))

# Locale
locale_data = get_all_files(os.path.join('locale'))
for ld in locale_data:
    dest_dir = os.path.dirname(ld)
    data_files.append((ld, dest_dir))

# Neuro navigation
neuro_data = get_all_files(os.path.join('navigation'))
for nd in neuro_data:
    dest_dir = os.path.dirname(nd)
    data_files.append((nd, dest_dir))

# Presets
preset_data = get_all_files(os.path.join('presets'))
for pd in preset_data:
    dest_dir = os.path.dirname(pd)
    data_files.append((pd, dest_dir))

# Samples
sample_data = get_all_files(os.path.join('samples'))
for sd in sample_data:
    dest_dir = os.path.dirname(sd)
    data_files.append((sd, dest_dir))

#---------------------------------------------------------------------------------

block_cipher = None

a = Analysis(['app.py'],
             pathex=[SOURCE_DIR],
             binaries=libraries,
             datas=data_files,
             hiddenimports=['scipy._lib.messagestream',
                            'skimage.restoration._denoise',
                            'scipy.linalg',
                            'scipy.linalg.blas',
                            'scipy.interpolate',
                            'pywt._extensions._cwt',
                            'skimage.filters.rank.core_cy_3d',
                            'encodings',
                            'setuptools'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='invesalius',
          icon='./icons/invesalius.png',   # Linux typically uses PNG
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True)

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='invesalius')

