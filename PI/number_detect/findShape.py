import argparse
import imutils
import cv2

def match(pic):
    cv2.imwrite('8.jpg', pic)
    # 首先匹配正的
    res_list = []
    shape_list = []
    for i in range(1, 9):
        template_pic = cv2.imread(f'template/{i}-shu.jpg', cv2.IMREAD_GRAYSCALE)
        res = cv2.matchTemplate(pic, template_pic, cv2.TM_SQDIFF)
        res_list.append(cv2.minMaxLoc(res)[0])
        shape_list.append(template_pic.shape[:2])
    print(res_list)
    # 如果没找到匹配的，就匹配横的
    if min(res_list) < 10 * 1000 * 1000:
        index = res_list.index(min(res_list))
        # print(min(res_list))
        return index + 1, shape_list[index]
    else:
        res_list = []
        shape_list = []
        for i in range(1, 9):
            template_pic = cv2.imread(f'template/{i}-heng.jpg', cv2.IMREAD_GRAYSCALE)
            res = cv2.matchTemplate(pic, template_pic, cv2.TM_SQDIFF)
            res_list.append(cv2.minMaxLoc(res)[0])
            shape_list.append(template_pic.shape[:2])
        print(res_list)
        if min(res_list) < 10 * 1000 * 1000:
            index = res_list.index(min(res_list))
            return index + 1, shape_list[index]
        # else:
        #     res_list = []
        #     shape_list = []
        #     for i in range(1, 9):
        #         template_pic = cv2.imread(f'template/{i}-jia.jpg', cv2.IMREAD_GRAYSCALE)
        #         res = cv2.matchTemplate(pic, template_pic, cv2.TM_SQDIFF)
        #         res_list.append(cv2.minMaxLoc(res)[0])
        #         shape_list.append(template_pic.shape[:2])
        #     if min(res_list) < 10 * 1000 * 1000:
        #         index = res_list.index(min(res_list))
        #         return index + 1, shape_list[index]



class ShapeDetector:
    def __init__(self):
        pass

    def detect(self, c):
        # 初始化形状名称并近似轮廓
        shape = "unidentified"
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.05 * peri, True)
        return approx
        ## 如果形状是一个三角形，它将有3个顶点
        #if len(approx) == 3:
        #    shape = "triangle"
        ## 如果形状有4个顶点，它要么是正方形，要么是矩形
        #elif len(approx) == 4:
        #    print(approx)
        #    # 计算轮廓的包围框，并使用包围框计算高宽比
        #    (x, y, w, h) = cv2.boundingRect(approx)
        #    ar = w / float(h)
        #    # 正方形的长宽比大约等于1，否则，形状就是矩形
        #    shape = "square" if ar >= 0.95 and ar <= 1.05 else "rectangle"
        ## 如果形状是一个五边形，它将有5个顶点
        #elif len(approx) == 5:
        #    shape = "pentagon"
        ## 否则，我们假设形状是一个圆
        #else:
        #    shape = "circle"+str(len(approx))
        ## 返回形状的名称
        #return shape


# 加载图像并将其调整图像大小，以便更好地近似形状
image = cv2.imread("testNew/0.jpg")
#(h, w) = image.shape[:2]
#image=image[0:h, 0:w//2]
resized = image #imutils.resize(image, width=300)
ratio = image.shape[0] / float(resized.shape[0])
# 将调整后的图像转换为灰度，稍微模糊它，并阈值化
gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
cv2.imwrite('7.jpg', gray)
img4 = cv2.Canny(gray, 100, 200)
cv2.imwrite('13.jpg', img4)
thresh = cv2.threshold(gray, 104, 255, cv2.THRESH_BINARY)[1]
cv2.imwrite('6.jpg', thresh)
# 在阈值化图像中找到轮廓并初始化形状检测器
cnts = cv2.findContours(img4.copy(), cv2.RETR_EXTERNAL,
                        cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
sd = ShapeDetector()
rect_list = []
# 遍历所有轮廓
i=7
for c in cnts:
    if cv2.contourArea(c)>100:
        # 计算轮廓的中心，然后仅使用轮廓检测形状的名称
        M = cv2.moments(c)
        cX = int((M["m10"] / (1+M["m00"])) * ratio)
        cY = int((M["m01"] / (1+M["m00"])) * ratio)
        shape = sd.detect(c)
        print(shape)
        # 将轮廓(x, y)坐标乘以调整比例，然后在图像上绘制轮廓和形状的名称
        c = c.astype("float")
        c *= ratio
        c = c.astype("int")
        cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
        print(len(shape))
        print(c)
        print(i)
        cv2.putText(image, str(len(shape)), (cX, cY), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (255, 255, 255), 2)
        # 显示输出图像
        cv2.imwrite(f'{i}.jpg', image)
        i=i+1
