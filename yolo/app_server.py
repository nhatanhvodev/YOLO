import datetime
import webbrowser
import os
import numpy as np
import logging

from flask import Flask, jsonify, url_for
from flask import render_template, Response
from flask_cors import CORS
from flask_mysqldb import MySQL
from testLane import *

app = Flask(__name__, static_folder='static')
CORS(app)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'yolo'
mysql = MySQL(app)

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# Apply Flask CORSx`
# CORS(app)
# app.config['CORS_HEADERS'] = 'Content-Type'
#
@app.route('/test', methods=['GET'])
def get_violate():
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT nametransportation.vh_name  ,  transportationviolation.date_violate , COUNT(*) AS total_violate FROM transportationviolation INNER JOIN nametransportation ON transportationviolation.id_name = nametransportation.id_name  GROUP BY nametransportation.id_name ;")
        users = cur.fetchall()
        cur.close()
        return jsonify(users)
    except Exception as e:
        logging.error(f"DB error /test: {e}")
        return jsonify({'error': 'DB unavailable'}), 503


@app.route('/test1', methods=['GET'])
def get_violate_current():
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT nametransportation.vh_name  ,   transportationviolation.date_violate , COUNT(*) AS total_violate FROM transportationviolation INNER JOIN nametransportation ON transportationviolation.id_name = nametransportation.id_name  where transportationviolation.date_violate = curdate() GROUP BY nametransportation.id_name ;")
        users = cur.fetchall()
        cur.close()
        return jsonify(users)
    except Exception as e:
        logging.error(f"DB error /test1: {e}")
        return jsonify({'error': 'DB unavailable'}), 503


# @app.route('/create', methods=['GET'])
def create(cls):
    with app.app_context():
        cur = mysql.connection.cursor()
        ngay_hien_tai = datetime.date.today()
        cur.execute("insert into transportationviolation(id_name , date_violate) values (%s, %s)",
                    (cls + 1, ngay_hien_tai))
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'User created successfully'})


def call_route(cls):
    url_for('create', cls=cls)
    # return redirect(url_for('create', cls=cls))


