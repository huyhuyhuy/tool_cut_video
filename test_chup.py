import cv2
import os
import time
from datetime import datetime

def capture_frames_from_video():
    """Chụp ảnh từ video mỗi 1 giây"""
    
    # Đường dẫn thư mục video
    video_dir = r"D:\DEV_TOOL\video_test_cut_video_no_start"
    
    # Tạo thư mục lưu ảnh
    output_dir = "test_anh"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Đã tạo thư mục: {output_dir}")
    
    # Tìm file video trong thư mục
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v']
    video_file = None
    
    for file in os.listdir(video_dir):
        if any(file.lower().endswith(ext) for ext in video_extensions):
            video_file = os.path.join(video_dir, file)
            break
    
    if not video_file:
        print("Không tìm thấy file video trong thư mục!")
        return
    
    print(f"Tìm thấy video: {video_file}")
    
    # Mở video
    cap = cv2.VideoCapture(video_file)
    if not cap.isOpened():
        print("Không thể mở video!")
        return
    
    # Lấy thông tin video
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0
    
    print(f"FPS: {fps}")
    print(f"Tổng số frame: {total_frames}")
    print(f"Thời lượng: {duration:.2f} giây")
    print(f"Bắt đầu chụp ảnh mỗi 1 giây...")
    
    # Biến đếm
    frame_count = 0
    saved_count = 0
    
    # Tính số frame cần skip (1 giây = fps frames)
    skip_frames = int(fps) if fps > 0 else 30
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Chụp ảnh mỗi 1 giây
        if frame_count % skip_frames == 0:
            # Tạo tên file với timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"frame_{saved_count:04d}_{timestamp}.png"
            filepath = os.path.join(output_dir, filename)
            
            # Lưu ảnh
            success = cv2.imwrite(filepath, frame)
            if success:
                saved_count += 1
                current_time = frame_count / fps if fps > 0 else frame_count / 30
                print(f"Đã lưu ảnh {saved_count}: {filename} (thời gian: {current_time:.1f}s)")
            else:
                print(f"Lỗi khi lưu ảnh: {filename}")
        
        frame_count += 1
        
        # Hiển thị tiến trình mỗi 100 frame
        if frame_count % 100 == 0:
            progress = (frame_count / total_frames) * 100
            print(f"Tiến trình: {progress:.1f}% ({frame_count}/{total_frames} frames)")
    
    # Đóng video
    cap.release()
    
    print(f"\nHoàn thành!")
    print(f"Tổng số ảnh đã lưu: {saved_count}")
    print(f"Ảnh được lưu trong thư mục: {os.path.abspath(output_dir)}")

if __name__ == "__main__":
    print("=== CHƯƠNG TRÌNH CHỤP ẢNH TỪ VIDEO ===")
    print("Thư mục video: D:\\DEV_TOOL\\video_test_cut_video_no_start")
    print("Thư mục lưu ảnh: test_anh")
    print("Tần suất chụp: 1 giây 1 lần")
    print("=" * 40)
    
    try:
        capture_frames_from_video()
    except KeyboardInterrupt:
        print("\nĐã dừng chương trình!")
    except Exception as e:
        print(f"Lỗi: {str(e)}")
    
    input("\nNhấn Enter để thoát...")
