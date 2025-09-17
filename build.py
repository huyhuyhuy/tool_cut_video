import os
import subprocess
import shutil
import sys

def clean_build():
    """Xóa các thư mục build cũ"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['VideoProcessor.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Đang xóa thư mục {dir_name}...")
            shutil.rmtree(dir_name)
    
    for file_name in files_to_clean:
        if os.path.exists(file_name):
            print(f"Đang xóa file {file_name}...")
            os.remove(file_name)

def install_requirements():
    """Cài đặt các thư viện cần thiết với version tương thích"""
    print("Đang cài đặt các thư viện...")
    
    # Cài đặt từng package riêng để tránh conflict
    packages = [
        'opencv-python',
        'numpy<2.0',      # Tránh NumPy 2.x conflict
        'pyautogui',
        'pynput',
        'pillow',
        'mss',
        'pyinstaller'
    ]
    
    for package in packages:
        try:
            print(f"Đang cài đặt {package}...")
            subprocess.run(['pip', 'install', package], check=True, capture_output=True)
            print(f"✅ Đã cài đặt {package}")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Lỗi cài đặt {package}, tiếp tục...")
            continue

def check_files():
    """Kiểm tra các file cần thiết"""
    required_files = [
        'main.py',
        'detect_start_real_time.py',
        'add_point_xy.py',
        'config.json',
        'fight_number_template.png',
        'fight_number_template2.png',
        'fight_number_template3.png',
        'template_do_new.png',
        'template_xanh_new.png',
        'template_hoa_new.png'
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

def test_dependencies():
    """Test các dependencies đã cài đúng chưa"""
    print("🧪 Testing dependencies...")
    
    try:
        import cv2
        print(f"✅ OpenCV: {cv2.__version__}")
    except ImportError as e:
        print(f"❌ OpenCV lỗi: {e}")
        return False
    
    try:
        import numpy
        print(f"✅ NumPy: {numpy.__version__}")
    except ImportError as e:
        print(f"❌ NumPy lỗi: {e}")
        return False
    
    try:
        import pyautogui
        print(f"✅ PyAutoGUI: {pyautogui.__version__}")
    except ImportError as e:
        print(f"❌ PyAutoGUI lỗi: {e}")
        return False
    
    try:
        import pynput
        print("✅ PyNput: OK")
    except ImportError as e:
        print(f"❌ PyNput lỗi: {e}")
        return False
    
    try:
        import mss
        print("✅ MSS: OK")
    except ImportError as e:
        print(f"❌ MSS lỗi: {e}")
        return False
    
    print("✅ Tất cả dependencies OK!")
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
        ('template_do_new.png', '.'),
        ('template_xanh_new.png', '.'),
        ('template_hoa_new.png', '.'),
    ],
    hiddenimports=[
        'cv2',
        'numpy',
        'numpy.core.multiarray',
        'numpy.core._methods',
        'numpy.lib.format',
        'pyautogui',
        'pynput',
        'pynput.mouse',
        'pynput.keyboard',
        'mss',
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
    name='VideoProcessor',
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
    with open('VideoProcessor.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    # Build với spec file
    subprocess.run([
        'pyinstaller',
        '--noconfirm',
        'VideoProcessor.spec'
    ], check=True)

def create_requirements():
    """Tạo file requirements.txt nếu chưa có"""
    if not os.path.exists('requirements.txt'):
        print("Tạo file requirements.txt...")
        requirements = '''opencv-python
numpy<2.0
pyinstaller
pyautogui
pynput
pillow
mss
'''
        with open('requirements.txt', 'w', encoding='utf-8') as f:
            f.write(requirements)
        print("Đã tạo file requirements.txt")

def main():
    try:
        print("🚀 Bắt đầu quá trình build VideoProcessor...")
        print("=" * 50)
        
        # Kiểm tra file cần thiết
        if not check_files():
            print("\n❌ Build thất bại do thiếu file!")
            return 1
        
        # Clean build cũ
        clean_build()
        
        # Cài đặt requirements
        install_requirements()
        
        # Test dependencies
        if not test_dependencies():
            print("\n❌ Dependencies không hoạt động!")
            print("Hãy cài đặt lại: pip install opencv-python numpy<2.0 pyautogui pynput pillow mss pyinstaller")
            return 1
        
        # Build exe
        build_exe()
        
        print("\n" + "=" * 50)
        print("✅ BUILD THÀNH CÔNG!")
        print("📁 File exe: dist/VideoProcessor.exe")
        print("\n📋 Hướng dẫn:")
        print("1. Copy file VideoProcessor.exe sang máy khác")
        print("2. Chạy VideoProcessor.exe (không cần cài Python)")
        print("3. Chọn thư mục video và xử lý")
        print("4. 'Bắt đầu xử lý' - video có banner START")
        print("5. 'Bắt đầu xử lý (New)' - video không có banner START")
        print("\n⚠️  Nếu exe không chạy trên máy khác:")
        print("   - Cài Visual C++ Redistributable 2015-2022")
        print("   - Chạy với quyền Administrator")
        print("   - Tạm tắt Windows Defender")
        
    except Exception as e:
        print(f"\n❌ Lỗi build: {str(e)}")
        print("\n🔧 Giải pháp:")
        print("1. Cài đặt Visual Studio Build Tools")
        print("2. Hoặc dùng Python 3.9-3.11 thay vì 3.13")
        print("3. Cài đặt lại: pip install opencv-python numpy<2.0")
        return 1
    return 0

if __name__ == "__main__":
    exit(main()) 