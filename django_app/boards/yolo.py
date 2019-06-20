## path 바꾸기 -> 한번만 실행
import os
import numpy as np
from darkflow.net.build import TFNet
import cv2
#
# print(os.getcwd())  # 현재 디렉토리
# darkflow_path = os.path.join(os.getcwd(), '../darkflow-slave')
# # 디렉토리를 darkflow 안으로 바꿔줌
# os.chdir(darkflow_path)
# print(os.getcwd())  # 변경된 디렉토리

# model은 사용하는 cfg model
options = {"model": "cfg/size-yolo.cfg",
           "load": 22000}  # 최신 checkpoint를 load하려면 -1

tfnet = TFNet(options)

tfnet.load_from_ckpt()
