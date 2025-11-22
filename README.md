# Hướng dẫn triển khai hệ thống giám sát giao thông (YOLO)

Đây là một hệ thống giám sát giao thông sử dụng thuật toán YOLO và ngôn ngữ lập trình Python. Hệ thống được thiết kế để nhận diện 5 loại phương tiện lưu thông trên đường (xe máy, xe đạp, ô tô, xe tải, xe bus).

Tài liệu này tổng hợp lại cách cài đặt, vận hành và các thành phần chính bên trong thư mục `python_project`.

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
pip install -r python_project\requirements.txt

# Cài thêm các dịch vụ web và PDF
pip install flask flask-cors flask-mysqldb pymysql ultralytics supervision reportlab
```

> Ghi chú: một số script thử nghiệm cần thêm `opencv-contrib-python`, `PyQt5`, `deep-sort-realtime`… hãy cài khi thực sự sử dụng tới.

## 3. Thư mục và script quan trọng trong `python_project`

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
| `templates/`, `static/` | HTML/CSS/ảnh phục vụ Flask. |
| `BienBanNopPhatXeMay/`, `BienBanNopPhatXeOTo/` | PDF kết quả. |
| `data_xe_may_vi_pham/`, `data_oto_vi_pham/` | Ảnh trích xuất khi phát hiện vi phạm. |

> Nhiều script thử nghiệm vẫn để đường dẫn tuyệt đối `F:/python_project/...`. Trước khi chạy trên thư mục hiện tại (`D:/YOLO`), hãy sửa thành đường dẫn tương đối hoặc tuyệt đối phù hợp.

## 4. Tích hợp MySQL (tùy chọn)

`app_server.py` hiện kết nối tới schema `...` với tài khoản `root/....`.

1. Mở XAMPP (hoặc dịch vụ MySQL khác) **bằng quyền Administrator**, start MySQL.
2. Đảm bảo không có tiến trình MySQL khác chiếm cổng 3306 (`netstat -ano | findstr 3306`).
3. Nếu chưa có database:
  ```sql
  CREATE DATABASE yolo DEFAULT CHARACTER SET utf8mb4;
  USE yolo;
  SOURCE create_database.sql;  -- hoặc import 
  ```
  File `create_database.sql` tạo bảng `nametransportation` và `transportationviolation`.
4. Cập nhật/phpMyAdmin: sửa `C:\xampp\phpMyAdmin\config.inc.php` để dùng mật khẩu `12345` (hoặc giá trị bạn cài).
5. Muốn đổi mật khẩu khác, sửa tương ứng trong `python_project/app_server.py` và (nếu dùng) `setup_db.py`.

> `setup_db.py` vẫn tạo schema `datn` mặc định. Nếu muốn dùng script này, hãy đổi tên schema trong file hoặc cập nhật lại `app_server.py` cho khớp.

### Đặt biến môi trường `USE_DB`

| Mục đích | Lệnh PowerShell |
| --- | --- |
| Bật tạm thời trong phiên hiện tại | `$env:USE_DB = '1'` |
| Tắt tạm thời | `$env:USE_DB = '0'` |
| Ghi vĩnh viễn cho user | `setx USE_DB 1` (cần mở PowerShell mới để nhận) |

## 5. Chạy các chế độ chính

### 5.1 Web server Flask

```powershell
.\.venv\Scripts\Activate.ps1
$env:USE_DB = '1'   # hoặc '0'
python yolo\app_server.py
```

Truy cập http://127.0.0.1:8000

- `/` : tổng quan camera
- `/thongke` : thống kê vi phạm (lấy từ MySQL nếu `USE_DB=1`, ngược lại trả dữ liệu mặc định)
- `/bb` : xem mẫu biên bản
- `/LaneViolate1` → `/LaneViolate4` : từng luồng video giả lập

Trong khi chạy, server sẽ lưu ảnh và PDF vào các thư mục tương ứng, đồng thời chèn bản ghi MySQL thông qua hàm `insert_violation_record`.

### 5.2 Script OpenCV độc lập

```powershell
.\.venv\Scripts\Activate.ps1
python python_project\main.py
```

Script hiển thị cửa sổ OpenCV, sử dụng mô hình ở `YoloWeights/best.pt` và bộ đếm line zone của Supervision.

### 5.3 Công cụ hỗ trợ khác
- `testLane.py`: tạo ảnh ROI và PDF offline, hữu ích khi kiểm thử logic lane.
- `trackingMain.py`, `tichhop.py`: minh họa gắn Sort tracker + cảnh báo. Cần chỉnh đường dẫn video/model trước khi chạy.
- `tong_hop.py`: giao diện PyQt5 phát video và lưu biên bản; yêu cầu `PyQt5` và cập nhật lại đường dẫn.
- `speed.py`, `SpeedEstimation.py`, `tets1.py`: code nháp đo tốc độ/tracking; mặc định bị comment nhiều đoạn.

## 6. Dữ liệu và log đầu ra

- Ảnh vi phạm: `python_project/data_xe_may_vi_pham/` và `python_project/data_oto_vi_pham/`
- PDF biên bản: `python_project/BienBanNopPhatXeMay/` và `python_project/BienBanNopPhatXeOTo/`
- Thư mục `runs/detect/` lưu kết quả mặc định của Ultralytics.
- File log trên console bao gồm nhãn `[INFO]`, `[WARN]`, `[ERROR]` từ `app_server.py` để dễ chẩn đoán.

## 7. Khắc phục sự cố phổ biến

- **Không kết nối được MySQL (10061/1045):** kiểm tra dịch vụ MySQL đã bật, mật khẩu `root`, cập nhật `config.inc.php`, và chắc chắn không có tiến trình khác chiếm cổng 3306.
- **`cryptography package is required`:** cài bổ sung `pip install cryptography`.
- **Thiếu model `.pt`:** đặt file đúng vị trí hoặc cập nhật đường dẫn trong code (`model_path` trong `app_server.py`, `main.py`, `testLane.py`...).
- **Không hiển thị video:** xác thực `python_project/Videos/*.mp4` tồn tại, codec hỗ trợ, hoặc đổi đường dẫn tới camera/RTSP.
- **Lỗi đường dẫn `F:/python_project/...`:** nhiều script thử nghiệm chưa chuyển sang đường dẫn tương đối; tìm và chỉnh trước khi sử dụng.

## 8. Ghi chú phát triển

- Flask đang chạy `debug=True` và `threaded=True` chỉ nên dùng khi phát triển.
- Khi triển khai thực tế, hãy tách luồng YOLO sang service riêng hoặc dùng queue để tránh nghẽn.
- `insert_violation_record` được gọi trên từng khung hợp lệ; cân nhắc throttle nếu đưa vào môi trường thực.
- Các thư mục dữ liệu nên backup định kỳ vì số lượng file có thể lớn.

---