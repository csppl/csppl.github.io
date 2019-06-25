import cv2
import numpy as np
import os


# 열을 잘라주는 함수
def crop_col_img(img_path):
    print(os.getcwd()+img_path)
    img = cv2.imread(os.getcwd() + img_path)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    x_len = img_gray.shape[1]
    y_len = img_gray.shape[0]

    threshold = int(y_len / 200 * 0.6)

    check_list = []
    for x in range(x_len):
        not_white = 0
        for y in range(0, y_len, 200):
            if img_gray[y][x] != 255:
                not_white += 1
        # 임계치보다 white가 아닌부분이 많이 나오면 check_list에 추가해줌
        if not_white > threshold:
            check_list.append(x)
    if len(check_list) > 0:
        # check list에서 가장 작은 x좌표, 가장 큰 x좌표로 indexing
        x_min_point = np.min(check_list)
        x_max_point = np.max(check_list)
        crop_img = img[:, x_min_point:x_max_point]
        if crop_img.shape[1] == 0:
            return img
        return crop_img
    # check list를 하나도 못찾으면 그냥 이미지 리턴
    return img


# 이미지를 행을 분리시켜주는 함수
def split_img(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    y_shape = img_gray.shape[0]
    x_shape = img_gray.shape[1]
    split_point_y = []
    line = 0
    for y in range(y_shape):
        ck_color = 0
        for x in range(0, x_shape, 15):
            # 한줄이 다 같은색이면
            if img_gray[y][x] == img_gray[y][0]:
                ck_color += 1
            else:
                line = 0
                break
        if ck_color >= int(x_shape/15):
            line += 1
            if line == 25:
                split_point_y.append(y)
                line = 0
    split_img_list = []
    # 분리 못하면 그냥 원래 img 리턴
    if len(split_point_y) == 0:
        return [img]
    start = 0
    for point in split_point_y:
        if (point - start) > 100:
            split_img_list.append(img[start:point][:])
        start = point
    if (point - start) > 100:
        split_img_list.append(img[start:][:])
    #     print('len(split_point_y) : {} '.format(len(split_point_y)))
    #     print('len(split_img_list) : {} '.format(len(split_img_list)))

    return split_img_list


def img_concat(split_img_list):
    sum_len = 0
    concat_img_list = []
    over_1500_img = []
    for img in split_img_list:
        concat_img_list.append(img)
        sum_len = sum_len + img.shape[0]
        # 1500보다 길면 지금까지의 append된 이미지를 concat
        if sum_len > 1500:
            over_1500_img.append(np.concatenate(concat_img_list, axis=0))
            concat_img_list = []
            sum_len = 0
        else:
            continue
    # 딱 1500별로 잘리는 케이스 아니면 나머지에 더해줌
    if len(concat_img_list) != 0:
        over_1500_img.append(np.concatenate(concat_img_list, axis=0))
    return over_1500_img


# yolo로 뽑은box에 대한 정보를 관리하는 클래스
class yolo_box_info:
    # 원본이미지, YOLO로 예측된 박스정보를 저장하는 class
    def __init__(self, img, top_x, top_y, btm_x, btm_y):
        # 오리지널 이미지와
        self.origin_img = img
        # yolo box에 대한 좌표정보가 들어감
        self.top_x = top_x
        self.top_y = top_y
        self.btm_x = btm_x
        self.btm_y = btm_y
        self.height = self.btm_y - self.top_y
        self.width = self.btm_x - self.top_x

    def return_box(self):
        return self.origin_img[self.top_y:self.btm_y, self.top_x:self.btm_x]

    def __str__(self):
        print_str = f'top_x : {self.top_x} top_y : {self.top_y} btm_x : {self.btm_x} btm_y : {self.btm_y} '
        print_str2 = f'height : {self.height} width : {self.width} '

        return print_str + print_str2


# yolo box + 위아래 200에 대한 정보를 관리하는 클래스
class cv_box_info():
    def __init__(self, yolo_box, img, top_x, top_y, btm_x, btm_y):
        self.yolo_box = yolo_box
        self.origin_img = img
        self.top_x = top_x
        self.top_y = top_y
        self.btm_x = btm_x
        self.btm_y = btm_y
        self.height = self.btm_y - self.top_y
        self.width = self.btm_x - self.top_x

    def return_box(self):
        return self.yolo_box.origin_img[self.top_y:self.btm_y, self.top_x:self.btm_x]

    def __str__(self):
        print_str = f'top_x : {self.top_x} top_y : {self.top_y} btm_x : {self.btm_x} btm_y : {self.btm_y} '
        print_str2 = f'height : {self.height} width : {self.width} '

        return print_str + print_str2


# 컨투어 이미지 정보를 관리하는 클래스
class cnt_img_info:
    def __init__(self, img, y, y_h):
        self.img = img
        self.y = y
        self.y_h = y_h


default_img_path = r'C:\STUDY\FindSizeProject\django_app\boards\static\boards\images\404.png'
# yolo table을 기준으로 위아래 150으로 뽑아주는 함수
def yolo_split(original_img, tfnet):
    # yolo box저장 list
    yolo_box_list = []
    # 위아래 150 추가한 이미지 저장 리스트
    cv_box_list = []
    predictions = tfnet.return_predict(original_img)
    # yolo로 예측하고 그 박스부분을 뽑는다
    try:
        for result in predictions:
            top_x = result['topleft']['x']
            top_y = result['topleft']['y']
            btm_x = result['bottomright']['x']
            btm_y = result['bottomright']['y']

            confidence = result['confidence']
            # confidence는 클래스일 확률
            label = result['label'] + " " + str(round(confidence, 5))
            box_image = original_img
            if confidence > 0.3:
                box_image = original_img[top_y:btm_y, top_x:btm_x]
                yolo_box = yolo_box_info(original_img, top_x, top_y, btm_x, btm_y)
#                print(yolo_box)
                yolo_box_list.append(yolo_box)
    except:
        print("yolo predictions error !")
        pass
    # yolo가 못찾으면 그냥 default 이미지 리턴
    if len(yolo_box_list) == 0:
        print("empitied yolo_box_list !")
        # default_img = cv2.imread(default_img_path)
        # yolo_box = yolo_box_info(default_img, 0, 0, default_img.shape[1], default_img.shape[0])
        # yolo_box_list.append(yolo_box)
        return 0
    try:
        # yolo box를 기준으로 위아래 150으로 이미지를 뽑는다
        for yolo_box in yolo_box_list:
            cv_top_x = 0
            cv_btm_x = yolo_box.origin_img.shape[1]
            cv_top_y = max(yolo_box.top_y-150, 0)
            cv_btm_y = max(yolo_box.btm_y+150, yolo_box.origin_img.shape[1])
            # yolo box로 부터 위아래 200씩 준 이미지
            box_image = yolo_box.origin_img[cv_top_y:cv_btm_y, cv_top_x:cv_btm_x]
            cv_box = cv_box_info(yolo_box, box_image, cv_top_x, cv_top_y, cv_btm_x, cv_btm_y)
#             print(cv_box)
            cv_box_list.append(cv_box)
    except:
        print('opencv split error!')
        pass
    # box class를 담고있는 리스트를 리턴
    return cv_box_list


# 컨투어로 뽑은 영역과 YOLO 테이블의 영역의 intersection over union을 구하는 함수
def get_iou(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)

    boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
    boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)

    iou = interArea / float(boxAArea + boxBArea - interArea)

    return iou



