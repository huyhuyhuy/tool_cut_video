import cv2
import numpy as np
import json
import pyautogui
import time
import threading
from datetime import datetime
import os
import mss
from pynput import mouse

# Cài đặt pyautogui cho Windows
pyautogui.FAILSAFE = False  # Tắt failsafe để tránh lỗi khi di chuyển chuột
pyautogui.PAUSE = 0.1  # Delay giữa các thao tác

class RealTimeDetector:
    def __init__(self, config_file='config.json'):
        self.config = self.load_config(config_file)
        self.running = False
        self.detection_thread = None
        
        # Load templates từ main.py
        self.load_templates()
        
        # Thêm biến để theo dõi trạng thái (giống main.py)
        self.start_detected = False
        self.looking_for_scene_change = False  # Đang tìm chuyển cảnh
        self.waiting_for_result = False        # Đang đợi 2 phút
        self.start_time = None
        self.wait_start_time = None
        self.reference_frame = None  # Frame START làm tham chiếu
        self.MIN_MATCH_DURATION = 1 * 60 + 58  # 1 phút 58 giây (thay vì 2 phút)
        
        # Thêm biến để theo dõi trạng thái auto click
        self.auto_click_state = "WAITING_START"  # WAITING_START, BET_OPENED, BET_CLOSED
        self.bet_open_time = None
        self.BET_DURATION = 45  # 45 giây để đóng cược
    
    def load_config(self, config_file):
        """Load cấu hình từ file JSON"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Lỗi load config: {e}")
            return {
                "x1": 176, "y1": 72, "x2": 1005, "y2": 447,
                "mo_cuoc_x": 100, "mo_cuoc_y": 100,
                "dong_cuoc_x": 200, "dong_cuoc_y": 100,
                "meron_thang_x": 300, "meron_thang_y": 100,
                "wala_thang_x": 400, "wala_thang_y": 100,
                "hoa_x": 500, "hoa_y": 100,
                "huy_tran_x": 600, "huy_tran_y": 100
            }
    
    def reload_config(self):
        """Reload cấu hình từ file JSON"""
        try:
            self.config = self.load_config('config.json')
            print("Đã reload config thành công")
            return True
        except Exception as e:
            print(f"Lỗi reload config: {e}")
            return False
    
    def load_templates(self):
        """Load các template từ main.py"""
        try:
            # Load template 1
            template_full = cv2.imread('fight_number_template.png')
            if template_full is not None:
                height, width = template_full.shape[:2]
                text_roi = {
                    'y1': int(height * 0.3201),
                    'y2': int(height * 0.52),
                    'x1': int(width * 0.2996),
                    'x2': int(width * 0.6493)
                }
                self.fight_number_template = template_full[text_roi['y1']:text_roi['y2'], 
                                 text_roi['x1']:text_roi['x2']]
            else:
                self.fight_number_template = None
                print("Không thể load template 1")
            
            # Load template 2
            template_full2 = cv2.imread('fight_number_template2.png')
            if template_full2 is not None:
                height2, width2 = template_full2.shape[:2]
                text_roi2 = {
                    'y1': int(height2 * 0.3201),
                    'y2': int(height2 * 0.52),
                    'x1': int(width2 * 0.2996),
                    'x2': int(width2 * 0.6493)
                }
                self.fight_number_template2 = template_full2[text_roi2['y1']:text_roi2['y2'], 
                                  text_roi2['x1']:text_roi2['x2']]
            else:
                self.fight_number_template2 = None
                print("Không thể load template 2")
            
            # Load template 3
            template_full3 = cv2.imread('fight_number_template3.png')
            if template_full3 is not None:
                height3, width3 = template_full3.shape[:2]
                text_roi3 = {
                    'y1': int(height3 * 0.3201),
                    'y2': int(height3 * 0.52),
                    'x1': int(width3 * 0.2996),
                    'x2': int(width3 * 0.6493)
                }
                self.fight_number_template3 = template_full3[text_roi3['y1']:text_roi3['y2'], 
                                  text_roi3['x1']:text_roi3['x2']]
            else:
                self.fight_number_template3 = None
                print("Không thể load template 3")
                
        except Exception as e:
            print(f"Lỗi load templates: {e}")
            self.fight_number_template = None
            self.fight_number_template2 = None
            self.fight_number_template3 = None
    
    def detect_start_banner(self, frame):
        """Chỉ phát hiện banner START, không cần phát hiện kết quả"""
        height, width = frame.shape[:2]
        
        # Vùng chứa chữ FIGHT NUMBER - dùng cùng tỷ lệ với template
        text_roi = {
            'y1': int(height * 0.3201),
            'y2': int(height * 0.52),
            'x1': int(width * 0.2996),
            'x2': int(width * 0.6493)
        }
        
        # Lấy vùng text 
        text_area = frame[text_roi['y1']:text_roi['y2'], text_roi['x1']:text_roi['x2']]
        
        # Debug: Kiểm tra template và vùng text
        if self.fight_number_template is None:
            print("ERROR: Template is None!")
            return False

        # Resize template để khớp với kích thước vùng text
        template_resized = cv2.resize(self.fight_number_template, (text_area.shape[1], text_area.shape[0]))

        max_val = 0
        try:
            # So khớp template với vùng text
            result = cv2.matchTemplate(text_area, template_resized, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)
        except Exception as e:
            print("Lỗi so sánh ảnh - Có thể hai ảnh hoàn toàn khác nhau!")

        if max_val >= 0.48:
            return True
        else:
            # Thử so thêm với template thứ 2
            if self.fight_number_template2 is None:
                print("ERROR: Template 2 is None!")
                return False
            template_resized2 = cv2.resize(self.fight_number_template2, 
                                    (text_area.shape[1], text_area.shape[0]))
            
            max_val2 = 0
            try:
                result2 = cv2.matchTemplate(text_area, template_resized2, cv2.TM_CCOEFF_NORMED)
                _, max_val2, _, _ = cv2.minMaxLoc(result2)
            except Exception as e:
                print("Lỗi so sánh ảnh 2 - Có thể hai ảnh hoàn toàn khác nhau!")

            if max_val2 >= 0.48:
                return True
            else:
                # Thử so thêm với template thứ 3
                if self.fight_number_template3 is None:
                    print("ERROR: Template 3 is None!")
                    return False
                template_resized3 = cv2.resize(self.fight_number_template3, 
                                    (text_area.shape[1], text_area.shape[0]))
                
                max_val3 = 0
                try:
                    result3 = cv2.matchTemplate(text_area, template_resized3, cv2.TM_CCOEFF_NORMED)
                    _, max_val3, _, _ = cv2.minMaxLoc(result3)
                except Exception as e:
                    print("Lỗi so sánh ảnh 3 - Có thể hai ảnh hoàn toàn khác nhau!")

                if max_val3 >= 0.48:
                    return True
        
        return False
    
    def detect_banner_and_result(self, frame):
        """Phát hiện cả banner START và kết quả - Copy từ main.py"""
        height, width = frame.shape[:2]
        
        # Vùng chứa chữ FIGHT NUMBER - dùng cùng tỷ lệ với template
        text_roi = {
            'y1': int(height * 0.3201),  # Giữ nguyên
            'y2': int(height * 0.52),     # Tăng lên để lấy được chữ NUMBER
            'x1': int(width * 0.2996),   # Giữ nguyên
            'x2': int(width * 0.6493)    # Giữ nguyên
        }
        
        # Lấy vùng text 
        text_area = frame[text_roi['y1']:text_roi['y2'], text_roi['x1']:text_roi['x2']]
        
        # Debug: Kiểm tra template và vùng text
        if self.fight_number_template is None:
            print("ERROR: Template is None!")
            return None

        # Resize template để khớp với kích thước vùng text
        template_resized = cv2.resize(self.fight_number_template, (text_area.shape[1], text_area.shape[0]))

        max_val = 0
        try:
            # So khớp template với vùng text
            result = cv2.matchTemplate(text_area, template_resized, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)

        except Exception as e:
            print("Lỗi so sánh ảnh - Có thể hai ảnh hoàn toàn khác nhau!")

        if max_val >= 0.48:
            return "START"
        else:
            # Thử so thêm với template thứ 2
            if self.fight_number_template2 is None:
                print("ERROR: Template 2 is None!")
                return None
            # Resize template để khớp với kích thước vùng text
            template_resized2 = cv2.resize(self.fight_number_template2, 
                                    (text_area.shape[1], text_area.shape[0]))
            
            max_val2 = 0
            try:
                result2 = cv2.matchTemplate(text_area, template_resized2, cv2.TM_CCOEFF_NORMED)
                _, max_val2, _, _ = cv2.minMaxLoc(result2)

            except Exception as e:
                print("Lỗi so sánh ảnh 2 - Có thể hai ảnh hoàn toàn khác nhau!")

            if max_val2 >= 0.48:
                return "START"
            else:
                # Thử so thêm với template thứ 3
                if self.fight_number_template3 is None:
                    print("ERROR: Template 3 is None!")
                    return None
                # Resize template để khớp với kích thước vùng text  
                template_resized3 = cv2.resize(self.fight_number_template3, 
                                    (text_area.shape[1], text_area.shape[0]))
                
                max_val3 = 0
                try:
                    result3 = cv2.matchTemplate(text_area, template_resized3, cv2.TM_CCOEFF_NORMED)
                    _, max_val3, _, _ = cv2.minMaxLoc(result3)

                except Exception as e:
                    print("Lỗi so sánh ảnh 3 - Có thể hai ảnh hoàn toàn khác nhau!")

                if max_val3 >= 0.48:
                    return "START"
        
        # Kiểm tra banner kết quả (copy từ main.py)
        result_roi = {
            'y1': int(height * 0.12),
            'y2': int(height * 0.88),
            'x1': int(width * 0.12),
            'x2': int(width * 0.88)
        }

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        roi_result = hsv[result_roi['y1']:result_roi['y2'], result_roi['x1']:result_roi['x2']]
        
        red_range1 = ([0, 150, 150], [10, 255, 255])
        red_range2 = ([170, 150, 150], [180, 255, 255])
        blue_range = ([115, 180, 180], [125, 255, 255])
        green_range1 = ([35, 100, 100], [45, 255, 255])
        green_range2 = ([45, 100, 100], [65, 255, 255])
        
        red_mask1 = cv2.inRange(roi_result, np.array(red_range1[0]), np.array(red_range1[1]))
        red_mask2 = cv2.inRange(roi_result, np.array(red_range2[0]), np.array(red_range2[1]))
        red_mask = cv2.bitwise_or(red_mask1, red_mask2)
        
        blue_mask = cv2.inRange(roi_result, np.array(blue_range[0]), np.array(blue_range[1]))
        
        green_mask1 = cv2.inRange(roi_result, np.array(green_range1[0]), np.array(green_range1[1]))
        green_mask2 = cv2.inRange(roi_result, np.array(green_range2[0]), np.array(green_range2[1]))
        green_mask = cv2.bitwise_or(green_mask1, green_mask2)
        
        total_pixels = roi_result.shape[0] * roi_result.shape[1]
        red_ratio = np.sum(red_mask) / 255 / total_pixels
        blue_ratio = np.sum(blue_mask) / 255 / total_pixels
        green_ratio = np.sum(green_mask) / 255 / total_pixels
        
        threshold = 0.4
        
        if red_ratio > threshold:
            return "D"
        elif blue_ratio > threshold:
            return "X"
        elif green_ratio > threshold:
            return "H"
        
        return None

    def find_first_scene_change(self, frame, reference_frame, threshold=0.25):
        """Tìm chuyển cảnh đầu tiên - Copy từ main.py"""
        try:
            # Chuyển sang grayscale để so sánh
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_reference = cv2.cvtColor(reference_frame, cv2.COLOR_BGR2GRAY)
            
            # Tính độ khác biệt
            diff = cv2.absdiff(gray_frame, gray_reference)
            mean_diff = np.mean(diff)
            
            return mean_diff > threshold
        except Exception as e:
            print(f"Lỗi tìm chuyển cảnh: {e}")
            return False

    def capture_screen_region(self):
        """Chụp vùng màn hình được cấu hình"""
        try:
            with mss.mss() as sct:
                monitor = {
                    "top": self.config['y1'],
                    "left": self.config['x1'],
                    "width": self.config['x2'] - self.config['x1'],
                    "height": self.config['y2'] - self.config['y1']
                }
                screenshot = sct.grab(monitor)
                frame = np.array(screenshot)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                return frame
        except Exception as e:
            print(f"Lỗi chụp màn hình: {e}")
            return None
    
    def click_at_position(self, point_name):
        """Click chuột tại vị trí được chỉ định - Sử dụng pyautogui"""
        try:
            # Lấy tọa độ từ config
            if point_name == "mo_cuoc":
                x, y = self.config['x_open_bet'], self.config['y_open_bet']
            elif point_name == "dong_cuoc":
                x, y = self.config['x_close_bet'], self.config['y_close_bet']
            elif point_name == "meron_thang":
                x, y = self.config['x_meron_win'], self.config['y_meron_win']
            elif point_name == "wala_thang":
                x, y = self.config['x_wala_win'], self.config['y_wala_win']
            elif point_name == "hoa":
                x, y = self.config['x_draw'], self.config['y_draw']
            elif point_name == "huy_tran":
                x, y = self.config['x_cancel'], self.config['y_cancel']
            else:
                print(f"Lỗi: Không tìm thấy điểm {point_name}")
                return False
            
            # Sử dụng pyautogui để click
            print(f"Đang click {point_name} tại ({x}, {y})...")
            pyautogui.moveTo(x, y, duration=0.1)  # Di chuyển chuột trong 0.1 giây
            pyautogui.click(x, y)  # Click chuột trái
            print(f"Đã click {point_name} tại ({x}, {y})")
            
            # Gửi thông báo click qua callback nếu có
            if hasattr(self, 'callback') and self.callback:
                click_names = {
                    "mo_cuoc": "Mở cược",
                    "dong_cuoc": "Đóng cược", 
                    "meron_thang": "Meron thắng",
                    "wala_thang": "Wala thắng",
                    "hoa": "Hòa",
                    "huy_tran": "Hủy trận"
                }
                click_name = click_names.get(point_name, point_name)
                self.callback("CLICK_EVENT", None, click_name, f"Đã click {click_name}")
            
            time.sleep(0.2)  # Delay 0.2 giây
                
            return True
        except Exception as e:
            print(f"Lỗi click chuột {point_name}: {e}")
            return False
    
    def force_reload_config(self):
        """Force reload config và in thông tin tọa độ hiện tại"""
        if self.reload_config():
            print(f"Tọa độ click hiện tại:")
            print(f"  Mở cược: ({self.config['x_open_bet']}, {self.config['y_open_bet']})")
            print(f"  Đóng cược: ({self.config['x_close_bet']}, {self.config['y_close_bet']})")
            print(f"  Meron thắng: ({self.config['x_meron_win']}, {self.config['y_meron_win']})")
            print(f"  Wala thắng: ({self.config['x_wala_win']}, {self.config['y_wala_win']})")
            print(f"  Hòa: ({self.config['x_draw']}, {self.config['y_draw']})")
            print(f"  Hủy trận: ({self.config['x_cancel']}, {self.config['y_cancel']})")
            return True
        return False
    
    def test_click(self, point_name):
        """Test click một điểm để kiểm tra xem có hoạt động không"""
        print(f"Test click {point_name}...")
        result = self.click_at_position(point_name)
        if result:
            print(f"✓ Test click {point_name} thành công!")
        else:
            print(f"✗ Test click {point_name} thất bại!")
        return result
    
    def detection_loop(self, callback=None):
        """Vòng lặp phát hiện real-time - Logic mới với auto click 6 điểm"""
        print("Bắt đầu phát hiện real-time...")
        
        while self.running:
            try:
                # Logic chính - giống main.py
                if not self.start_detected and not self.looking_for_scene_change and not self.waiting_for_result:
                    # Trạng thái: Tìm banner START và click ngay lập tức
                    frame = self.capture_screen_region()
                    if frame is None:
                        time.sleep(0.1)
                        continue
                        
                    # Tìm START và click ngay
                    if self.detect_start_banner(frame):
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] Phát hiện banner START!")
                        self.start_detected = True
                        self.start_time = time.time()
                        
                        # Chờ 2 giây trước khi click
                        # print("Chờ 2 giây trước khi click...")
                        # time.sleep(2)
                        
                        # Click "Mở cược" tự động ngay khi thấy START
                        if self.click_at_position("mo_cuoc"):
                            print("Đã click 'Mở cược'!")
                            self.auto_click_state = "BET_OPENED"
                            self.bet_open_time = time.time()
                        
                        if callback:
                            callback("START_DETECTED", frame)
                        
                        # Chuyển sang đợi 1 phút 58 giây
                        self.waiting_for_result = True
                        self.wait_start_time = time.time()
                        print("Bắt đầu đợi 1 phút 58 giây...")
                
                elif self.start_detected and not self.looking_for_scene_change and self.waiting_for_result:
                    # Trạng thái: Đợi 1 phút 58 giây - KHÔNG TÌM KẾT QUẢ (giống "Bắt đầu xử lý")
                    elapsed_time = time.time() - self.wait_start_time
                    
                    # Kiểm tra xem có cần đóng cược sau 45 giây không
                    if (self.auto_click_state == "BET_OPENED" and 
                        self.bet_open_time and 
                        time.time() - self.bet_open_time >= self.BET_DURATION):
                        
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] Đã đủ 45 giây - Click 'Đóng cược'")
                        if self.click_at_position("dong_cuoc"):
                            print("Đã click 'Đóng cược'!")
                            self.auto_click_state = "BET_CLOSED"
                    
                    if elapsed_time >= self.MIN_MATCH_DURATION:
                        # Đã đủ 1 phút 58 giây, bây giờ tìm kết quả liên tục
                        if not hasattr(self, 'searching_for_result'):
                            print(f"[{datetime.now().strftime('%H:%M:%S')}] Đã đủ 1 phút 58 giây - Bắt đầu tìm kết quả liên tục")
                            self.searching_for_result = True
                        
                        # Tìm kết quả liên tục
                        frame = self.capture_screen_region()
                        if frame is not None:
                            result = self.detect_banner_and_result(frame)
                            
                            if result == "START":
                                # Trận đấu bị hủy - Phát hiện START mới
                                print(f"[{datetime.now().strftime('%H:%M:%S')}] Trận đấu bị hủy - Phát hiện START mới")
                                
                                # Click "Hủy trận" trước khi reset
                                if self.auto_click_state in ["BET_OPENED", "BET_CLOSED"]:
                                    print("Click 'Hủy trận' do trận bị hủy")
                                    self.click_at_position("huy_tran")
                                
                                if callback:
                                    callback("RESULT_DETECTED", frame, "CANCEL", "Trận đấu bị hủy")
                                
                                # Bắt đầu trận mới ngay lập tức với START vừa phát hiện
                                # Click "Mở cược" ngay cho trận mới
                                self.start_detected = True
                                self.start_time = time.time()
                                
                                # # Chờ 2 giây rồi click "Mở cược" cho trận mới
                                # print("Chờ 2 giây rồi click 'Mở cược' cho trận mới...")
                                # time.sleep(2)
                                
                                if self.click_at_position("mo_cuoc"):
                                    print("Đã click 'Mở cược' cho trận mới!")
                                    self.auto_click_state = "BET_OPENED"
                                    self.bet_open_time = time.time()
                                
                                self.waiting_for_result = True
                                self.wait_start_time = time.time()
                                self.searching_for_result = False
                                
                                if callback:
                                    callback("START_DETECTED", frame)
                                
                            elif result in ["D", "X", "H"]:
                                # Phát hiện kết quả - click kết quả tương ứng
                                result_text = {
                                    "D": "Meron thắng",
                                    "X": "Wala thắng", 
                                    "H": "Hòa"
                                }.get(result, result)
                                print(f"[{datetime.now().strftime('%H:%M:%S')}] Phát hiện kết quả: {result_text} ({result})")
                                
                                # Click kết quả tương ứng
                                if result == "D":
                                    self.click_at_position("meron_thang")
                                elif result == "X":
                                    self.click_at_position("wala_thang")
                                elif result == "H":
                                    self.click_at_position("hoa")
                                
                                if callback:
                                    callback("RESULT_DETECTED", frame, result, result_text)
                                
                                # Reset để tìm trận tiếp theo
                                print(f"[{datetime.now().strftime('%H:%M:%S')}] Reset để tìm trận tiếp theo")
                                self.start_detected = False
                                self.looking_for_scene_change = False
                                self.waiting_for_result = False
                                self.start_time = None
                                self.wait_start_time = None
                                self.reference_frame = None
                                self.searching_for_result = False
                                self.auto_click_state = "WAITING_START"
                                self.bet_open_time = None
                                
                                if callback:
                                    callback("RESET_COMPLETE", None)
                            else:
                                # Chưa phát hiện gì - tiếp tục tìm
                                time.sleep(0.5)  # Tìm mỗi 0.5 giây
                                continue
                    else:
                        # Chưa đủ 1 phút 58 giây - CHỈ ĐỢI, KHÔNG TÌM KẾT QUẢ
                        remaining = self.MIN_MATCH_DURATION - elapsed_time
                        
                        # Hiển thị thời gian còn lại mỗi 30 giây
                        if int(elapsed_time) % 30 == 0:
                            print(f"Đang đợi... còn {int(remaining)} giây")
                        
                        # Ngủ 1 giây để tiết kiệm tài nguyên
                        time.sleep(1)
                        continue
                
                # Delay chỉ khi đang tìm START hoặc tìm chuyển cảnh
                if not self.waiting_for_result:
                    time.sleep(0.1)  # 10 FPS
                
            except Exception as e:
                print(f"Lỗi trong detection loop: {e}")
                time.sleep(0.1)
        
        print("Dừng phát hiện real-time.")
    
    def start_detection(self, callback=None):
        """Bắt đầu phát hiện real-time"""
        if self.running:
            print("Đang chạy rồi!")
            return
        
        # Lưu callback để sử dụng trong click_at_position
        self.callback = callback
        
        # Reset trạng thái
        self.start_detected = False
        self.looking_for_scene_change = False
        self.waiting_for_result = False
        self.start_time = None
        self.wait_start_time = None
        self.reference_frame = None
        self.searching_for_result = False
        self.auto_click_state = "WAITING_START"
        self.bet_open_time = None
        
        self.running = True
        self.detection_thread = threading.Thread(target=self.detection_loop, args=(callback,))
        self.detection_thread.daemon = True
        self.detection_thread.start()
        print("Đã bắt đầu thread phát hiện real-time")
    
    def stop_detection(self):
        """Dừng phát hiện real-time"""
        self.running = False
        if self.detection_thread:
            self.detection_thread.join(timeout=1)
        
        # Reset trạng thái
        self.start_detected = False
        self.looking_for_scene_change = False
        self.waiting_for_result = False
        self.start_time = None
        self.wait_start_time = None
        self.reference_frame = None
        self.searching_for_result = False
        self.auto_click_state = "WAITING_START"
        self.bet_open_time = None
        
        print("Đã dừng phát hiện real-time")

# Test function
if __name__ == "__main__":
    detector = RealTimeDetector()
    
    def callback(event, frame):
        print(f"Event: {event}")
    
    try:
        detector.start_detection(callback)
        print("Nhấn Ctrl+C để dừng...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        detector.stop_detection()
        print("Đã dừng.")
