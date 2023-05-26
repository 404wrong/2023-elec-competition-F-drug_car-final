import serial
import cv2, os
import sys
import string
import imutils
import numpy as np
import RPi.GPIO as GPIO
import time, bluetooth

LEFT = -1
RIGHT = 1
button_reset = 4
cap = cv2.VideoCapture(0)
# 设置GPIO模式为BCM
GPIO.setmode(GPIO.BCM)
# 配置按钮引脚为输入模式，使用内部上拉电阻
GPIO.setup(button_reset, GPIO.IN, pull_up_down=GPIO.PUD_UP)
default_weight = -10000
server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
port = 1  # 设置端口号
server_sock.bind(("", port))  # 绑定地址和端口
server_sock.listen(5)  # 绑定监听，最大挂起连接数为1
ser = serial.Serial('/dev/ttyS0', 19200)
Green = 18
Red = 17
Yellow = 12
Guang = 23
WEIGHT_FULL = 180
WEIGHT_BLANK = 20
GPIO.setmode(GPIO.BCM)
GPIO.setup(Green, GPIO.OUT)
GPIO.setup(Red, GPIO.OUT)
GPIO.setup(Yellow, GPIO.OUT)
GPIO.setup(Guang, GPIO.IN)
GPIO.setup(27, GPIO.IN)
GPIO.setup(22, GPIO.IN)
GPIO.setup(26, GPIO.IN)
GPIO.setup(19, GPIO.IN)
GPIO.setup(13, GPIO.IN)
GPIO.setup(6, GPIO.IN)
GPIO.setup(5, GPIO.IN)

Sth = GPIO.input(Guang)

num = [0, 0, 0, 1, 1, 1, 1, 1, 1]


def restart_program(channel):
    """重新启动当前程序"""
    # 在此处添加任何清理操作
    GPIO.output(Green, GPIO.LOW)
    GPIO.output(Red, GPIO.LOW)
    GPIO.output(Yellow, GPIO.LOW)
    cap.release()
    server_sock.close()
    python = sys.executable
    os.execl(python, python, *sys.argv)


# 注册按钮按下事件的回调函数
GPIO.add_event_detect(button_reset, GPIO.FALLING, callback=restart_program, bouncetime=200)


def getWeight():
    CLK_pin = 21
    DATA_pin = 20

    GPIO.setup(CLK_pin, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(DATA_pin, GPIO.IN)

    weight_adc = 0
    if GPIO.input(DATA_pin):
        #         print("error")
        return -10000  # Module error
    else:
        # print("yes")
        for i in range(1, 24):
            GPIO.output(CLK_pin, GPIO.HIGH)
            weight_adc = weight_adc << 1
            GPIO.output(CLK_pin, GPIO.LOW)
            if GPIO.input(DATA_pin):
                weight_adc += 1
        GPIO.output(CLK_pin, GPIO.HIGH)
        weight_adc = weight_adc ^ 0x800000
        GPIO.output(CLK_pin, GPIO.LOW)
        a = 1000 * 1000
        GPIO.output(CLK_pin, GPIO.HIGH)
        time.sleep(0.001)
        GPIO.output(CLK_pin, GPIO.LOW)
        # print(weight_adc * -0.0026833 + 43825.5247)
        return weight_adc * -0.0026833 + 43825.5247


def match(pic):
    # cv2.imwrite('0.jpg', pic)
    # 首先匹配正的
    res_list = []
    shape_list = []
    for i in range(1, 9):
        template_pic = cv2.imread(f'template/{i}-d.jpg', cv2.IMREAD_GRAYSCALE)
        # cv2.imwrite("1.jpg",template_pic)
        res = cv2.matchTemplate(pic, template_pic, cv2.TM_SQDIFF)
        res_list.append(cv2.minMaxLoc(res)[0])
        shape_list.append(template_pic.shape[:2])
    # print(res_list)
    # 如果没找到匹配的，就匹配横的
    if min(res_list) < 20 * 1000 * 1000:
        index = res_list.index(min(res_list))
        # print(min(res_list))
        return index + 1, shape_list[index]
    else:
        res_list = []
        shape_list = []
        for i in range(1, 9):
            template_pic = cv2.imread(f'template/{i}-l.jpg', cv2.IMREAD_GRAYSCALE)
            res = cv2.matchTemplate(pic, template_pic, cv2.TM_SQDIFF)
            res_list.append(cv2.minMaxLoc(res)[0])
            shape_list.append(template_pic.shape[:2])
        # print(res_list)
        if min(res_list) < 20 * 1000 * 1000:
            index = res_list.index(min(res_list))
            return index + 1, shape_list[index]
        else:
            res_list = []
            shape_list = []
            for i in range(1, 9):
                template_pic = cv2.imread(f'template/{i}-r.jpg', cv2.IMREAD_GRAYSCALE)
                res = cv2.matchTemplate(pic, template_pic, cv2.TM_SQDIFF)
                res_list.append(cv2.minMaxLoc(res)[0])
                shape_list.append(template_pic.shape[:2])
            # print(res_list)
            if min(res_list) < 20 * 1000 * 1000:
                index = res_list.index(min(res_list))
                return index + 1, shape_list[index]
            else:
                res_list = []
                shape_list = []
                for i in range(1, 9):
                    template_pic = cv2.imread(f'template/{i}-u.jpg', cv2.IMREAD_GRAYSCALE)
                    res = cv2.matchTemplate(pic, template_pic, cv2.TM_SQDIFF)
                    res_list.append(cv2.minMaxLoc(res)[0])
                    shape_list.append(template_pic.shape[:2])
                # print(res_list)
                if min(res_list) < 20 * 1000 * 1000:
                    index = res_list.index(min(res_list))
                    return index + 1, shape_list[index]


class ShapeDetector:
    def __init__(self):
        pass

    def detect(self, c):
        # 初始化形状名称并近似轮廓
        shape = "unidentified"
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.04 * peri, True)
        return approx


