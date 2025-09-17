import cv2
import numpy as np
from datetime import datetime
import random
import os
import time
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from threading import Thread
from detect_start_real_time import RealTimeDetector
from add_point_xy import set_single_click_point_gui
# from skimage.metrics import structural_similarity as ssim

class VideoProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Processor")
        self.root.geometry("600x600")
        
        # Căn giữa cửa sổ
        # Lấy kích thước màn hình
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # Tính toán vị trí để căn giữa
        window_width = 600
        window_height = 400
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Đặt vị trí cửa sổ
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Frame chính
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Nút chọn thư mục chứa nhiều video
        self.dir_path = tk.StringVar()
        ttk.Label(main_frame, text="Thư mục video đầu vào:").pack(anchor=tk.W)
        dir_frame = ttk.Frame(main_frame)
        dir_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.dir_entry = ttk.Entry(dir_frame, textvariable=self.dir_path)
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(dir_frame, text="Chọn thư mục", command=self.browse_file).pack(side=tk.RIGHT)
        

        self.file_path = None

        self.stt_video_cho_thu_muc = 0
        
        # Frame chứa nút và label cú pháp đặt tên
        name_frame = ttk.Frame(main_frame)
        name_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Label hiển thị cú pháp đặt tên
        self.name_label = ttk.Label(name_frame, text="Cú pháp đặt tên: [đội thắng]_[ngày tháng năm]_[tên nhóm]_[stt]_[giờ phút bắt đầu trận đấu]")
        self.name_label.pack(side=tk.LEFT)
        
        # Thêm biến cho việc đặt tên
        self.name_value1 = None  # Giá trị text - lấy từ tên video, khi chạy video mới sẽ lấy tên video gán cho giá trị này
        self.name_value3_start = 1  # Giá trị số bắt đầu - mỗi lần chạy video mới sẽ reset lại 1
        
        # Thêm thanh tiến trình
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, 
            variable=self.progress_var, 
            maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
 
        # Frame chứa 2 nút xử lý
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        # Nút xử lý
        self.start_button = ttk.Button(button_frame, text="Bắt đầu xử lý", command=self.start_processing)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))

        # Nút xử lý với logic mới
        self.start_button_new = ttk.Button(button_frame, text="Bắt đầu xử lý (New)", command=self.start_processing_new, style="Accent.TButton")
        self.start_button_new.pack(side=tk.LEFT)

        # Nút detect auto có màu đỏ nổi bật
        self.detect_button = tk.Button(main_frame, text="Auto Detect", command=self.toggle_detection, bg="red", fg="white", font=("Arial", 12))
        self.detect_button.pack(pady=5)
        
        # Frame chứa cài đặt thời gian đóng cược
        bet_duration_frame = ttk.Frame(main_frame)
        bet_duration_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(bet_duration_frame, text="Thời gian đóng cược (giây):").pack(side=tk.LEFT)
        self.bet_duration_var = tk.StringVar(value="45")  # Giá trị mặc định
        self.bet_duration_entry = ttk.Entry(bet_duration_frame, textvariable=self.bet_duration_var, width=10)
        self.bet_duration_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # Nút cập nhật thời gian
        self.update_duration_button = ttk.Button(bet_duration_frame, text="Cập nhật", command=self.update_bet_duration)
        self.update_duration_button.pack(side=tk.LEFT, padx=(5, 0))
        
        # Frame chứa 6 nút set click
        click_frame = ttk.LabelFrame(main_frame, text="Thiết lập điểm click", padding="5")
        click_frame.pack(fill=tk.X, pady=5)
        
        # Nút Set Mở cược (màu cam)
        self.set_open_bet_button = tk.Button(click_frame, text="Set Mở cược", command=lambda: self.set_click_point("open_bet"), 
                                            bg="orange", fg="white", font=("Arial", 10))
        self.set_open_bet_button.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Nút Set Đóng cược (màu cam)
        self.set_close_bet_button = tk.Button(click_frame, text="Set Đóng cược", command=lambda: self.set_click_point("close_bet"), 
                                             bg="orange", fg="white", font=("Arial", 10))
        self.set_close_bet_button.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Nút Set Meron thắng (màu đỏ)
        self.set_meron_win_button = tk.Button(click_frame, text="Set Meron thắng", command=lambda: self.set_click_point("meron_win"), 
                                             bg="red", fg="white", font=("Arial", 10))
        self.set_meron_win_button.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Nút Set Wala thắng (màu xanh dương)
        self.set_wala_win_button = tk.Button(click_frame, text="Set Wala thắng", command=lambda: self.set_click_point("wala_win"), 
                                            bg="blue", fg="white", font=("Arial", 10))
        self.set_wala_win_button.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Nút Set Hòa (màu xanh lá)
        self.set_draw_button = tk.Button(click_frame, text="Set Hòa", command=lambda: self.set_click_point("draw"), 
                                        bg="green", fg="white", font=("Arial", 10))
        self.set_draw_button.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Nút Set Hủy trận (màu đỏ)
        self.set_cancel_button = tk.Button(click_frame, text="Set Hủy trận", command=lambda: self.set_click_point("cancel"), 
                                          bg="red", fg="white", font=("Arial", 10))
        self.set_cancel_button.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Khung log
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar cho log
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        # Trạng thái xử lý
        self.processing = False
        
        # Load và cắt template FIGHT NUMBER
        template_full = cv2.imread('fight_number_template.png')
        if template_full is None:
            raise Exception("Không thể load template fight_number_template.png")
        
        height, width = template_full.shape[:2]
        text_roi = {
            'y1': int(height * 0.3201),  # Giữ nguyên
            'y2': int(height * 0.52),     # Tăng lên để lấy được chữ NUMBER
            'x1': int(width * 0.2996),   # Giữ nguyên
            'x2': int(width * 0.6493)    # Giữ nguyên
        }
        # Cắt vùng chứa chữ FIGHT NUMBER từ template không cần chuyển qua xám
        self.fight_number_template = template_full[text_roi['y1']:text_roi['y2'], 
                         text_roi['x1']:text_roi['x2']]

        #hình mẫu thứ 2
        template_full2 = cv2.imread('fight_number_template2.png')
        if template_full2 is None:
            raise Exception("Không thể load template fight_number_template2.png")
        
        height2, width2 = template_full2.shape[:2]
        text_roi2 = {
            'y1': int(height2 * 0.3201),  # Giữ nguyên
            'y2': int(height2 * 0.52),     # Tăng lên để lấy được chữ NUMBER
            'x1': int(width2 * 0.2996),   # Giữ nguyên
            'x2': int(width2 * 0.6493)    # Giữ nguyên
        }
        
        # Cắt vùng chứa chữ FIGHT NUMBER từ template không cần chuyển qua xám
        self.fight_number_template2 = template_full2[text_roi2['y1']:text_roi2['y2'], 
                         text_roi2['x1']:text_roi2['x2']]


        # hình mẫu thứ 3
        template_full3 = cv2.imread('fight_number_template3.png')
        if template_full3 is None:
            raise Exception("Không thể load template fight_number_template3.png")
        
        height3, width3 = template_full3.shape[:2]
        text_roi3 = {
            'y1': int(height3 * 0.3201),  # Giữ nguyên
            'y2': int(height3 * 0.52),     # Tăng lên để lấy được chữ NUMBER
            'x1': int(width3 * 0.2996),   # Giữ nguyên
            'x2': int(width3 * 0.6493)    # Giữ nguyên
        }
        
        
        # Cắt vùng chứa chữ FIGHT NUMBER từ template không cần chuyển qua xám
        self.fight_number_template3 = template_full3[text_roi3['y1']:text_roi3['y2'], 
                         text_roi3['x1']:text_roi3['x2']]
        
        
        # self.template_h2, self.template_w2 = self.fight_number_template2.shape
        # hiển thị lên màn hình để xem có cắt đúng không 
        # cv2.imshow('fight_number_template', self.fight_number_template)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()


        #test
        # result_roi = {
        #     'y1': int(height * 0.12), #phần chiều cao phía trên, giảm sẽ lấy được nhiều hơn
        #     'y2': int(height * 0.74), #phần chiều cao phía dưới, tăng lên sẽ lấy được nhiều hơn xuống dưới
        #     'x1': int(width * 0.1), #phần chiều rộng phía trái, giảm  sẽ lấy được nhiều hơn trái
        #     'x2': int(width * 0.73) #phần chiều rộng phía phải, tăng lên sẽ lấy được nhiều hơn phải
        # }

        # #load ảnh test
        # img_test = cv2.imread('HOA2.png')
        # img_test = img_test[result_roi['y1']:result_roi['y2'], result_roi['x1']:result_roi['x2']]

        # cv2.imshow('img_test', img_test)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        #end test

        # Thêm biến fps global
        self.fps_global = None

        # Thêm biến để kiểm soát thread
        self.running = False
        
        # Load template ảnh mẫu cho logic mới (tối ưu hiệu suất)
        self.template_red_new = cv2.imread('template_do_new.png')
        self.template_blue_new = cv2.imread('template_xanh_new.png')
        self.template_green_new = cv2.imread('template_hoa_new.png')
        
        # Kiểm tra template có load được không
        if self.template_red_new is None or self.template_blue_new is None or self.template_green_new is None:
            print("Lỗi: Không thể load template ảnh mẫu cho logic mới!")
            self.template_red_new = None
            self.template_blue_new = None
            self.template_green_new = None
        
        # Thêm xử lý sự kiện đóng cửa sổ
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Thêm biến cho real-time detector
        self.real_time_detector = None
        self.detection_running = False
        
        # Thêm biến cho click point setter
        self.click_point_setter = None
        self.click_point_thread = None

    def on_closing(self):
        """Xử lý khi đóng chương trình"""
        if self.processing:
            if messagebox.askokcancel("Đang xử lý", "Đang trong quá trình xử lý. Bạn có chắc muốn thoát?"):
                self.running = False
                self.processing = False
                self.root.after(100, self.root.destroy)
        else:
            # Dừng detect real-time nếu đang chạy
            if self.detection_running:
                self.stop_real_time_detection()
            # Dừng click point setter nếu đang chạy
            if self.click_point_setter:
                self.click_point_setter.stop_monitoring()
            self.root.destroy()

    def log(self, message):
        """Thread-safe logging"""
        self.root.after(0, self._log, message)
        
    def _log(self, message):
        """Actual logging in main thread"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)

    def update_progress(self, value):
        """Thread-safe progress update"""
        self.root.after(0, self._update_progress, value)
        
    def _update_progress(self, value):
        """Actual progress update in main thread"""
        self.progress_var.set(value)

    def browse_file(self):
        dirname = filedialog.askdirectory(
            title="Chọn thư mục",
            initialdir=os.getcwd()
        )
        if dirname:
            self.dir_path.set(dirname)

    def show_name_dialog(self):
        # Tạo cửa sổ dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Đặt tên")
        dialog.geometry("300x170")
        
        # Căn giữa dialog
        dialog.transient(self.root)
        dialog.grab_set()
        x = self.root.winfo_x() + (self.root.winfo_width() - 300) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 170) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Frame chứa các widget
        frame = ttk.Frame(dialog, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Ô nhập text
        ttk.Label(frame, text="Tên nhóm:").pack(anchor=tk.W)
        text_entry = ttk.Entry(frame)
        text_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Ô nhập số
        ttk.Label(frame, text="STT:").pack(anchor=tk.W)
        number_entry = ttk.Entry(frame)
        number_entry.pack(fill=tk.X, pady=(0, 10))
        
        # def validate_and_save():
        #     text = text_entry.get().strip()
        #     try:
        #         number = int(number_entry.get().strip())
        #         if text and number >= 0:
        #             self.name_value1 = text
        #             self.name_value3_start = number
        #             self.current_value3 = number
                    
        #             # Cập nhật label mẫu
        #             example = f"Ví dụ: D_140324_{text}_{number}_123"
        #             self.name_label.config(text=f"Cú pháp đặt tên: {example}")
                    
        #             dialog.destroy()
        #         else:
        #             tk.messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin hợp lệ!")
        #     except ValueError:
        #         tk.messagebox.showerror("Lỗi", "Giá trị STT phải là số nguyên!")
        
        # # Nút OK
        # ttk.Button(frame, text="OK", command=validate_and_save).pack(pady=10)

    def start_processing(self):
        if self.processing:
            self.log("Đang xử lý, vui lòng đợi...")
            return
            
        if not self.dir_path.get():
            self.log("Vui lòng chọn thư mục video!")
            return
            
        # if self.name_value1 is None or self.name_value3_start is None:
        #     self.log("Vui lòng đặt tên trước khi xử lý!")
        #     return
 
        self.processing = True
        self.running = True  # Set running = True khi bắt đầu
        self.start_button.config(state=tk.DISABLED)
        self.log_text.delete(1.0, tk.END)
        
        # Tạo thread mới để xử lý tất cả video
        process_thread = Thread(target=self.process_all_videos)
        process_thread.start()

    def start_processing_new(self):
        """Bắt đầu xử lý với logic mới (không có banner START)"""
        if self.processing:
            self.log("Đang xử lý, vui lòng đợi...")
            return
            
        if not self.dir_path.get():
            self.log("Vui lòng chọn thư mục video!")
            return
 
        self.processing = True
        self.running = True
        self.start_button_new.config(state=tk.DISABLED)
        self.log_text.delete(1.0, tk.END)
        
        # Tạo thread mới để xử lý tất cả video với logic mới
        process_thread = Thread(target=self.process_all_videos_new)
        process_thread.start()

    def process_all_videos(self):
        """Hàm xử lý tất cả video trong thư mục"""
        try:
            self.stt_video_cho_thu_muc = 0
            
            # Chỉ xử lý file video trong thư mục chính, không xử lý thư mục con
            video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v']
            
            for file in os.listdir(self.dir_path.get()):
                if not self.running:  # Kiểm tra có lệnh dừng không
                    print("Đã dừng xử lý!")
                    break
                
                # Kiểm tra xem có phải file video không
                file_lower = file.lower()
                is_video = any(file_lower.endswith(ext) for ext in video_extensions)
                
                if not is_video:
                    continue  # Bỏ qua file không phải video
                
                # Kiểm tra xem có phải thư mục không
                file_path = os.path.join(self.dir_path.get(), file)
                if os.path.isdir(file_path):
                    continue  # Bỏ qua thư mục con
                    
                self.file_path = file_path
                self.log("\n--------------------------------")
                self.log(f"Đang xử lý: {self.file_path}")

                # Lấy tên video để đặt tên thư mục kết quả
                self.name_value1 = os.path.splitext(file)[0]
                
                self.stt_video_cho_thu_muc += 1
                self.process_video()  # Xử lý trực tiếp
                
            # Hiển thị thông báo khi hoàn thành
            self.root.after(0, self.show_completion_message)
            
        except Exception as e:
            self.log(f"Lỗi: {str(e)}")
        finally:
            self.processing = False
            self.running = False  # Reset running khi kết thúc

    def process_all_videos_new(self):
        """Hàm xử lý tất cả video trong thư mục với logic mới"""
        try:
            # Chỉ xử lý file video trong thư mục chính, không xử lý thư mục con
            video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v']
            
            for file in os.listdir(self.dir_path.get()):
                if not self.running:
                    print("Đã dừng xử lý!")
                    break
                
                # Kiểm tra xem có phải file video không
                file_lower = file.lower()
                is_video = any(file_lower.endswith(ext) for ext in video_extensions)
                
                if not is_video:
                    continue  # Bỏ qua file không phải video
                
                # Kiểm tra xem có phải thư mục không
                file_path = os.path.join(self.dir_path.get(), file)
                if os.path.isdir(file_path):
                    continue  # Bỏ qua thư mục con
                    
                self.file_path = file_path
                self.log("\n--------------------------------")
                self.log(f"Đang xử lý: {self.file_path}")

                # Lấy tên video để đặt tên thư mục kết quả
                self.name_value1 = os.path.splitext(file)[0]
                
                self.process_video_new_logic()
                
            # Hiển thị thông báo khi hoàn thành
            self.root.after(0, self.show_completion_message_new)
            
        except Exception as e:
            self.log(f"Lỗi: {str(e)}")
        finally:
            self.processing = False
            self.running = False

    def show_completion_message_new(self):
        """Hiển thị thông báo hoàn thành trong main thread cho logic mới"""
        if tk.messagebox.showinfo("Thành công", "Đã xử lý xong!"):
            os.startfile(self.dir_path.get())
        self.start_button_new.config(state=tk.NORMAL)

    def show_completion_message(self):
        """Hiển thị thông báo hoàn thành trong main thread"""
        if tk.messagebox.showinfo("Thành công", "Đã xử lý xong!"):
            # Mở thư mục dir_path
            os.startfile(self.dir_path.get())
        self.start_button.config(state=tk.NORMAL)

    def detect_banner_color(self, frame):
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
        # template_resized2 = cv2.resize(self.fight_number_template2, (text_area.shape[1], text_area.shape[0]))
        # template_resized3 = cv2.resize(self.fight_number_template3, (text_area.shape[1], text_area.shape[0]))

        # hiển thị lên màn hình
        # cv2.imshow('current', text_area)
        # cv2.imshow('tmp', template_resized)
        # cv2.imshow('tmp2', template_resized2)
        # cv2.imshow('tmp3', template_resized3)
        # cv2.waitKey(100)
        # cv2.destroyAllWindows()

        max_val = 0
        try:
            # So khớp template với vùng text
            result = cv2.matchTemplate(text_area, template_resized, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)

        except Exception as e:
            print("Lỗi so sánh ảnh - Có thể hai ảnh hoàn toàn khác nhau!")

        # print(f"1. max_val: {max_val}")
        if max_val >= 0.48:
            return "START"
        else:
            # Thử so thêm với template thứ 2
            if self.fight_number_template2 is None:
                print("ERROR: Template is None!")
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

            # print(f"2. max_val2: {max_val2}")
            if max_val2 >= 0.48:
                return "START"
            else:
                # Thử so thêm với template thứ 3
                if self.fight_number_template3 is None:
                    print("ERROR: Template is None!")
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

                # print(f"3. max_val3: {max_val3}")
                if max_val3 >= 0.48:
                    return "START"
        
        # Kiểm tra banner kết quả (giữ nguyên code cũ)
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

    def detect_result_banner_new(self, frame):
        """Phát hiện banner kết quả (X, D, H) - Sử dụng Template Matching tối ưu cho logic mới"""
        
        # Kiểm tra template đã load chưa
        if self.template_red_new is None or self.template_blue_new is None or self.template_green_new is None:
            print("Lỗi: Template chưa được load!")
            return None
        
        height, width = frame.shape[:2]
        
        # ROI cho banner kết quả (toàn bộ frame như template)
        result_roi = {
            'y1': 0,        # Toàn bộ chiều cao
            'y2': height,   # Toàn bộ chiều cao
            'x1': 0,        # Toàn bộ chiều rộng
            'x2': width     # Toàn bộ chiều rộng
        }
        
        # Lấy vùng ROI từ frame (toàn bộ frame)
        roi_area = frame[result_roi['y1']:result_roi['y2'], result_roi['x1']:result_roi['x2']]
        
        # Sử dụng template gốc (không cần resize vì cùng kích thước)
        template_red_resized = self.template_red_new
        template_blue_resized = self.template_blue_new
        template_green_resized = self.template_green_new
        
        # Template matching cho từng màu (so sánh toàn bộ frame)
        result_red = cv2.matchTemplate(roi_area, template_red_resized, cv2.TM_CCOEFF_NORMED)
        result_blue = cv2.matchTemplate(roi_area, template_blue_resized, cv2.TM_CCOEFF_NORMED)
        result_green = cv2.matchTemplate(roi_area, template_green_resized, cv2.TM_CCOEFF_NORMED)
        
        # Lấy điểm matching cao nhất
        _, max_val_red, _, _ = cv2.minMaxLoc(result_red)
        _, max_val_blue, _, _ = cv2.minMaxLoc(result_blue)
        _, max_val_green, _, _ = cv2.minMaxLoc(result_green)
        
        # Ngưỡng matching (giảm xuống như main.py)
        threshold = 0.5  # Giảm từ 0.8 xuống 0.5
        
        # Debug: In giá trị matching (chỉ khi có giá trị cao - tối ưu)
        if max_val_red > 0.4 or max_val_blue > 0.4 or max_val_green > 0.4:
            print(f"Red: {max_val_red:.3f}, Blue: {max_val_blue:.3f}, Green: {max_val_green:.3f}")
        
        # Kiểm tra kết quả matching
        if max_val_red > threshold and max_val_red > max_val_blue and max_val_red > max_val_green:
            return "D"  # MERON WINS (Đỏ)
        elif max_val_blue > threshold and max_val_blue > max_val_red and max_val_blue > max_val_green:
            return "X"  # WALA WINS (Xanh)
        elif max_val_green > threshold and max_val_green > max_val_red and max_val_green > max_val_blue:
            return "H"  # HÒA (Xanh lá)
        
        return None

    def check_real_fps(self, input_video):
        cap = cv2.VideoCapture(input_video)
        if not cap.isOpened():
            return 0
        
        # Lấy FPS từ metadata của video
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        duration = total_frames / fps if fps > 0 else 0
        
        cap.release()
        
        # self.log(f"Metadata video:")
        print(f"- FPS: {fps}")
        # self.log(f"- Total frames: {total_frames}")
        # self.log(f"- Duration: {duration:.2f} seconds\n")
        
        return fps

    def process_video(self): 
        try:
            self.running = True
            input_video = self.file_path

            # Tạo thư mục kết quả
            name_folder = self.name_value1
            #chuyển name thành in hoa
            # name_folder = name_folder.upper()

            time_folder = datetime.now().strftime('%d%m%y_%H.%M')

            # stt_folder = self.stt_video_cho_thu_muc

            # Tạo thư mục nằm trong thư mục dir_path
            tmp_output_dir = f"{name_folder}_{time_folder}_VIDEO"
            output_dir = os.path.join(self.dir_path.get(), tmp_output_dir)
            os.makedirs(output_dir, exist_ok=True)

            # Tạo thư mục output_dir_picture nằm trong thư mục output_dir
            tmp_dir = f"{name_folder}_{time_folder}_PICTURE"
            output_dir_picture = os.path.join(output_dir, tmp_dir)
            os.makedirs(output_dir_picture, exist_ok=True)
            
            # Kiểm tra video
            cap = cv2.VideoCapture(input_video)
            if not cap.isOpened():
                self.log("Lỗi: Không thể mở video!")
                return
            cap.release()
            
            # self.log("Đang phân tích video...\n")

            fps_real = self.check_real_fps(input_video)

            self.fps_global = fps_real

            timestamps = self.process_video_file(input_video, output_dir_picture)
            # self.log(f"Tìm thấy {len(timestamps)} đoạn cần cắt")
            
            if timestamps:
                self.log("Bắt đầu cắt video...")
                self.cut_video_file(input_video, timestamps, output_dir)
                self.log("Hoàn thành!")
                
                # # Hiển thị thông báo và mở thư mục kết quả khi nhấn OK
                # if tk.messagebox.showinfo("Thành công", 
                #     f"Đã xử lý xong!\nKết quả được lưu trong thư mục: {output_dir}"):
                #     os.startfile(output_dir)  # Mở thư mục kết quả
                #     # enable button
                #     self.start_button.config(state=tk.NORMAL)
            else:
                self.log("Không tìm thấy đoạn nào để cắt")
                # enable button
                self.start_button.config(state=tk.NORMAL)
                
        except Exception as e:
            self.log(f"Lỗi: {str(e)}")
            tk.messagebox.showerror("Lỗi", str(e))
        finally:
            self.processing = False
            # self.running = False
            if 'cap' in locals():
                cap.release()

    def process_video_new_logic(self):
        """Xử lý video với logic mới - không có banner START"""
        try:
            input_video = self.file_path

            # Tạo thư mục kết quả
            name_folder = self.name_value1
            time_folder = datetime.now().strftime('%d%m%y_%H.%M')
            tmp_output_dir = f"{name_folder}_{time_folder}_VIDEO"
            output_dir = os.path.join(self.dir_path.get(), tmp_output_dir)
            os.makedirs(output_dir, exist_ok=True)

            # Tạo thư mục output_dir_picture
            tmp_dir = f"{name_folder}_{time_folder}_PICTURE"
            output_dir_picture = os.path.join(output_dir, tmp_dir)
            os.makedirs(output_dir_picture, exist_ok=True)
            
            # Kiểm tra video
            cap = cv2.VideoCapture(input_video)
            if not cap.isOpened():
                self.log("Lỗi: Không thể mở video!")
                return
            cap.release()
            
            # Lấy FPS
            fps_real = self.check_real_fps(input_video)
            self.fps_global = fps_real

            # Xử lý với logic mới
            timestamps = self.process_video_file_new_logic(input_video, output_dir_picture)
            
            if timestamps:
                self.log("Bắt đầu cắt video...")
                self.cut_video_file_new_logic(input_video, timestamps, output_dir)
                self.log("Hoàn thành!")
            else:
                self.log("Không tìm thấy đoạn nào để cắt")
                
        except Exception as e:
            self.log(f"Lỗi: {str(e)}")
            tk.messagebox.showerror("Lỗi", str(e))
        finally:
            self.processing = False

    # process_video_file: quét toàn bộ video tìm các đoạn cần cắt trả về list các tuple (start_frame, first_scene_frame, end_frame, result)
    def process_video_file(self, input_path, output_dir_picture):  
        cap = cv2.VideoCapture(input_path)
        timestamps = []
        current_match = None
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        processed_frames = 0
        
        # # Debug thông tin video
        # self.log(f"\nThông tin video:")
        # self.log(f"- Total frames: {total_frames}")
        # self.log(f"- FPS: {self.fps_global}")
        
        # Dùng fps_global
        MIN_MATCH_DURATION = 2 * 60 * 1000  # 2 phút trong milliseconds
        
        # Trạng thái tìm kiếm
        FINDING_START = 0   # Đang tìm frame bắt đầu
        FINDING_RESULT = 1  # Đang tìm frame kết quả
        current_state = FINDING_START

        stt_tmp = self.name_value3_start

        #test nhảy đến tiếng thứ 0, phút thứ 15, giây thứ 49    
        # cap.set(cv2.CAP_PROP_POS_MSEC, 15 * 60 * 1000 + 49 * 1000)
    
        while cap.isOpened():
            if not self.running:  # Kiểm tra có lệnh dừng không
                break
            ret, frame = cap.read()
            if not ret:
                break
            
            # Lấy thời gian của frame hiện tại (milliseconds)
            frame_time = cap.get(cv2.CAP_PROP_POS_MSEC)  # Thay vì dùng frame index
            
            processed_frames += 1
            
            # Cập nhật thanh tiến trình 60 frame 1 lần
            if processed_frames % 60 == 0:
                progress = (processed_frames / total_frames) * 100
                self.update_progress(progress)
                self.log_text.see(tk.END)
                self.root.update()

            banner_type = self.detect_banner_color(frame)
            if banner_type:
                if current_state == FINDING_START:
                    if banner_type == "START":
                        # Debug chi tiết
                        # self.log("\nDebug frame START:")
                        # self.log(f"Frame time (ms): {frame_time}")
                        
                        timecode = self.msec_to_timecode(frame_time)  # Hàm mới
                        # self.log(f"Phát hiện bắt đầu tại {timecode}")
                        
                        # Lưu ảnh frame này chỉ lấy giờ và phút của timecode bỏ giây đi
                        date_str = datetime.now().strftime("%d%m%y")
                        filename = f"{date_str}_{self.name_value1}_{stt_tmp}a_{timecode[:-3]}.jpg"
                        try:
                            cv2.imwrite(os.path.join(output_dir_picture, filename), frame)
                            # stt_tmp += 1
                        except Exception as e:
                            print(f"Lỗi khi lưu ảnh START: {str(e)}")
                        
                        # lưu thêm first_scene_time
                        first_scene_frame = self.find_first_scene_change(input_path, frame_time)
                        
                        timecode = self.msec_to_timecode(first_scene_frame)
                        # self.log(f"Phát hiện chuyển cảnh tại {timecode}")
                        
                        if current_match:
                            timestamps.append((current_match[0], frame_time, first_scene_frame, None))
                        current_match = (frame_time, None)
                        current_state = FINDING_RESULT
                        
                        # Skip 2 phút
                        skip_to_frame = frame_time + MIN_MATCH_DURATION
                        cap.set(cv2.CAP_PROP_POS_MSEC, skip_to_frame)

                        # Cập nhật processed_frames dựa trên số frame đã xử lý
                        current_frame_pos = cap.get(cv2.CAP_PROP_POS_FRAMES)
                        processed_frames = int(current_frame_pos)

                        # Cập nhật progress bar
                        progress = (processed_frames / total_frames) * 100
                        self.update_progress(progress)
                        self.log_text.see(tk.END)
                        self.root.update()
                
                elif current_state == FINDING_RESULT:
                    #nếu đanng cần tìm kết quả mà lại phát hiện trận bắt đầu thì result là CANCEL (trận này bị hủy)
                    if banner_type == "START":
                        timecode = self.msec_to_timecode(frame_time-3000)
                        self.log(f"TRẬN ĐẤU BỊ HỦY {timecode}\n")
                        
                        #lưu ảnh kết quả
                        date_str = datetime.now().strftime("%d%m%y")
                        filename = f"{date_str}_{self.name_value1}_{stt_tmp}CANCEL_{timecode[:-3]}.jpg"
                        try:
                            cv2.imwrite(os.path.join(output_dir_picture, filename), frame)
                            stt_tmp += 1
                        except Exception as e:
                            print(f"Lỗi khi lưu ảnh kết quả: {str(e)}")
                        
                        current_match = (current_match[0], first_scene_frame, frame_time-3000, "CANCEL")
                        timestamps.append(current_match)
                        current_match = None
                        current_state = FINDING_START
                    
                    elif banner_type in ["D", "X", "H"]:
                        timecode = self.msec_to_timecode(frame_time)
                        result_type = {
                            "D": "Đỏ thắng",
                            "X": "Xanh thắng",
                            "H": "Hòa"
                        }
                        # self.log(f"Phát hiện {result_type[banner_type]} tại {timecode}\n")

                        #lưu ảnh kết quả
                        date_str = datetime.now().strftime("%d%m%y")
                        filename = f"{date_str}_{self.name_value1}_{stt_tmp}b_{timecode[:-3]}.jpg"
                        try:
                            cv2.imwrite(os.path.join(output_dir_picture, filename), frame)
                            stt_tmp += 1
                        except Exception as e:
                            print(f"Lỗi khi lưu ảnh kết quả: {str(e)}")
                        
                        current_match = (current_match[0], first_scene_frame, frame_time, banner_type)
                        timestamps.append(current_match)
                        current_match = None
                        current_state = FINDING_START
    
        cap.release()
        self.update_progress(0)
        
        # Lọc bỏ các trận không hợp lệ và sắp xếp theo frame
        valid_timestamps = []
        for start_frame, first_scene_frame, end_frame, result in timestamps:
            if result and end_frame > start_frame:  # Kiểm tra thêm điều kiện frame
                valid_timestamps.append((start_frame, first_scene_frame, end_frame, result))
        
        # Sắp xếp theo frame bắt đầu
        valid_timestamps.sort(key=lambda x: x[0])
        
        # In tổng kết
        valid_matches = len(valid_timestamps)
        self.log(f"Tìm thấy {valid_matches} đoạn cần cắt")

        # lưu file check.txt tại thư mục hiện tại
        # with open("check.txt", "w") as f:
        #     for start_frame, first_scene_frame, end_frame, result in valid_timestamps:
        #         f.write(f"{self.frame_to_timecode(start_frame, self.fps_global)} -> {self.frame_to_timecode(first_scene_frame, self.fps_global)} - > {self.frame_to_timecode(end_frame, self.fps_global)} : {result}\n")
        
        return valid_timestamps

    def process_video_file_new_logic(self, input_path, output_dir_picture):
        """Logic mới: Chỉ tìm kết quả, kết quả đầu tiên bỏ qua, từ kết quả + 10s là START video"""
        cap = cv2.VideoCapture(input_path)
        timestamps = []
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        processed_frames = 0
        
        # Trạng thái xử lý
        FINDING_FIRST_RESULT = 0  # Tìm kết quả đầu tiên (để tính START cho Video 1)
        FINDING_VIDEO_RESULTS = 1 # Tìm kết quả cho các video
        
        current_state = FINDING_FIRST_RESULT
        stt_tmp = self.name_value3_start
        first_result_time = None  # Lưu thời gian kết quả đầu tiên
        last_result_time = None   # Lưu thời gian kết quả trước đó
        
        # Tối ưu: Chỉ check 7 frame mỗi giây   
        frame_skip_interval = int(self.fps_global / 7) if self.fps_global > 0 else 3  # 7 FPS
        frame_count = 0
        
        self.log("Bắt đầu xử lý với logic mới...")
        self.log("Chỉ tìm banner kết quả (X, D, H)")
        self.log("Kết quả đầu tiên dùng để tính START cho Video 1")
        self.log(f"Tối ưu: Chỉ check 7 FPS (skip {frame_skip_interval} frame)")
        
        while cap.isOpened():
            if not self.running:
                break
                
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            processed_frames += 1
            
            # Chỉ xử lý mỗi frame_skip_interval frame (7 FPS)
            if frame_count % frame_skip_interval != 0:
                continue
            
            # Lấy thời gian của frame hiện tại (milliseconds)
            frame_time = cap.get(cv2.CAP_PROP_POS_MSEC)
            
            # Cập nhật thanh tiến trình (tối ưu như main.py)
            if processed_frames % 60 == 0:
                progress = (processed_frames / total_frames) * 100
                self.update_progress(progress)
                self.log_text.see(tk.END)
                self.root.update()

            # Phát hiện banner kết quả (chỉ 7 lần/giây)
            result = self.detect_result_banner_new(frame)
            
            if result:
                timecode = self.msec_to_timecode(frame_time)
                
                if current_state == FINDING_FIRST_RESULT:
                    # Trạng thái 1: Tìm kết quả đầu tiên (để tính START cho Video 1)
                    result_type = {
                        "D": "Đỏ thắng",
                        "X": "Xanh thắng", 
                        "H": "Hòa"
                    }.get(result, result)
                    
                    self.log(f"Phát hiện kết quả đầu tiên: {result_type} ({result}) tại {timecode}\n")
                    
                    # Lưu ảnh kết quả đầu tiên với thời gian thực tế trong video
                    date_str = datetime.now().strftime("%d%m%y")
                    filename = f"{date_str}_{self.name_value1}_{stt_tmp}_FIRST_{timecode}.jpg"
                    try:
                        cv2.imwrite(os.path.join(output_dir_picture, filename), frame)
                    except Exception as e:
                        print(f"Lỗi khi lưu ảnh: {str(e)}")
                    
                    # Lưu thời gian kết quả đầu tiên
                    first_result_time = frame_time
                    last_result_time = frame_time
                    
                    # Chuyển sang tìm kết quả cho video
                    current_state = FINDING_VIDEO_RESULTS
                    
                    # Skip 2 phút để bỏ qua toàn bộ video 1 (10s + 25s)
                    skip_to_time = frame_time + 120000  # Skip 2 phút
                    cap.set(cv2.CAP_PROP_POS_MSEC, skip_to_time)
                    
                    # Cập nhật processed_frames dựa trên số frame đã xử lý
                    current_frame_pos = cap.get(cv2.CAP_PROP_POS_FRAMES)
                    processed_frames = int(current_frame_pos)
                    
                    # Cập nhật progress bar
                    progress = (processed_frames / total_frames) * 100
                    self.update_progress(progress)
                    self.log_text.see(tk.END)
                    self.root.update()
                    
                elif current_state == FINDING_VIDEO_RESULTS:
                    # Trạng thái 2: Tìm kết quả cho video
                    result_type = {
                        "D": "Đỏ thắng",
                        "X": "Xanh thắng", 
                        "H": "Hòa"
                    }.get(result, result)
                    
                    # Tính toán thời gian video
                    if stt_tmp == self.name_value3_start:
                        # Video 1: START = Kết quả đầu tiên + 10s, END = START + 25s
                        video_start_time = first_result_time + 10000   # Kết quả đầu tiên + 10s
                        video_end_time = video_start_time + 25000    # START + 25s
                    else:
                        # Video tiếp theo: START = Kết quả trước + 10s, END = START + 25s
                        video_start_time = last_result_time + 10000   # Kết quả trước + 10s
                        video_end_time = video_start_time + 25000    # START + 25s
                    
                    # Lưu timestamp: (start_time, end_time, result)
                    timestamps.append((video_start_time, video_end_time, result))
                    self.log(f"Video {stt_tmp}: {self.msec_to_timecode(video_start_time)} -> {self.msec_to_timecode(video_end_time)}")
                    self.log(f"Phát hiện kết quả: {result_type} ({result}) tại {timecode} (video {stt_tmp} -> {result_type})\n")
                    
                    # Lưu ảnh kết quả với thời gian thực tế trong video khi phát hiện
                    date_str = datetime.now().strftime("%d%m%y")
                    filename = f"{date_str}_{self.name_value1}_{stt_tmp}_{result}_{timecode}.jpg"
                    try:
                        cv2.imwrite(os.path.join(output_dir_picture, filename), frame)
                    except Exception as e:
                        print(f"Lỗi khi lưu ảnh kết quả: {str(e)}")
                    
                    # Cập nhật kết quả trước đó
                    last_result_time = frame_time
                    
                    stt_tmp += 1
                    
                    # Skip 2 phút để tìm kết quả tiếp theo
                    skip_to_time = frame_time + 120000  # Skip 2 phút
                    cap.set(cv2.CAP_PROP_POS_MSEC, skip_to_time)
                    
                    # Cập nhật processed_frames dựa trên số frame đã xử lý
                    current_frame_pos = cap.get(cv2.CAP_PROP_POS_FRAMES)
                    processed_frames = int(current_frame_pos)
                    
                    # Cập nhật progress bar
                    progress = (processed_frames / total_frames) * 100
                    self.update_progress(progress)
                    self.log_text.see(tk.END)
                    self.root.update()
        
        cap.release()
        self.update_progress(0)
        
        # Lọc bỏ các trận không hợp lệ
        valid_timestamps = []
        for start_time, end_time, result in timestamps:
            if result and end_time > start_time and start_time > 0:
                valid_timestamps.append((start_time, end_time, result))
        
        # Sắp xếp theo thời gian bắt đầu
        valid_timestamps.sort(key=lambda x: x[0])
        
        valid_matches = len(valid_timestamps)
        self.log(f"Tìm thấy {valid_matches} đoạn video cần cắt")
        
        return valid_timestamps

    def cut_video_file(self, input_path, timestamps, output_dir):
        total_cuts = len([t for t in timestamps if t[2]])
        current_cut = 0
        stt_video = self.name_value3_start
        
        for start_time, first_scene_time, end_time, result in timestamps:
            if not result:
                continue
            
            try:
                current_cut += 1
                self.update_progress((current_cut / total_cuts) * 100)
            
                # Tạo tên file
                date_str = datetime.now().strftime("%d%m%y")
                # self.current_value3 = random.randint(100, 9999)
                name_value3 = self.msec_to_timecode(start_time)
                filename = f"{result}_{date_str}_{self.name_value1}_{stt_video}_{name_value3[:-3]}"
                stt_video += 1
                
                output_filename = os.path.join(output_dir, f"{filename}.mp4")
                # self.log(f"Đang cắt video {current_cut}/{total_cuts}: {os.path.basename(output_filename)}")
                
                # Đọc video gốc
                cap = cv2.VideoCapture(input_path)
                if not cap.isOpened():
                    raise Exception("Không thể mở video gốc")
                
                # Lấy thông số video
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                
                # Thử các codec khác nhau
                codecs = ['mp4v', 'avc1', 'xvid']
                out = None
                
                for codec in codecs:
                    fourcc = cv2.VideoWriter_fourcc(*codec)
                    out = cv2.VideoWriter(output_filename, fourcc, self.fps_global, (width, height))
                    if out.isOpened():
                        break
                
                if not out.isOpened():
                    raise Exception("Không thể tạo file output")
                
                # Tính số frame cần cắt
                duration_needed = 28 * 1000  # 28 giây trong milliseconds
                remaining_duration = end_time - first_scene_time
                duration_to_write = min(duration_needed, remaining_duration)
                frames_to_write = int(duration_to_write/1000 * self.fps_global)
                
                # Seek đến time bắt đầu
                cap.set(cv2.CAP_PROP_POS_MSEC, first_scene_time)

                # Bắt đầu ghi từ first_scene_frame
                frames_written = 0
                for _ in range(frames_to_write):
                    ret, frame = cap.read()
                    if not ret:
                        break
                    out.write(frame)
                    frames_written += 1
                
                if frames_written == 0:
                    raise Exception("Không ghi được frame nào")
                    
                cap.release()
                out.release()
                
                # self.log(f"Đã cắt xong: {frames_written} frames")
                
            except Exception as e:
                self.log(f"Lỗi khi cắt video: {str(e)}")
                continue

    def cut_video_file_new_logic(self, input_path, timestamps, output_dir):
        """Cắt video với logic mới"""
        total_cuts = len(timestamps)
        current_cut = 0
        stt_video = self.name_value3_start
        
        for start_time, end_time, result in timestamps:
            try:
                current_cut += 1
                self.update_progress((current_cut / total_cuts) * 100)
            
                # Tạo tên file
                date_str = datetime.now().strftime("%d%m%y")
                name_value3 = self.msec_to_timecode(start_time)
                filename = f"{result}_{date_str}_{self.name_value1}_{stt_video}_{name_value3}"
                stt_video += 1
                
                output_filename = os.path.join(output_dir, f"{filename}.mp4")
                
                # Đọc video gốc
                cap = cv2.VideoCapture(input_path)
                if not cap.isOpened():
                    raise Exception("Không thể mở video gốc")
                
                # Lấy thông số video
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                
                # Thử các codec khác nhau
                codecs = ['mp4v', 'avc1', 'xvid']
                out = None
                
                for codec in codecs:
                    fourcc = cv2.VideoWriter_fourcc(*codec)
                    out = cv2.VideoWriter(output_filename, fourcc, self.fps_global, (width, height))
                    if out.isOpened():
                        break
                
                if not out.isOpened():
                    raise Exception("Không thể tạo file output")
                
                # Tính số frame cần cắt (25 giây - từ START đến END)
                duration_to_write = end_time - start_time  # Thời gian thực tế
                frames_to_write = int(duration_to_write / 1000 * self.fps_global)
                
                # Seek đến thời điểm bắt đầu
                cap.set(cv2.CAP_PROP_POS_MSEC, start_time)

                # Ghi video
                frames_written = 0
                for _ in range(frames_to_write):
                    ret, frame = cap.read()
                    if not ret:
                        break
                    out.write(frame)
                    frames_written += 1
                
                if frames_written == 0:
                    raise Exception("Không ghi được frame nào")
                    
                cap.release()
                out.release()
                
                self.log(f"Đã cắt xong: {os.path.basename(output_filename)} ({frames_written} frames)")
                
            except Exception as e:
                self.log(f"Lỗi khi cắt video: {str(e)}")
                continue

    # hàm tìm thời gian chuyển cảnh đầu tiên
    # thông thường ngay sau start_time là chuyển cảnh đầu tiên, hàm này sẽ quét từ start_time đến hết video
    # nếu không gặp chuyển cảnh thì sẽ trả về start_time
    def find_first_scene_change(self, input_path, start_time, threshold=0.25):
        cap = cv2.VideoCapture(input_path)
        
        # Seek đến thời điểm START
        cap.set(cv2.CAP_PROP_POS_MSEC, start_time)
        current_time = cap.get(cv2.CAP_PROP_POS_MSEC)

        if current_time < start_time:
            cap.set(cv2.CAP_PROP_POS_MSEC, start_time + 1000)

        # Lấy kích thước frame
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Tạo mask để loại bỏ vùng banner ở giữa
        mask = np.ones((height, width), dtype=np.uint8)
        banner_roi = {
            'y1': int(height * 0.27),  
            'y2': int(height * 0.9),
            'x1': int(width * 0.26),  
            'x2': int(width * 0.74)
        }
        mask[banner_roi['y1']:banner_roi['y2'], banner_roi['x1']:banner_roi['x2']] = 0
        
        # Đọc frame đầu tiên
        ret, prev_frame = cap.read()
        if not ret:
            cap.release()
            return start_time + 1000  # Trả về start + 1 giây nếu không đọc được
        
        # Xử lý frame đầu với mask
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        prev_gray_masked = cv2.bitwise_and(prev_gray, prev_gray, mask=mask)
        prev_hist = cv2.calcHist([prev_gray_masked], [0], mask, [256], [0, 256])
        cv2.normalize(prev_hist, prev_hist, 0, 1, cv2.NORM_MINMAX)
        
        # Tìm trong 120 giây
        
        max_search_time = start_time + (120 * 1000)
        found_scene = False
        
        while cap.isOpened() and current_time < max_search_time:
            ret, frame = cap.read()
            if not ret:
                break

            current_time = cap.get(cv2.CAP_PROP_POS_MSEC)

            # Xử lý frame hiện tại với mask
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.bitwise_and(gray, gray, mask=mask)
            hist = cv2.calcHist([gray], [0], mask, [256], [0, 256])
            cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)
            
            # So sánh histogram
            diff = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_BHATTACHARYYA)
               
            if diff > threshold:
                found_scene = True
                break
            
            prev_hist = hist
        
        cap.release()
        if found_scene:
            return current_time
        else:
            return start_time + 1000  # Trả về start + 1 giây nếu không tìm thấy

    def msec_to_timecode(self, milliseconds):
        """Chuyển milliseconds thành timecode"""
        total_seconds = int(milliseconds / 1000)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        return f"{hours:02d}.{minutes:02d}.{seconds:02d}"

    def toggle_detection(self):
        """Bật/tắt chức năng detect real-time"""
        if not self.detection_running:
            self.start_real_time_detection()
        else:
            self.stop_real_time_detection()
    
    def start_real_time_detection(self):
        """Bắt đầu detect real-time"""
        try:
            if self.real_time_detector is None:
                self.real_time_detector = RealTimeDetector()
            
            # Cập nhật thời gian đóng cược từ giao diện
            try:
                bet_duration = int(self.bet_duration_var.get())
                if bet_duration > 0:
                    self.real_time_detector.BET_DURATION = bet_duration
                    self.log(f"Thời gian đóng cược: {bet_duration} giây")
            except ValueError:
                self.log("⚠️ Sử dụng thời gian đóng cược mặc định: 45 giây")
            
            self.real_time_detector.start_detection(self.detection_callback)
            self.detection_running = True
            self.detect_button.config(text="Stop Detect", bg="green", fg="white")
            self.log("Đã bắt đầu detect real-time")
            
        except Exception as e:
            self.log(f"Lỗi khởi động detect: {str(e)}")
            tk.messagebox.showerror("Lỗi", f"Không thể khởi động detect: {str(e)}")
    
    def stop_real_time_detection(self):
        """Dừng detect real-time"""
        try:
            if self.real_time_detector:
                self.real_time_detector.stop_detection()
            
            self.detection_running = False
            self.detect_button.config(text="Auto Detect", bg="red", fg="white")
            self.log("Đã dừng detect real-time")
            
        except Exception as e:
            self.log(f"Lỗi dừng detect: {str(e)}")
    
    def detection_callback(self, event, frame, result=None, result_text=None):
        """Callback khi phát hiện sự kiện"""
        if event == "START_DETECTED":
            self.log("🎬 Phát hiện banner START!")
        elif event == "SCENE_CHANGE_DETECTED":
            self.log("🎬 Phát hiện chuyển cảnh - Đã click tự động!")
        elif event == "RESULT_DETECTED":
            if result == "CANCEL":
                self.log("❌ Trận đấu bị hủy - Phát hiện START mới")
            else:
                # Map kết quả để hiển thị đúng
                display_text = {
                    "D": "Meron thắng",
                    "X": "Wala thắng",
                    "H": "Hòa"
                }.get(result, result_text)
                self.log(f"🏆 Phát hiện kết quả: {display_text} ({result})")
        elif event == "RESET_COMPLETE":
            self.log("🔄 Đã reset - Sẵn sàng cho trận tiếp theo")
        elif event == "CLICK_EVENT":
            # Hiển thị thông báo click với icon tương ứng
            click_icons = {
                "Mở cược": "💰",
                "Đóng cược": "🔒", 
                "Meron thắng": "🔴",
                "Wala thắng": "🔵",
                "Hòa": "🟢",
                "Hủy trận": "❌"
            }
            icon = click_icons.get(result, "🖱️")
            self.log(f"{icon} {result_text}")

    def set_click_point(self, setting_type):
        """Bắt đầu quá trình đặt điểm click cho loại cụ thể"""
        try:
            # Dừng click point setter cũ nếu đang chạy
            if self.click_point_setter:
                self.click_point_setter.stop_monitoring()
            
            type_names = {
                "open_bet": "Mở cược",
                "close_bet": "Đóng cược", 
                "meron_win": "Meron thắng",
                "wala_win": "Wala thắng",
                "draw": "Hòa",
                "cancel": "Hủy trận"
            }
            type_name = type_names.get(setting_type, setting_type)
            
            # self.log(f"Di chuyển chuột đến vị trí {type_name} và nhấn chuột trái 1 lần")
            # self.log("Nhấn ESC để hủy")
            
            # Disable tất cả nút trong khi đang set
            self.disable_all_click_buttons()
            
            # Bắt đầu quá trình đặt điểm click
            self.click_point_setter, self.click_point_thread = set_single_click_point_gui(setting_type, self.root)
            
            # Enable tất cả nút sau khi bắt đầu thread
            self.enable_all_click_buttons()
            
        except Exception as e:
            self.log(f"❌ Lỗi khi đặt điểm click: {str(e)}")
            self.enable_all_click_buttons()
    
    def reload_config_after_setting(self):
        """Reload config sau khi người dùng xác nhận message box"""
        try:
            # Chờ thêm 0.5 giây để đảm bảo file đã được lưu
            time.sleep(0.5)
            
            # Reload config trong real_time_detector nếu đang chạy
            if self.real_time_detector:
                if self.real_time_detector.reload_config():
                    self.log("✅ Đã reload config và cập nhật tọa độ mới")
                    
                    # In thông tin tọa độ hiện tại
                    if hasattr(self.real_time_detector, 'force_reload_config'):
                        self.real_time_detector.force_reload_config()
                else:
                    self.log("⚠️ Không thể reload config")
            else:
                self.log("✅ Đã lưu tọa độ mới")
                
        except Exception as e:
            self.log(f"❌ Lỗi khi reload config: {str(e)}")
    
    def disable_all_click_buttons(self):
        """Disable tất cả nút set click"""
        self.set_open_bet_button.config(state=tk.DISABLED)
        self.set_close_bet_button.config(state=tk.DISABLED)
        self.set_meron_win_button.config(state=tk.DISABLED)
        self.set_wala_win_button.config(state=tk.DISABLED)
        self.set_draw_button.config(state=tk.DISABLED)
        self.set_cancel_button.config(state=tk.DISABLED)
    
    def update_bet_duration(self):
        """Cập nhật thời gian đóng cược"""
        try:
            new_duration = int(self.bet_duration_var.get())
            if new_duration <= 0:
                messagebox.showerror("Lỗi", "Thời gian phải lớn hơn 0!")
                return
            
            # Cập nhật trong real_time_detector nếu đang chạy
            if self.real_time_detector:
                self.real_time_detector.BET_DURATION = new_duration
                self.log(f"✅ Đã cập nhật thời gian đóng cược: {new_duration} giây")
            else:
                self.log(f"✅ Đã lưu thời gian đóng cược: {new_duration} giây")
                
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập số hợp lệ!")
        except Exception as e:
            self.log(f"❌ Lỗi cập nhật thời gian: {str(e)}")
    
    def enable_all_click_buttons(self):
        """Enable tất cả nút set click"""
        self.set_open_bet_button.config(state=tk.NORMAL)
        self.set_close_bet_button.config(state=tk.NORMAL)
        self.set_meron_win_button.config(state=tk.NORMAL)
        self.set_wala_win_button.config(state=tk.NORMAL)
        self.set_draw_button.config(state=tk.NORMAL)
        self.set_cancel_button.config(state=tk.NORMAL)

def main():
    root = tk.Tk()
    app = VideoProcessorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()