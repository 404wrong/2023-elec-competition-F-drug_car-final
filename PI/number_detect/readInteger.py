import cv2
import sys
import string

import imutils
import numpy as np

def match(pic):
    #cv2.imwrite('0.jpg', pic)
    # 首先匹配正的
    res_list = []
    shape_list = []
    for i in range(1, 9):
        template_pic = cv2.imread(f'template/{i}-d.jpg', cv2.IMREAD_GRAYSCALE)
        #cv2.imwrite("1.jpg",template_pic)
        res = cv2.matchTemplate(pic, template_pic, cv2.TM_SQDIFF)
        res_list.append(cv2.minMaxLoc(res)[0])
        shape_list.append(template_pic.shape[:2])
    #print(res_list)
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
        #print(res_list)
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


cap=cv2.VideoCapture(0)
while(1):
    ret,image=cap.read()
    # 加载图像并将其调整图像大小，以便更好地近似形状
    resized = imutils.resize(image, width=300)
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
                rect_list.append(rec)
        res_list = []
    # print(rect_list)
    blur = cv2.blur(thresh, (3, 3))
    a = -1
    for each_rect in rect_list:
        try:
            target = np.array([[0., 0.],
                               [0., 120.0],
                               [90.0, 120.0],
                               [90.0, 0.]], dtype=np.float32)
            M = cv2.getPerspectiveTransform(np.array(each_rect, dtype=np.float32), target)
            perspective = cv2.warpPerspective(blur, M, (90, 120))
            # cv2.imshow('7', perspective)

            res = match(perspective)
            if res is not None:
                a = res[0]
                print(a)

            # print(res)
            res_list.append((res, each_rect[1]))

            # if res is not None:
            #     ser.write(res[0])

        # template = cv.imread('template/7-shu.jpg', cv.IMREAD_GRAYSCALE)
        # height, width = template.shape[:2]
        # res = cv.matchTemplate(perspective, template, cv.TM_SQDIFF)
        # min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
        # print(min_val)
        # left_top = min_loc
        # right_bottom = (left_top[0] + width, left_top[1] + height)
        # cv.rectangle(img=perspective, pt1=left_top, pt2=right_bottom, color=(0, 0, 255), thickness=2)
        # cv.imshow('result', perspective)

        except IOError:
            pass
    print(a)
    cv2.putText(image, str(a), (20,120), cv2.FONT_HERSHEY_SIMPLEX,
                2, (255, 255, 255), 2)
    cv2.imshow("capture",image)
