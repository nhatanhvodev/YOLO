# Hướng dẫn triển khai hệ thống giám sát giao thông (YOLO)

Đây là một hệ thống giám sát giao thông sử dụng thuật toán YOLO và ngôn ngữ lập trình Python. Hệ thống được thiết kế để nhận diện 5 loại phương tiện lưu thông trên đường (xe máy, xe đạp, ô tô, xe tải, xe bus).

Tài liệu này tổng hợp lại cách cài đặt, vận hành và các thành phần chính bên trong thư mục `yolo` (trước đây là `python_project`).

## Tính năng chính
- Đếm số lượng phương tiện vi phạm.
- Thống kê số lượt vi phạm theo ngày và theo năm (khi bật lưu DB).
- Tạo biên bản PDF cho phương tiện đi sai làn.
- Theo dõi chuyển động phương tiện bằng tracker để tránh đếm trùng.

## 1. Yêu cầu hệ thống
- Windows 10/11 với PowerShell 5.1
- Python 3.8 trở lên
- Virtual environment để cô lập thư viện (`python -m venv .venv`)
- MySQL/MariaDB (tùy chọn) nếu muốn ghi nhận dữ liệu vi phạm
- GPU là lợi thế nhưng không bắt buộc

## 2. Thiết lập môi trường Python

```powershell
# Tạo và kích hoạt virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Cập nhật công cụ build
python -m pip install --upgrade pip setuptools wheel

# Cài thư viện nền tảng của Ultralytics
pip install -r yolo\requirements.txt

# Cài thêm các dịch vụ web và PDF
pip install flask flask-cors flask-mysqldb pymysql ultralytics supervision reportlab
```

> Ghi chú: một số script thử nghiệm cần thêm `opencv-contrib-python`, `PyQt5`, `deep-sort-realtime`… hãy cài khi thực sự sử dụng tới.

## 3. Thư mục và script quan trọng trong `yolo`

| Thành phần | Mô tả |
| --- | --- |
| `app_server.py` | Flask server phát video (4 camera mẫu), tạo PDF, chèn dữ liệu vào MySQL nếu bật `USE_DB`. |
| `createBB.py` | Sinh biên bản PDF bằng ReportLab, tự động chèn mốc thời gian “Ngày … lúc …”. |
| `main.py` | Ví dụ đếm phương tiện bằng YOLO + line counter (Supervision). |
| `testLane.py` | Script xử lý khung hình, cắt ROI, lưu ảnh/PDF thủ công. |
| `trackingMain.py`, `tichhop.py`, `tong_hop.py` | Các thử nghiệm tracking với SORT/cvzone, nhiều đường dẫn tuyệt đối cần chỉnh lại trước khi chạy. |
| `tracker.py`, `sort.py` | Cài đặt bộ theo dõi ID tự viết và phiên bản SORT gốc. |
| `gui.py` + `gui.ui` | Giao diện PyQt5 dùng trong `tong_hop.py`. |
| `requirements.txt` | Danh sách thư viện Ultralytics cơ bản. |
| `best_new/`, `YoloWeights/` | Model `.pt` cho từng chế độ (web server dùng `best_new/vehicle.pt`, script đơn dùng `YoloWeights/best.pt`). |
| `Videos/` | Video mẫu `main.mp4`, `lane.mp4`, `test9.mp4`, `test13.mp4`. |
| `templates/` | HTML templates cho Flask (index, thongke, bb, laneviolate1-4). |
| `static/img/` | Hình ảnh tĩnh (loader.gif, home.png) phục vụ qua Flask. |
| `BienBanNopPhatXeMay/`, `BienBanNopPhatXeOTo/` | PDF biên bản vi phạm tự động. |
| `data_xe_may_vi_pham/`, `data_oto_vi_pham/` | Ảnh trích xuất khi phát hiện vi phạm. |

> **Lưu ý:** Thư mục đã đổi tên từ `python_project` → `yolo`. Nhiều script thử nghiệm còn đường dẫn tuyệt đối cũ cần chỉnh lại.

## 4. Tích hợp MySQL (tùy chọn)

`app_server.py` hiện kết nối tới schema `yolo` với tài khoản `root` (mật khẩu trống).

1. Mở XAMPP (hoặc dịch vụ MySQL khác) **bằng quyền Administrator**, start MySQL.
2. Đảm bảo không có tiến trình MySQL khác chiếm cổng 3306 (`netstat -ano | findstr 3306`).
3. Tạo database:
   ```sql
   CREATE DATABASE yolo DEFAULT CHARACTER SET utf8mb4;
   USE yolo;
   SOURCE create_database.sql;
   ```
   File `create_database.sql` tạo bảng `nametransportation` (5 loại xe) và `transportationviolation` (log vi phạm).
4. Nếu cần đổi mật khẩu MySQL, cập nhật trong `yolo/app_server.py`:
   ```python
   app.config['MYSQL_PASSWORD'] = 'your_password'
   ```

> **Cải tiến mới:** Hệ thống tự động trả về dữ liệu mặc định (zero-filled) khi `USE_DB=0` hoặc MySQL lỗi, tránh crash trang thống kê.

### Đặt biến môi trường `USE_DB`

| Mục đích | Lệnh PowerShell |
| --- | --- |
| Bật tạm thời trong phiên hiện tại | `$env:USE_DB = '1'` |
| Tắt tạm thời | `$env:USE_DB = '0'` |
| Ghi vĩnh viễn cho user | `setx USE_DB 1` (cần mở PowerShell mới để nhận) |

## 5. Chạy các chế độ chính

### 5.1 Web server Flask

