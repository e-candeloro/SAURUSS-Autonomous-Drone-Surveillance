from threading import Thread
from HTTP_Session import Session_Service
from Drone_State_Machine import Drone_State, Alarm_State
from Autonomous_Driving import Drone_Object

import numpy as np
import datetime
import time
import json
import cv2
import os

""" In this file is implemented the convolutional neural network used for understand if a person it's nearby.
    For the net I used YOLO v3 in the tiny mode (this is because it's the limit of the technologies in my possession)
    But it works well.
"""


tello = Drone_Object.tello.tello

area_recognition_mission = None
area_recognition_RTH = None

confidenceThreshold = 0.4
nmsThreshold = 0.3

classesFile = 'coco.names'


def init(MAC):
    global area_recognition_mission
    global area_recognition_RTH
    dir = '../Object_Detection/'
    with open(dir + classesFile, 'rt') as f:
        classNames = f.read().rstrip('\n').split('\n')

    modelConfiguration = dir + 'yolov3-tiny.cfg'
    modelWeights = dir + 'yolov3-tiny.weights'

    net = cv2.dnn.readNetFromDarknet(modelConfiguration, modelWeights)
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

    area_recognition_mission = Recognition(classNames, net, MAC)
    area_recognition_RTH = Recognition(classNames, net, MAC)


class Recognition(Thread):

    def __init__(self, class_names, net, sensor_id):

        Thread.__init__(self)
        self.class_names = class_names
        self.net = net
        self.id = sensor_id

    def run(self):
        print("Scanning area...")
        frame_read = tello.get_frame_read()

        while Drone_State.int_state == 1:  # YOLO STATE

            frame = frame_read.frame
            text = "Battery: {}%".format(tello.get_battery())
            cv2.putText(frame, text, (5, 720 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            img = cv2.resize(frame, (640, 480))

            blob = cv2.dnn.blobFromImage(img, 1 / 255, (640, 480), [0, 0, 0], 1, crop=False)
            self.net.setInput(blob)

            layerNames = self.net.getLayerNames()
            outputNames = [layerNames[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
            # array of probability for each object
            outputs = self.net.forward(outputNames)

            self.findObject(outputs, img, self.id)

            ################################################################
            cv2.imshow('Tello detection...', img)

            # this is for safe debug mode
            if cv2.waitKey(1) == ord('q'):
                tello.land()
                tello.streamoff()
                break
        # Call it always before finishing. To deallocate resources.

        if Drone_State.int_state == 3:
            Alarm_State.enable_alarm()
            sendProof(self.id)

    def findObject(self, outputs, img, sensor_id):
        hT, wT, cT = img.shape
        bbox = []
        confs = []
        classIds = []

        for output in outputs:
            for det in output:
                scores = det[5:]
                classId = np.argmax(scores)
                confidence = scores[classId]
                if confidence > confidenceThreshold:
                    w, h = int(det[2] * wT), int(det[3] * hT)
                    x, y = int((det[0] * wT) - w / 2), int((det[1] * hT) - h / 2)
                    bbox.append([x, y, w, h])
                    classIds.append(classId)
                    confs.append(float(confidence))

        indeces = cv2.dnn.NMSBoxes(bbox, confs, confidenceThreshold, nmsThreshold)

        for i in indeces:
            if Drone_State.int_state != 3:
                i = i[0]
                box = bbox[i]
                x, y, w, h = box[0], box[1], box[2], box[3]
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 255), 2)
                cv2.putText(img, f'{self.class_names[classIds[i]].upper()} {int(confs[i] * 100)}%',
                            (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)

                for j in classIds:
                    if j == 0:  # person

                        for k in range(0, 2):
                            Session_Service.sendAlarmBySensorID(sensor_id)

                        cv2.putText(img, f'{self.class_names[j].upper()} {int(confs[i] * 100)}%',
                                    (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

                        print("WARNING! PERSON DETECTED!")
                        cv2.imwrite("picture.png", img)
                        timer = time.perf_counter()
                        video = cv2.VideoWriter('video.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 30, (640, 480))
                        frame_read = tello.get_frame_read()
                        while time.perf_counter() - timer < 3:
                            image = cv2.resize(frame_read.frame, (640, 480))
                            video.write(image)
                            time.sleep(1 / 30)

                        print("Semaphore unlocked")

                        video.release()
                        Drone_State.person_found()
                        break


def sendProof(sensor_id):
    result_set = json.loads(Session_Service.getTimestampsOfAlarms(sensor_id))["Timestamps"]

    timestamp_img = str(result_set[0]["timestamp"].split(" ")[1].replace(":", ""))
    timestamp_vid = str(result_set[1]["timestamp"].split(" ")[1].replace(":", ""))

    os.rename("video.mp4", f"{timestamp_vid}.mp4")
    os.rename("picture.png", f"{timestamp_img}.png")

    today = datetime.datetime.now().strftime("%d%m%y")

    # send a image as proof
    image_proof = open(f"{timestamp_img}.png", "rb")
    Session_Service.uploadMediaFile(sensor_id, today, image_proof)
    image_proof.close()

    # send a video as proof
    recorded_proof = open(f"{timestamp_vid}.mp4", "rb")
    Session_Service.uploadMediaFile(sensor_id, today, recorded_proof)
    recorded_proof.close()
