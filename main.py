from maix import camera, display, image, nn, time,app, key
import math
import statistics

cap_state = False
cap_frame = 0
max_frame = 20
detector = None
def on_key(key_id, state):
    global cap_state, cap_frame
    '''
        this func is called in a single thread
    '''
    print(f"key: {key_id}") # key.c or key.State.KEY_RELEASED
    
    if cap_state == False:
        if (key_id == 116):
            app.set_exit_flag(True)
        elif (key_id == 352):
            cap_state = True
            cap_frame = max_frame

def btn_event(cap_state, img, cap_frame, results, prev_count):
    RECT_COLOR = image.COLOR_RED
    RECT_SCALE = 1
    count  = 0
    if cap_frame == 0:
        cap_state = False
        cap_frame = 0
        results.clear()
    if cap_state:
        cap_frame -= 1
        objs = detector.detect(img, conf_th = 0.27, iou_th = 0.45)
        img.draw_string(round(img.width()/2 - 100), img.height() - 40, f"===========", scale=2.5, color=image.COLOR_GREEN, thickness=2)
        for obj in objs:
            count += 1
            #mid_pos = max(img.height() - 10, obj.y + (obj.h/2))
            img.draw_rect(obj.x, obj.y, obj.w, obj.h, RECT_COLOR, RECT_SCALE)
            #img.draw_string(obj.x, mid_pos, f"**", scale=3, color=image.COLOR_RED)
        results.append(count)
        prev_count = filter_noise(results)
    return cap_state, img, cap_frame, prev_count

def filter_noise(results):
   count = round(statistics.median(results))
   return count

def main(disp):
    global detector, cap_state, cap_frame
    detector = nn.YOLO11(model="/root/models/model-fish-640.mud", dual_buff = True)
    cam = camera.Camera(1280, 1280, detector.input_format())
    cap_state = False
    results = []
    all_results = []

    prev_count = 0
    key_obj = key.Key(on_key)
    while not app.need_exit():
        img = cam.read()
        cap_state, img, cap_frame, prev_count = btn_event(cap_state, img, cap_frame, results, prev_count)
        img.draw_string(2, 40, f'valid: {prev_count} capture_frame: {cap_frame}', image.COLOR_WHITE, scale=2.5, thickness= 2)
        disp.show(img)

disp = display.Display()
try:
    main(disp)
except Exception:
    import traceback
    msg = traceback.format_exc()
    img = image.Image(disp.width(), disp.height())
    print("Error:", msg)
    disp.show(img)
    while not app.need_exit():
        time.sleep_ms(100)
