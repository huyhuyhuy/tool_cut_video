import cv2
import numpy as np
from datetime import datetime
import os
import time
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from threading import Thread

class NewVideoProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("New Video Processor - No START Banner")
        self.root.geometry("600x500")
        
        # Căn giữa cửa sổ
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = 600
        window_height = 500
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
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
        
        # Label hiển thị cú pháp đặt tên
        self.name_label = ttk.Label(main_frame, text="Cú pháp đặt tên: [đội thắng]_[ngày tháng năm]_[tên nhóm]_[stt]_[giờ phút bắt đầu trận đấu]")
        self.name_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Thêm thanh tiến trình
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, 
            variable=self.progress_var, 
            maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
 
        # Nút xử lý
        self.start_button = ttk.Button(main_frame, text="Bắt đầu xử lý (Logic mới)", command=self.start_processing)
        self.start_button.pack(pady=10)
        
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
        self.running = False
        
        # Biến cho việc đặt tên
        self.name_value1 = None
        self.name_value3_start = 1
        
        # FPS global
        self.fps_global = None
        
        # Load template ảnh mẫu 1 lần (tối ưu hiệu suất)
        self.template_red = cv2.imread('template_do_new.png')
        self.template_blue = cv2.imread('template_xanh_new.png')
        self.template_green = cv2.imread('template_hoa_new.png')
        
        # Kiểm tra template có load được không
        if self.template_red is None or self.template_blue is None or self.template_green is None:
            print("Lỗi: Không thể load template ảnh mẫu!")
            self.template_red = None
            self.template_blue = None
            self.template_green = None
        
        
        # Xử lý sự kiện đóng cửa sổ
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """Xử lý khi đóng chương trình"""
        if self.processing:
            if messagebox.askokcancel("Đang xử lý", "Đang trong quá trình xử lý. Bạn có chắc muốn thoát?"):
                self.running = False
                self.processing = False
                self.root.after(100, self.root.destroy)
        else:
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

    def start_processing(self):
        if self.processing:
            self.log("Đang xử lý, vui lòng đợi...")
            return
            
        if not self.dir_path.get():
            self.log("Vui lòng chọn thư mục video!")
            return
 
        self.processing = True
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.log_text.delete(1.0, tk.END)
        
        # Tạo thread mới để xử lý tất cả video
        process_thread = Thread(target=self.process_all_videos)
        process_thread.start()

    def process_all_videos(self):
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
            self.root.after(0, self.show_completion_message)
            
        except Exception as e:
            self.log(f"Lỗi: {str(e)}")
        finally:
            self.processing = False
            self.running = False

    def show_completion_message(self):
        """Hiển thị thông báo hoàn thành trong main thread"""
        if tk.messagebox.showinfo("Thành công", "Đã xử lý xong!"):
            os.startfile(self.dir_path.get())
        self.start_button.config(state=tk.NORMAL)


    def detect_result_banner(self, frame):
        """Phát hiện banner kết quả (X, D, H) - Sử dụng Template Matching tối ưu"""
        
        # Kiểm tra template đã load chưa
        if self.template_red is None or self.template_blue is None or self.template_green is None:
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
        template_red_resized = self.template_red
        template_blue_resized = self.template_blue
        template_green_resized = self.template_green
        
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
        """Kiểm tra FPS thực của video"""
        cap = cv2.VideoCapture(input_video)
        if not cap.isOpened():
            return 0
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        duration = total_frames / fps if fps > 0 else 0
        
        cap.release()
        
        print(f"- FPS: {fps}")
        return fps

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

    def process_video_file_new_logic(self, input_path, output_dir_picture):
        """Logic mới: Chỉ tìm kết quả, kết quả đầu tiên bỏ qua, từ kết quả + 5s là START video"""
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
            result = self.detect_result_banner(frame)
            
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

    def msec_to_timecode(self, milliseconds):
        """Chuyển milliseconds thành timecode"""
        total_seconds = int(milliseconds / 1000)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        return f"{hours:02d}.{minutes:02d}.{seconds:02d}"

def main():
    root = tk.Tk()
    app = NewVideoProcessorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
