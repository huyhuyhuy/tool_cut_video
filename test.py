import tkinter as tk

# Thông số tọa độ
data = {
    "x1": 176,
    "y1": 72,
    "x2": 1005,
    "y2": 536,
    "x_point": 300,
    "y_point": 800
}

# === CỬA SỔ KHUNG ĐỎ ===
rect_width = data["x2"] - data["x1"]
rect_height = data["y2"] - data["y1"]

root = tk.Tk()
root.attributes('-topmost', True)
root.geometry(f"{rect_width}x{rect_height}+{data['x1']}+{data['y1']}")
root.attributes('-alpha', 0.3)
root.configure(bg='red')
root.overrideredirect(True)

# === CỬA SỔ DẤU CỘNG ===
plus = tk.Toplevel(root)
plus.attributes('-topmost', True)
plus.overrideredirect(True)
plus.attributes('-alpha', 1.0)
plus.configure(bg='white')  # để dễ nhìn, bạn có thể đặt bg='' nếu muốn trong suốt

# Kích thước dấu cộng
line_len = 10
plus.geometry(f"{line_len*2}x{line_len*2}+{data['x_point'] - line_len}+{data['y_point'] - line_len}")

# Nét dọc
vertical = tk.Frame(plus, bg='black', width=2, height=line_len * 2)
vertical.place(x=line_len - 1, y=0)

# Nét ngang
horizontal = tk.Frame(plus, bg='black', width=line_len * 2, height=2)
horizontal.place(x=0, y=line_len - 1)

root.mainloop()