def video_detection(path_x=""):
    # Base directories (created if missing) for generated assets
    # Using global BASE_DIR
    DIR_XE_MAY_VP = os.path.join(BASE_DIR, 'data_xe_may_vi_pham')
    DIR_OTO_VP = os.path.join(BASE_DIR, 'data_oto_vi_pham')
    DIR_BIEN_BAN_M = os.path.join(BASE_DIR, 'BienBanNopPhatXeMay')
    DIR_BIEN_BAN_CTB = os.path.join(BASE_DIR, 'BienBanNopPhatXeOTo')
    for d in [DIR_XE_MAY_VP, DIR_OTO_VP, DIR_BIEN_BAN_M, DIR_BIEN_BAN_CTB]:
        os.makedirs(d, exist_ok=True)

    cap = cv2.VideoCapture(path_x)
    model_path = os.path.join(BASE_DIR, 'best_new', 'vehicle.pt')
    if not os.path.isfile(model_path):
        fallback = os.path.join(BASE_DIR, 'YoloWeights', 'yolov8n.pt')
        logging.warning(f"Custom model missing ({model_path}), falling back to {fallback}")
        model_path = fallback
    try:
        model = YOLO(model_path)
    except Exception as e:
        logging.error(f"Failed to load YOLO model: {e}")
        # Return raw frames without detection
        while cap.isOpened():
            ok, frm = cap.read()
            if not ok:
                break
            yield frm
        return
    stt_m = 0
    stt_ctb = 0
    examBB = createBB.infoObject()
    dataBienBan_M = DIR_BIEN_BAN_M
    dataBienBan_CTB = DIR_BIEN_BAN_CTB

    # results = model.track(source="Videos/test4.mp4", show=True, stream=True)
    while cap.isOpened():
        success, frame = cap.read()
        if success:
            #  Dự đoán
            results = model(frame)

            # lấy ra frame sau khi đc gắn nhãn
            annotated_frame = results[0].plot()

            # lấy kích thước (height , width , _ )
            # print("kích thước frame : ", annotated_frame.shape)

            # Hiển thị lên
            # cv2.imshow("Display ", annotated_frame)
            # results = model.track(source="Videos/test4.mp4", show=True, tracker="bytetrack.yaml", stream=True)
            for result in results:
                boxes = result.boxes.numpy()

                # Lấy tên class
                name = result.names

                # lấy tất cả các thông số trong một list tọa độ các đối tượng (x0 ,y0, x1, y1, )
                # print("list 1 ", boxes.xyxy)
                list_2 = []

                # Lấy tất các các thông số của nhiều đối tượng (x0, y0 , x1 , y1 , id ,độ chính xác , loại class)
                # print("Boxes ", boxes)

                for box in boxes:
                    # lấy tên class tương ứng bounding box trong model đã custom
                    # print("Class : ", box.cls)

                    # lấy tọa độ của bounding box đối tượng (x0y0 , x1y1)
                    print("xyxy : ", box.xyxy[0])

                    # Lấy độ chính xác của bounding box đối tượng
                    # print("Độ chính xác : ", box.conf)

                    print("ID------------------- ", box.id)
                    font = cv2.FONT_HERSHEY_SIMPLEX

                    # box.xyxy trả về ma trận 2 chiều dạng [[x0, y0 , x1 ,y1]]
                    # đó là tọa độ bounding box
                    print("box.xyxy", box.xyxy)
                    # org (Tọa độ cần vẽ lên bounding box (x,y) )
                    # thêm int để lấy số nguyên (nghĩa là lấy x0 , y0 để vẽ lên bounding box)
                    org = (int(box.xyxy[0][0]), int(box.xyxy[0][1]))

                    # fontScale (Độ lớn của chữ)
                    fontScale = 0.5

                    # Blue color in RGB (Màu sắc của chữ)
                    color = ()

                    # Line thickness of 2px (Độ dày của chữ )
                    thickness = 2

                    # Lấy tọa độ bounding box
                    x = int(box.xyxy[0][0])
                    y = int(box.xyxy[0][1])
                    w = int(box.xyxy[0][2])
                    h = int(box.xyxy[0][3])

                    text = str(name[box.cls[0]] + " ") + str(round(box.conf[0], 2))

                    #####################################################################
                    # Xe OTO vi pham lane XE MAY
                    start_line_motor = (0 * int(frame.shape[1] / 10), int((2 * frame.shape[0] / 10)))
                    # 11/20 = 5.5 / 10
                    end_line_motor = (11 * int(frame.shape[1] / 20), int(8 * frame.shape[0] / 10))
                    canh_bao_vi_pham_lane_xe_may = start_line_motor[0] < box.xyxy[0][0] < end_line_motor[0] and \
                                                   start_line_motor[1] < box.xyxy[0][
                                                       1] < end_line_motor[1]
                    #####################################################################

                    # ##################################################################
                    # Xe máy vi pham lane OTO
                    # lane xe ô tô (trục y phải khớp với vùng roi)
                    # trục x lấy 6/10 , trục y lấy 3/10
                    start_line_car = (22 * int(frame.shape[1] / 40), int((2 * frame.shape[0] / 10)))

                    # lấy từ 6/10 đến hết trục X , trục y lấy 8/10
                    end_line_car = (int(frame.shape[1]), int(8 * frame.shape[0] / 10))

                    canh_bao_vi_pham_lane_oto = start_line_car[0] < box.xyxy[0][0] < end_line_car[0] and \
                                                start_line_car[1] < box.xyxy[0][
                                                    1] < end_line_car[1]
                    # filterDataViolate(frame, (0, int(5 * frame.shape[0] / 10)),
                    #                   (int(frame.shape[1]), int(55 * frame.shape[0] / 10)))
                    center_x = (x + w) // 2
                    center_y = (y + h) // 2
                    filterData = 0 <= center_x <= (int(frame.shape[1])) and int(
                        5 * frame.shape[0] / 10) <= center_y <= int(
                        52 * frame.shape[0] / 100)
                    #####################################################################

                    # vẽ ra vùng lane xe máy và oto
                    # image = cv2.rectangle(frame, start_line_car, end_line_car
                    #                       , (0, 0, 255), thickness)
                    image = cv2.rectangle(frame, start_line_motor, end_line_motor
                                          , (255, 0, 255), thickness)

                    # xét vùng roi theo trục Y
                    if int((2 * frame.shape[0]) / 10) < int(box.xyxy[0][1]) < int((8 * frame.shape[0]) / 10):
                        cv2.rectangle(frame, (x, y), (w, h), (36, 255, 12), 2)
                        cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)
                        if box.cls[0] == 1:
                            if canh_bao_vi_pham_lane_oto:
                                draw_text(frame, name[box.cls[0]] + " warning", font_scale=0.5,
                                          pos=(int(box.xyxy[0][0]), int(box.xyxy[0][1])),
                                          text_color_bg=(0, 0, 0))
                                print("tọa độ xe máy vi phạm : ", box.xyxy[0])
                                # cắt hình ảnh xe máy
                                # cropped_frame = frame[round(y, 1) - 100:round(y + h, 2) + 100,
                                #                 round(x, 1) - 100: round(x + w, 1) + 100]

                                # Cắt hình làn ô tô
                                # cropped_frame = frame[int((3 * frame.shape[0]) / 10):int((8 * frame.shape[0]) / 10),
                                #                 6 * int(frame.shape[1] / 10):int(frame.shape[1])]
                                if filterData:
                                    stt_m += 1
                                    imageMotorViolate(frame, int((2 * frame.shape[0]) / 10),
                                                      int((8 * frame.shape[0]) / 10), 2 * int(frame.shape[1] / 10),
                                                      int(frame.shape[1]), stt_m)
                                    stt_BB_m = os.path.join(dataBienBan_M, f"{stt_m}.pdf")
                                    frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                                    # Tạo tệp tạm thời và lưu ảnh PIL vào đó
                                    temp_image = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
                                    frame_pil.save(temp_image.name)
                                    create(box.cls[0])
                                    xe_may_image_path = os.path.join(DIR_XE_MAY_VP, f"{stt_m}.jpg")
                                    createBB.bienBanNopPhat(examBB,
                                                            temp_image.name,
                                                            xe_may_image_path,
                                                            stt_BB_m)
                                    temp_image.close()

                                    # cv2.imwrite("F:\python_project\data_xe_may_vi_pham\ " + str(count) + ".xe_may_lan_lan.jpg",
                                    #             cropped_frame)
                                    # frame = cv2.putText(frame, name[box.cls[0]] + " warning", org, font, fontScale, (0, 0, 255),
                                    #                     thickness, cv2.LINE_AA)
                            else:
                                draw_text(frame, text, font_scale=0.5,
                                          pos=(int(box.xyxy[0][0]), int(box.xyxy[0][1])),
                                          text_color=(255, 255, 255), text_color_bg=(78, 235, 133))
                                # frame = cv2.putText(frame, text, org, font, fontScale,
                                #                     generate_random_color(int(box.cls[0])), thickness,
                                #                     cv2.LINE_AA)
                        if box.cls[0] == 0 or box.cls[0] == 3 or box.cls[0] == 4:
                            if canh_bao_vi_pham_lane_xe_may:
                                draw_text(frame, name[box.cls[0]] + " warning", font_scale=0.5,
                                          pos=(int(box.xyxy[0][0]), int(box.xyxy[0][1])),
                                          text_color_bg=(0, 0, 0))
                                # Cắt hình làn ô tô
                                if filterData:
                                    stt_ctb += 1
                                    cropped_frame = frame[
                                                    int((3 * frame.shape[0]) / 10):int((8 * frame.shape[0]) / 10),
                                                    6 * int(frame.shape[1] / 10):int(frame.shape[1])]
                                    imageCTBViolate(frame, int((2 * frame.shape[0]) / 10),
                                                    int((8 * frame.shape[0]) / 10), 0 * int(frame.shape[1] / 10),
                                                    6 *
                                                    int(frame.shape[1] / 10), stt_ctb)

                                    stt_BB_CTB = os.path.join(dataBienBan_CTB, f"{stt_ctb}.pdf")
                                    frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                                    # Tạo tệp tạm thời và lưu ảnh PIL vào đó
                                    temp_image = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
                                    frame_pil.save(temp_image.name)
                                    create(box.cls[0])
                                    oto_image_path = os.path.join(DIR_OTO_VP, f"{stt_ctb}.jpg")
                                    createBB.bienBanNopPhat(examBB,
                                                            temp_image.name,
                                                            oto_image_path,
                                                            stt_BB_CTB)
                                    temp_image.close()
                            else:
                                draw_text(frame, text, font_scale=0.5,
                                          pos=(int(box.xyxy[0][0]), int(box.xyxy[0][1])),
                                          text_color=(255, 255, 255), text_color_bg=(77, 229, 26))

                    # muốn lấy 5/10 phần của height tính từ trên xuống
                    start_point = (0, int((2 * frame.shape[0]) / 10))
                    # vẽ hết chiều rộng và chiểu cao lấy 9/10
                    end_point = (int(frame.shape[1]), int((8 * frame.shape[0]) / 10))
                    color = (255, 0, 0)
                    thickness = 2

                    # vẽ ra cái ROI
                    image = cv2.rectangle(frame, start_point, end_point, color, thickness)

                    # scale_percent = 30
                    # width = int(image.shape[1] * scale_percent / 100)
                    # height = int(image.shape[0] * scale_percent / 100)
                    # dim = (width, height)

                    # resize Image
                    # resize = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
                    # cv2.imshow("Roi ", image)
                    yield image
        else:
            break
    cv2.destroyAllWindows()


