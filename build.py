import os
import subprocess
import shutil
import sys

def clean_build():
    """Xóa các thư mục build cũ"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['VideoProcessor.spec', 'VideoProcessorAutoDetect.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Đang xóa thư mục {dir_name}...")
            shutil.rmtree(dir_name)
    
    for file_name in files_to_clean:
        if os.path.exists(file_name):
            print(f"Đang xóa file {file_name}...")
            os.remove(file_name)

def install_requirements():
    """Cài đặt các thư viện cần thiết"""
    print("Đang cài đặt các thư viện...")
    try:
        subprocess.run(['pip', 'install', '-r', 'requirements.txt'], check=True)
    except subprocess.CalledProcessError:
        print("Lỗi cài đặt requirements. Thử cài đặt thủ công...")
        # Cài đặt các thư viện chính
        packages = [
            'opencv-python==4.9.0.80',
            'numpy==1.26.4',
            'pyautogui==0.9.54',
            'pynput==1.7.6',
            'pillow==10.2.0',
            'mss==9.0.1',
            'pyinstaller==6.4.0'
        ]
        for package in packages:
            try:
                subprocess.run(['pip', 'install', package], check=True)
                print(f"Đã cài đặt {package}")
            except subprocess.CalledProcessError as e:
                print(f"Lỗi cài đặt {package}: {e}")

def check_files():
    """Kiểm tra các file cần thiết"""
    required_files = [
        'main.py',
        'detect_start_real_time.py',
        'add_point_xy.py',
        'config.json',
        'fight_number_template.png',
        'fight_number_template2.png',
        'fight_number_template3.png'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Thiếu các file sau:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ Tất cả file cần thiết đã có")
    return True

def build_exe():
    """Build file exe"""
    print("Đang build file exe...")
    
    # Tạo spec file tùy chỉnh
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

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
'''
    
    # Lưu spec file
    with open('VideoProcessorAutoDetect.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    # Build với spec file
    subprocess.run([
        'pyinstaller',
        '--noconfirm',
        'VideoProcessorAutoDetect.spec'
    ], check=True)

def create_requirements():
    """Tạo file requirements.txt nếu chưa có"""
    if not os.path.exists('requirements.txt'):
        print("Tạo file requirements.txt...")
        requirements = '''opencv-python==4.9.0.80
numpy==1.26.4
pyinstaller==6.4.0
pyautogui==0.9.54
pynput==1.7.6
pillow==10.2.0
mss==9.0.1
'''
        with open('requirements.txt', 'w', encoding='utf-8') as f:
            f.write(requirements)
        print("Đã tạo file requirements.txt")

def main():
    try:
        print("🚀 Bắt đầu quá trình build VideoProcessor Auto Detect...")
        print("=" * 50)
        
        # Tạo requirements.txt nếu chưa có
        create_requirements()
        
        # Kiểm tra file cần thiết
        if not check_files():
            print("\n❌ Build thất bại do thiếu file!")
            return 1
        
        # Clean build cũ
        clean_build()
        
        # Cài đặt requirements
        install_requirements()
        
        # Build exe
        build_exe()
        
        print("\n" + "=" * 50)
        print("✅ Build thành công!")
        print("📁 File exe được tạo tại: dist/VideoProcessorAutoDetect.exe")
        print("\n📋 Hướng dẫn sử dụng:")
        print("1. Copy file exe và các file .png template vào cùng thư mục")
        print("2. Chạy VideoProcessorAutoDetect.exe")
        print("3. Chọn thư mục video hoặc dùng Auto Detect")
        
    except Exception as e:
        print(f"\n❌ Lỗi trong quá trình build: {str(e)}")
        print("\n🔧 Thử các bước sau:")
        print("1. Cài đặt Python 3.8+")
        print("2. Cài đặt pip: python -m ensurepip --upgrade")
        print("3. Cài đặt PyInstaller: pip install pyinstaller")
        print("4. Chạy lại: python build.py")
        return 1
    return 0

if __name__ == "__main__":
    exit(main()) 