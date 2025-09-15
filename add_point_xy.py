import json
import pyautogui
import tkinter as tk
from tkinter import messagebox
import threading
import time
from pynput import mouse, keyboard
import mss

class ClickPointSetter:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.running = False
        self.click_points = []  # Lưu 6 điểm click
        self.current_point = 0  # Điểm hiện tại (0-5)
        self.mouse_listener = None
        self.keyboard_listener = None
        self.current_setting_type = None  # Loại vị trí đang set
        
    def load_config(self):
        """Load cấu hình hiện tại từ file JSON"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Lỗi load config: {e}")
            return {
                # "x1": 585, "y1": 180, "x2": 1265, "y2": 566,
                # 6 vị trí click mới
                "x_open_bet": 300, "y_open_bet": 800,
                "x_close_bet": 300, "y_close_bet": 800,
                "x_meron_win": 300, "y_meron_win": 800,
                "x_wala_win": 300, "y_wala_win": 800,
                "x_draw": 300, "y_draw": 800,
                "x_cancel": 300, "y_cancel": 800
            }
    
    def save_config(self, config):
        """Lưu cấu hình vào file JSON"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Lỗi save config: {e}")
            return False
    
    def get_mouse_position(self):
        """Lấy vị trí con trỏ chuột hiện tại - Hỗ trợ đa màn hình"""
        try:
            # Sử dụng pynput để lấy tọa độ chính xác trên đa màn hình
            with mouse.Controller() as controller:
                x, y = controller.position
                return x, y
        except Exception as e:
            print(f"Lỗi lấy vị trí chuột: {e}")
            return None, None
    
    def on_click(self, x, y, button, pressed):
        """Callback khi click chuột"""
        if pressed and button == mouse.Button.left and self.running:
            self.click_points.append((x, y))
            print(f"Đã click điểm {self.current_point + 1} tại tọa độ: ({x}, {y})")
            
            self.current_point += 1
            
            # Nếu đã đủ 1 điểm (chỉ cần 1 điểm cho mỗi loại)
            if self.current_point >= 1:
                print(f"Đã set tọa độ cho {self.current_setting_type}!")
                self.stop_monitoring()
                return False  # Dừng listener
            
            return True  # Tiếp tục listener
    
    def on_key_press(self, key):
        """Callback khi nhấn phím"""
        if key == keyboard.Key.esc and self.running:
            print("Đã hủy")
            self.stop_monitoring()
            return False  # Dừng listener
    
    def wait_for_click(self, setting_type, callback=None):
        """Chờ người dùng click chuột trái để xác nhận 1 tọa độ cho loại cụ thể"""
        type_names = {
            "open_bet": "Mở cược",
            "close_bet": "Đóng cược", 
            "meron_win": "Meron thắng",
            "wala_win": "Wala thắng",
            "draw": "Hòa",
            "cancel": "Hủy trận"
        }
        
        type_name = type_names.get(setting_type, setting_type)
        print(f"Di chuyển chuột đến vị trí {type_name} và nhấn chuột trái 1 lần...")
        print("Nhấn ESC để hủy")
        
        self.running = True
        self.click_points = []
        self.current_point = 0
        self.current_setting_type = setting_type
        
        def monitor_click():
            try:
                # Tạo mouse listener
                self.mouse_listener = mouse.Listener(on_click=self.on_click)
                self.mouse_listener.start()
                
                # Tạo keyboard listener
                self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
                self.keyboard_listener.start()
                
                # Chờ cho đến khi có 1 click hoặc ESC
                while self.running and self.current_point < 1:
                    time.sleep(0.1)
                
                # Dừng listeners
                if self.mouse_listener:
                    self.mouse_listener.stop()
                if self.keyboard_listener:
                    self.keyboard_listener.stop()
                
                # Gọi callback nếu có click point
                if len(self.click_points) == 1 and callback:
                    callback(self.click_points[0], setting_type)
                    
            except Exception as e:
                print(f"Lỗi monitor click: {e}")
                self.running = False
        
        # Chạy trong thread riêng
        click_thread = threading.Thread(target=monitor_click)
        click_thread.daemon = True
        click_thread.start()
        
        return click_thread
    
    def set_single_click_point(self, click_point, setting_type):
        """Cập nhật 1 tọa độ click point vào config cho loại cụ thể"""
        try:
            if len(click_point) != 2:
                print("Cần đúng 1 điểm click!")
                return False
                
            # Load config hiện tại
            config = self.load_config()
            
            # Cập nhật tọa độ mới theo loại
            x, y = click_point
            config[f'x_{setting_type}'] = x
            config[f'y_{setting_type}'] = y
            
            # Lưu config
            if self.save_config(config):
                type_names = {
                    "open_bet": "Mở cược",
                    "close_bet": "Đóng cược", 
                    "meron_win": "Meron thắng",
                    "wala_win": "Wala thắng",
                    "draw": "Hòa",
                    "cancel": "Hủy trận"
                }
                type_name = type_names.get(setting_type, setting_type)
                print(f"Đã cập nhật tọa độ {type_name}: ({x}, {y})")
                return True
            else:
                print("Lỗi khi lưu config")
                return False
                
        except Exception as e:
            print(f"Lỗi set click point: {e}")
            return False
    
    def stop_monitoring(self):
        """Dừng việc theo dõi click"""
        self.running = False
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()

def set_single_click_point_gui(setting_type, parent_window=None):
    """Hàm chính để set 1 click point với GUI cho loại cụ thể"""
    setter = ClickPointSetter()
    
    def on_click_detected(click_point, setting_type):
        """Callback khi phát hiện click"""
        # Cập nhật config
        if setter.set_single_click_point(click_point, setting_type):
            # Tạo message chi tiết
            type_names = {
                "open_bet": "Mở cược",
                "close_bet": "Đóng cược", 
                "meron_win": "Meron thắng",
                "wala_win": "Wala thắng",
                "draw": "Hòa",
                "cancel": "Hủy trận"
            }
            type_name = type_names.get(setting_type, setting_type)
            x, y = click_point
            message = f"Đã cập nhật tọa độ {type_name}:\n({x}, {y})"
            
            if parent_window:
                # Hiển thị thông báo trong main window và reload config sau khi OK
                def show_message_and_reload():
                    result = messagebox.showinfo("Thành công", message)
                    # Sau khi người dùng nhấn OK, reload config
                    if hasattr(parent_window, 'reload_config_after_setting'):
                        parent_window.reload_config_after_setting()
                
                parent_window.after(0, show_message_and_reload)
            else:
                messagebox.showinfo("Thành công", message)
        else:
            if parent_window:
                parent_window.after(0, lambda: messagebox.showerror(
                    "Lỗi", 
                    "Không thể lưu tọa độ vào config.json"
                ))
            else:
                messagebox.showerror("Lỗi", "Không thể lưu tọa độ vào config.json")
    
    # Bắt đầu theo dõi click
    click_thread = setter.wait_for_click(setting_type, on_click_detected)
    
    return setter, click_thread

# Test function
if __name__ == "__main__":
    print("Test chức năng Set Click Point")
    setter = ClickPointSetter()
    
    def test_callback(click_point, setting_type):
        print(f"Test callback cho {setting_type}: {click_point}")
        if setter.set_single_click_point(click_point, setting_type):
            print("Test thành công!")
        else:
            print("Test thất bại!")
    
    click_thread = setter.wait_for_click("open_bet", test_callback)
    
    try:
        click_thread.join()
    except KeyboardInterrupt:
        setter.stop_monitoring()
        print("Đã dừng test")
