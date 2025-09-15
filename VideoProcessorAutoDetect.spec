# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('detect_start_real_time.py', '.'),
        ('add_point_xy.py', '.'),
        ('config.json', '.'),
        ('fight_number_template.png', '.'),
        ('fight_number_template2.png', '.'),
        ('fight_number_template3.png', '.'),
    ],
    hiddenimports=[
        'cv2',
        'numpy',
        'pyautogui',
        'pynput',
        'pynput.mouse',
        'pynput.keyboard',
        'mss',
        'mss.mss',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'threading',
        'datetime',
        'json',
        'time',
        'os',
        'random',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VideoProcessorAutoDetect',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