# 컨투어 영역과 yolo테이블 비교해서 적합한 테이블 검출하는 함수
def find_table(cv_box_list):
    # 전체 검출되는 사이즈 테이블
    cnt_list = []

    if len(cv_box_list) == 0:
        print('failed detection')
    else :
        for cv_box in cv_box_list:
            try:
                # yolo box에서 위아래로 200씩 더한 이미지
                split_img = cv_box.return_box()
                draw_rect_img = split_img.copy()
                # 이미지에서의 yolo box
                yolo_box = cv_box.yolo_box.return_box()

                gray = cv2.cvtColor(split_img, cv2.COLOR_BGR2GRAY)
                blur = cv2.blur(gray, (5,5))
                canny_img = cv2.Canny(blur, 10,20)
                kernel = np.ones((20,20), np.uint8)
                morph_gray = cv2.morphologyEx(canny_img, cv2.MORPH_CLOSE, kernel)
                # 컨투어 인자 설정 링크 : https://datascienceschool.net/view-notebook/f9f8983941254a34bf0fee42c66c5539/
                # 모든 컨투어라인을 찾고 상하구조는 2단계, 그릴수있는 컨투어만 찾음
                contours, _ = cv2.findContours(morph_gray,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
                cnt_img = []
                cnt_idx = -1
                check_iou = []
                draw_img = yolo_box
                # 여기서 각 split된 이미지에 대해 contour를 뽑는데
                # 뽑게되는 좌표값이 split된 이미지에 대해 상대적인 값을 갖게된다
                # 때문에 절대적인 좌표, 즉 원본의 이미지에 대한 좌표값을 참조하기 위해서는
                # y좌표에 이전에 잘려나간 윗부분의 좌표값들을 더해주도록한다
                for i in range(0,len(contours)):
                    cnt = contours[i]
                    x,y,w,h = cv2.boundingRect(cnt)
                    # 전체 이미지의 1/4보다 크고 yolo사이즈표의 1/2보다 커야함
                    if w > split_img.shape[1]//4 and h > yolo_box.shape[0]//2:
                        # 오리지널 이미지에 대한 절대좌표 y를 가지고 옴
                        abs_y = y+cv_box.top_y
#                         print(x,abs_y,x+w,abs_y+h)

                        # contour 이미지를 list에 더함
                        # 클래스 형태로 저장(이미지, 절대 좌표y를 갖게)
                        cnt_img.append(cnt_img_info(split_img[y:y+h, x:x+w], abs_y, abs_y+h ))
                        cnt_idx += 1

                        draw_img = cv2.rectangle(draw_rect_img,(x,y),(x+w,y+h),(0,0,255),2)
                        # 위에서 언급한 절대적인 좌표가 필요한 이유는 yolo box와 contour box의 IOU를 구하기 위함
#                         print(cv_box.yolo_box)

                        # yolo box
                        boxA = [cv_box.yolo_box.top_x, cv_box.yolo_box.top_y, cv_box.yolo_box.btm_x, cv_box.yolo_box.btm_y]
                        # contour box
                        boxB = [x,abs_y,x+w,abs_y+h]
                        # top_x, top_y, btm_x, btm_y
                        box_iou = get_iou(boxA, boxB)
#                         print(f'box iou : {box_iou}')
                        if box_iou > 0.2:
                            check_iou.append(cnt_idx)
                # 만약에 0.1이상 일치하는 컨투어 없으면 그냥 split이미지 리턴
                if len(check_iou) == 0:
                    cnt_list.append(cnt_img_info(split_img, cv_box.top_y, cv_box.btm_y))
                # 0.1이상 일치하는 컨투어 있으면 그 중 가장 큰 것을 리턴
                else:
                    area_list = []
                    for idx in check_iou:
                        cnt_area = cnt_img[idx].img.shape[0]*cnt_img[idx].img.shape[1]
                        area_list.append(cnt_area)
#                         print(f'cnt_area : {cnt_img[idx].img.shape[0]*cnt_img[idx].img.shape[1]}')
                    max_idx = np.array(area_list).argmax()
                    cnt_list.append(cnt_img[check_iou[max_idx]])
            except:
                print('erorr!')
                continue
    return cnt_list