```powershell
# Kích hoạt virtual environment
.\.\.venv\Scripts\Activate.ps1

# Đặt USE_DB (tùy chọn)
$env:USE_DB = '1'   # Bật MySQL | '0' = dùng dữ liệu mặc định

# Khởi động server
python yolo\app_server.py
```

⚠️ **Lưu ý:** Phải dùng Python trong `.venv`, không dùng Python toàn cục!

Truy cập **http://127.0.0.1:8000**

### Các trang chính:
- `/` - Trang chủ với hero image `home.png`
- `/thongke` - Dashboard thống kê với biểu đồ Chart.js và cards hiển thị vi phạm theo ngày
- `/bb` - Quy định luật giao thông với sidebar navigation
- `/LaneViolate1` đến `/LaneViolate4` - Camera giám sát realtime với preloader

### Chức năng backend:
- API `/test` - Thống kê tổng (5 loại xe, normalized)
- API `/test1` - Thống kê theo ngày (với fallback zero-filled)
- Tự động lưu ảnh vi phạm vào `data_xe_may_vi_pham/` và `data_oto_vi_pham/`
- Tạo PDF biên bản tự động khi phát hiện vi phạm

### 5.2 Script OpenCV độc lập

```powershell
.\.\.venv\Scripts\Activate.ps1
python yolo\main.py
```

Script hiển thị cửa sổ OpenCV, sử dụng mô hình ở `yolo/YoloWeights/best.pt` và bộ đếm line zone của Supervision.

### 5.3 Công cụ hỗ trợ khác
- `testLane.py`: tạo ảnh ROI và PDF offline, hữu ích khi kiểm thử logic lane.
- `trackingMain.py`, `tichhop.py`: minh họa gắn Sort tracker + cảnh báo. Cần chỉnh đường dẫn video/model trước khi chạy.
- `tong_hop.py`: giao diện PyQt5 phát video và lưu biên bản; yêu cầu `PyQt5` và cập nhật lại đường dẫn.
- `speed.py`, `SpeedEstimation.py`, `tets1.py`: code nháp đo tốc độ/tracking; mặc định bị comment nhiều đoạn.

## 6. Dữ liệu và log đầu ra

- Ảnh vi phạm: `yolo/data_xe_may_vi_pham/` và `yolo/data_oto_vi_pham/`
- PDF biên bản: `yolo/BienBanNopPhatXeMay/` và `yolo/BienBanNopPhatXeOTo/`
- Static assets: `yolo/static/img/` (loader.gif, home.png)
- Thư mục `yolo/runs/detect/` lưu kết quả mặc định của Ultralytics
- Console logs với nhãn `[INFO]`, `[WARNING]`, `[ERROR]` từ `app_server.py`

## 7. Khắc phục sự cố phổ biến

- **Không kết nối được MySQL (10061/1045):** kiểm tra dịch vụ MySQL đã bật, mật khẩu `root`, cập nhật `config.inc.php`, và chắc chắn không có tiến trình khác chiếm cổng 3306.
- **`cryptography package is required`:** cài bổ sung `pip install cryptography`.
- **`ModuleNotFoundError: No module named 'flask'`:** Chưa kích hoạt virtual environment. Chạy `.\.\.venv\Scripts\Activate.ps1` trước khi chạy server.
- **Thiếu model `.pt`:** Đặt file đúng vị trí hoặc cập nhật `model_path` trong code (`app_server.py`, `main.py`, `testLane.py`).
- **Không hiển thị video:** Xác thực `yolo/Videos/*.mp4` tồn tại và codec hỗ trợ, hoặc đổi sang camera/RTSP.
- **404 cho static files:** Đảm bảo `yolo/static/img/` chứa `loader.gif` và `home.png`.
- **CORS errors cho remote images:** Một số CDN chặn cross-origin requests; thay bằng ảnh từ Unsplash hoặc local assets.

## 8. Cải tiến giao diện (November 2025)

### Templates mới
- **Preloader animation:** Tất cả pages (`index`, `bb`, `thongke`, `laneviolate1-4`) có loader.gif fade-out mượt mà
- **Hero image:** Trang chủ dùng `home.png` từ static folder thay vì remote URL
- **Statistics dashboard:** Cards gradient 2×2 với màu sắc đồng bộ biểu đồ Chart.js
- **Navigation:** Sidebar trắng responsive với active states xanh lá

### Cấu trúc static assets
```
yolo/
├── static/
│   └── img/
│       ├── loader.gif   # Preloader animation
│       └── home.png     # Homepage hero image
└── templates/
    ├── index.html       # Hero + sidebar navigation
    ├── thongke.html     # Statistics với Chart.js
    ├── bb.html          # Traffic laws content
    └── laneviolate{1-4}.html  # Camera feeds
```

### Backend improvements
- **Fallback mechanism:** API `/test` và `/test1` trả về zero-filled data khi MySQL offline
- **Normalized response:** Luôn trả 5 loại xe theo thứ tự cố định (Ô Tô, Xe Máy, Xe Đạp, Xe Tải, Xe Bus)
- **Error handling:** Graceful degradation thay vì crash page khi DB unavailable

## 9. Ghi chú phát triển

- Flask đang chạy `debug=True` và `threaded=True` chỉ nên dùng khi phát triển.
- Khi triển khai thực tế, hãy tách luồng YOLO sang service riêng hoặc dùng queue để tránh nghẽn.
- `insert_violation_record` được gọi trên từng khung hợp lệ; cân nhắc throttle nếu đưa vào môi trường thực.
- Các thư mục dữ liệu nên backup định kỳ vì số lượng file có thể lớn.

---