def generate_frames(path_x):
    # If file doesn't exist fallback to webcam 0, else placeholder
    if not os.path.isfile(path_x):
        cap_test = cv2.VideoCapture(0)
        if not cap_test.isOpened():
            # yield a placeholder frame repeatedly
            placeholder = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(placeholder, 'Video source not found', (40, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
            while True:
                ref, buffer = cv2.imencode('.jpg', placeholder)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            # Use webcam stream without detection as fallback
            while True:
                ok, frm = cap_test.read()
                if not ok:
                    break
                ref, buffer = cv2.imencode('.jpg', frm)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            cap_test.release()
            return

    yolo_output = video_detection(path_x)
    for detection_ in yolo_output:
        ref, buffer = cv2.imencode('.jpg', detection_)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/bb")
def bb():
    return render_template("bb.html")


@app.route("/thongke")
def tk():
    return render_template("thongke.html")


@app.route("/Hethongcamera1")
def camera_1():
    # Giữ đường dẫn cũ làm alias Camera 1
    return render_template("laneviolate1.html")

@app.route("/LaneViolate1")
def lane_violate_1():
    return render_template("laneviolate1.html")

@app.route("/LaneViolate2")
def lane_violate_2():
    return render_template("laneviolate2.html")

@app.route("/LaneViolate3")
def lane_violate_3():
    return render_template("laneviolate3.html")

@app.route("/LaneViolate4")
def lane_violate_4():
    return render_template("laneviolate4.html")

@app.route("/camera1")
def video():
    video_path = os.path.join(os.path.dirname(__file__), 'Videos', 'main.mp4')
    return Response(generate_frames(path_x=video_path), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/camera2")
def video2():
    video_path = os.path.join(os.path.dirname(__file__), 'Videos', 'lane.mp4')
    return Response(generate_frames(path_x=video_path), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/camera3")
def video3():
    video_path = os.path.join(os.path.dirname(__file__), 'Videos', 'test9.mp4')
    return Response(generate_frames(path_x=video_path), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/camera4")
def video4():
    video_path = os.path.join(os.path.dirname(__file__), 'Videos', 'traffic2.mp4')
    return Response(generate_frames(path_x=video_path), mimetype='multipart/x-mixed-replace; boundary=frame')



if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        webbrowser.open('http://127.0.0.1:8000/')
    app.run(host="0.0.0.0", port=8000, debug=True, use_reloader=True)
