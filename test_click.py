import json
import pyautogui
import time

# Cài đặt pyautogui cho Windows
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.1

def load_config():
    """Load cấu hình từ file JSON"""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Lỗi load config: {e}")
        return None

def test_click_point(point_name, x, y):
    """Test click một điểm"""
    print(f"Test click {point_name} tại ({x}, {y})...")
    try:
        # Di chuyển chuột đến vị trí
        pyautogui.moveTo(x, y, duration=0.5)
        print(f"Đã di chuyển chuột đến ({x}, {y})")
        
        # Click chuột
        pyautogui.click(x, y)
        print(f"✓ Đã click {point_name} thành công!")
        time.sleep(1)
        return True
    except Exception as e:
        print(f"✗ Lỗi click {point_name}: {e}")
        return False

def main():
    print("=== TEST CLICK CHUỘT ===")
    
    # Load config
    config = load_config()
    if not config:
        print("Không thể load config.json")
        return
    
    # In tọa độ hiện tại
    print("Tọa độ hiện tại:")
    print(f"  Mở cược: ({config['x_open_bet']}, {config['y_open_bet']})")
    print(f"  Đóng cược: ({config['x_close_bet']}, {config['y_close_bet']})")
    print(f"  Meron thắng: ({config['x_meron_win']}, {config['y_meron_win']})")
    print(f"  Wala thắng: ({config['x_wala_win']}, {config['y_wala_win']})")
    print(f"  Hòa: ({config['x_draw']}, {config['y_draw']})")
    print(f"  Hủy trận: ({config['x_cancel']}, {config['y_cancel']})")
    
    print("\nBắt đầu test click trong 3 giây...")
    time.sleep(3)
    
    # Test từng điểm
    points = [
        ("Mở cược", config['x_open_bet'], config['y_open_bet']),
        ("Đóng cược", config['x_close_bet'], config['y_close_bet']),
        ("Meron thắng", config['x_meron_win'], config['y_meron_win']),
        ("Wala thắng", config['x_wala_win'], config['y_wala_win']),
        ("Hòa", config['x_draw'], config['y_draw']),
        ("Hủy trận", config['x_cancel'], config['y_cancel'])
    ]
    
    for name, x, y in points:
        test_click_point(name, x, y)
        time.sleep(1)
    
    print("\n=== HOÀN THÀNH TEST ===")

if __name__ == "__main__":
    main() 