def get_integer_cv(image, cnt):
    resized = image  # imutils.resize(image, width=300)
    ratio = image.shape[0] / float(resized.shape[0])
    # 将调整后的图像转换为灰度，稍微模糊它，并阈值化
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    # cv2.imwrite('7.jpg', gray)
    img4 = cv2.Canny(gray, 100, 200)
    # cv2.imwrite('13.jpg', img4)
    thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)[1]
    # cv2.imwrite('6.jpg', thresh)
    # 在阈值化图像中找到轮廓并初始化形状检测器
    cnts = cv2.findContours(img4.copy(), cv2.RETR_TREE,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    sd = ShapeDetector()
    rect_list = []
    # 遍历所有轮廓
    for c in cnts:
        if cv2.contourArea(c) > 100:
            # 计算轮廓的中心，然后仅使用轮廓检测形状的名称
            M = cv2.moments(c)
            cX = int((M["m10"] / (1 + M["m00"])) * ratio)
            cY = int((M["m01"] / (1 + M["m00"])) * ratio)
            rec = sd.detect(c)
            if len(rec) == 4:
                rect_list.append((rec, cX, cY))
    # print(rect_list)
    blur = cv2.blur(thresh, (3, 3))
    a = []
    for each_rect, x, y in rect_list:
        try:
            target = np.array([[0., 0.],
                               [0., 120.0],
                               [90.0, 120.0],
                               [90.0, 0.]], dtype=np.float32)
            M = cv2.getPerspectiveTransform(np.array(each_rect, dtype=np.float32), target)
            perspective = cv2.warpPerspective(blur, M, (90, 120))
            # cv2.imshow('7', perspective)

            res = match(perspective)
            if res is None:
                res = match(cv2.resize(perspective, (95, 130)))
            if res is not None:
                tmptmp = 1
                for i, _ in a:
                    if i == res[0]:
                        tmptmp = 0
                        break
                if tmptmp == 1:
                    a.append((res[0], x))
                if len(a) == cnt:
                    return a


        except IOError:
            pass
    return a


def get_integer(cnt):
    global num
    global cap
    cap.release()
    cap = cv2.VideoCapture(0)
    ret, image = cap.read()
    a = get_integer_cv(image, cnt)
    adjust = 0
    while len(a) != cnt:
        print(a)
        time.sleep(1)
        ret, image = cap.read()
        for i in get_integer_cv(image, cnt):
            if i[0] not in [k[0] for k in a]:
                a.append(i)
        if cnt == 4 and len(a) == 3:
            adjust = 1
            print('try to adjust')
            for i in a:
                num[i[0]] = 0
            break
    a.sort(key=lambda n: n[1])
    a = [p[0] for p in a]
    for i in a:
        num[i] = 0
    if adjust == 1:
        for i in range(9):
            if num[i] == 1:
                a.append(i)
                print('adjust succeed')
    return a


def get_r_detected():
    a = GPIO.input(5) + GPIO.input(26) + GPIO.input(22)
    if a > 2:
        return 1
    else:
        return 0


def get_l_detected():
    a = GPIO.input(6) + GPIO.input(27) + GPIO.input(13)
    if a > 2:
        return 1
        print('get_l_detected')
    else:
        return 0


def get_ol_detected():
    # print(f'6:{GPIO.input(6)},27:{GPIO.input(27)},13:{GPIO.input(13)},5:{GPIO.input(5)}+26:{GPIO.input(26)}+22:{GPIO.input(22)}')
    if GPIO.input(6) + GPIO.input(27) + GPIO.input(13) > 2 or GPIO.input(5) + GPIO.input(26) + GPIO.input(22) > 2:
        return 1
        print('get_l_detected')
    else:
        return 0


def get_ex_detected():
    a = GPIO.input(27) + GPIO.input(22) + GPIO.input(26) + GPIO.input(19) + GPIO.input(13) + GPIO.input(6) + GPIO.input(
        5)
    if a > 5:
        return 1
    else:
        return 0


# 定义1为向前走(no capture along)，2为向左走，3为向右走，4为掉头，5为走指定距离（识别），6为走指定距离（终点）,7为停止,8 only along,9 走指定距离（返回）,a为向前走(no capture stop)
def send(s):
    print(s)
    data_to_send = (s).encode()
    ser.write(data_to_send)


def finished(pos, dir):
    time.sleep(2)
    GPIO.output(Red, GPIO.HIGH)
    # 第一次检测，称重检测,物品取走
    print('first weight test')
    while 1:
        a = getWeight()
        if a != -10000:
            if a >= 50 + default_weight:
                print(a)
                break
    print('weight test end')
    GPIO.output(Red, GPIO.LOW)
    time.sleep(2)
    send('4')
    time.sleep(5)
    send('1')
    time.sleep(0.2)
    while 1:
        if get_ol_detected() == 1:
            send('7')
            break
    time.sleep(1)
    if dir == 1:
        send('3')
    else:
        send('2')
    time.sleep(1)
    if pos == 3 or pos == 4:
        send('1')
        while 1:
            if get_ol_detected() == 1:
                send('7')
                break
        time.sleep(1)
    if pos == 3:
        send('3')
    elif pos == 4:
        send('2')
        pos = 3
    time.sleep(1)
    send('a')
    time.sleep(10)
    send('7')
    # 等待返回信号#todo
    # 等待执行完毕

    GPIO.output(Green, GPIO.HIGH)
    while 1:
        continue


# while 1:
#    print(f'r:{get_r_detected()}, l:{get_l_detected()}, all:{get_ex_detected()}')
# while 1:
#    get_ol_detected()
if __name__ == '__main__':
    try:
        while default_weight == -10000:
            default_weight = getWeight()
        GPIO.output(Green, GPIO.LOW)
        GPIO.output(Red, GPIO.LOW)
        GPIO.output(Yellow, GPIO.LOW)
        print('default_weight=' + str(default_weight))
        print('start')
        send('7')
        dir = 0
        pos = 0
        goal = -1
        # 第一次检测，检测目标值
        while 1:
            t = get_integer(1)
            if len(t) == 1:
                goal = t[0]
                print(goal)
                break
        # 第一次检测，称重检测
        print('first weight test')
        while 1:
            a = getWeight()
            if a != -10000:
                print(a)
                if a >= WEIGHT_FULL + default_weight:
                    print(a)
                    break
        print('weight test end')
        # 向前走
        send('1')
        while 1:
            if get_ex_detected() == 1:
                send('7')
                break
        time.sleep(1)
        # 第一次判断左右
        send('2')
        dir = 1
        time.sleep(1)
        send('6')
        # ===============================================================
        time.sleep(2)
        send('4')#掉头
        time.sleep(1)
        GPIO.output(Yellow, GPIO.HIGH)
        try:#开蓝牙
            client_sock, address = server_sock.accept()  # 阻塞等待连接
            print('连接成功')
            print("Accepted connection from ", address)
            data = client_sock.recv(1024).decode()
        except:
            pass
        GPIO.output(Yellow, GPIO.LOW)
        send('1')#继续走
        while 1:
            if get_ex_detected() == 1:
                send('7')
                break
        time.sleep(1)
        send('2')#左转
        time.sleep(1)
        send('1')#直行
        time.sleep(1.3)
        send('7')#停止
        t = get_integer(2)
        print(t)
        time.sleep(1)
        send('1')#直行到路口
        while 1:
            if get_ex_detected() == 1:
                send('7')
                break
        time.sleep(1)
        if goal == t[0]:
            send('2')
            dir = 1
            time.sleep(1)
            send('6')
        elif goal == t[1]:
            send('3')
            dir = 0
            time.sleep(1)
            send('6')
        time.sleep(2)
        # ===============================================================
        print('finish')
        GPIO.output(Red, GPIO.HIGH)
        while 1:
            pass
    except KeyboardInterrupt:
        GPIO.cleanup()
