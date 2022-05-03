from Drone_State_Machine import Drone_State, Alarm_State
from ArUco_Marker_Pose_Estimation import Tello_Pose_Estimation
from HTTP_Session import Session_Service
from Object_Detection import YOLO_object_detection as yolo
from SAURUSS_Node import Arduino_Sensor
from threading import Thread
from Autonomous_Driving import Drone_Object
import numpy as np
import threading
import time
""" This file is the core of the decisions of Tello drone.
    From here start the "reasoning" structure.
    It tell to the drone the entire procedure of the mission that it has to do.
"""

# Speed of the drone
V = 60

tello = Drone_Object.tello.tello
DEBUG_MODE = False


class MakeRotation(Thread):

    def __init__(self, x, y):
        Thread.__init__(self)

        self.x = x
        self.y = y
        self.h = 0

    def run(self):

        # do a rotation of 360 degrees while enabling second recognition
        if Drone_State.int_state == 1:  # if no person found
            self.h = 20
            tello.move_up(self.h)
            tello.rotate_counter_clockwise(360)

        tello.rotate_clockwise(180)
        tello.go_xyz_speed(self.x, self.y, -self.h, V)
        print("done")


def mission_tello(mac, user_name, password):

    time_to_start = 11  # sec
    print(mac)
    sensor = Arduino_Sensor.Arduino_Sensor(1)
    sensor.set_distances(user_name, password, mac)

    x, y = sensor.get_distances()

    yolo.init(mac)
    while True:
        try:
            tello.connect()
        except NameError:
            time.sleep(0.5)
            continue
        break

    tello.streamoff()
    tello.streamon()

    time.sleep(1)

    # change drone state
    Drone_State.running_YOLO()
    print(Drone_State.str_state)

    rotation = MakeRotation(x, y)
    # threads for the mission
    first_recognition = threading.Thread(target=yolo.area_recognition_mission.run)
    rotationThread = threading.Thread(target=rotation.run)
    second_recognition = threading.Thread(target=yolo.area_recognition_RTH.run)

    # start recognition thread
    first_recognition.start()

    if not DEBUG_MODE:
        tello.takeoff()
        tello.go_xyz_speed(x, y, 0, V)

    distance_to_fly = np.sqrt(x ** 2 + y ** 2)

    print(str((tello.get_flight_time() - time_to_start) * V) + "<=" + str(distance_to_fly))
    while (tello.get_flight_time() - time_to_start) * V <= distance_to_fly:  # if im not arrived yet
        # if a person is found
        if Drone_State.int_state == 3:
            break

    if Drone_State.int_state == 1:
        Drone_State.no_person()
    # this because the others movements cant be done if the current movement is enable
    if first_recognition.is_alive():
        first_recognition.join()

    print(str((tello.get_flight_time() - time_to_start) * V) + ">=" + str(distance_to_fly))
    time_of_rotation = 0  # sec

    if not Alarm_State.alarm_state:  # no person found yet
        Drone_State.running_ArUco_PE()

        print(Drone_State.str_state)

        # START ARUCO MARKER POSE ESTIMATION
        Tello_Pose_Estimation.ArUco_Pose_Estimation()

        # Now Tello is posed so he has to do another recognition
        Drone_State.running_YOLO()

        second_recognition.start()

        time_of_rotation = 7  # sec

    print("Make Rotation")
    rotationThread.start()

    time_of_return_to_home = tello.get_flight_time()

    print(str((tello.get_flight_time() - time_of_return_to_home - time_of_rotation) * V) + "<=" + str(distance_to_fly))
    # while i'm not arrived to home
    while (tello.get_flight_time() - time_of_return_to_home - time_of_rotation) * V <= distance_to_fly:
        # if a person is found
        if Drone_State.int_state == 3:
            break
    Drone_State.no_person()
    print(str((tello.get_flight_time() - time_of_return_to_home - time_of_rotation) * V) + ">=" + str(distance_to_fly))

    if second_recognition.isAlive():
        second_recognition.join()

    if Drone_State.str_state == 0:
        # can conclude there's no persons in the area
        print("FALSE ALARM!")

    if rotationThread.isAlive():
        rotationThread.join()

    Drone_State.running_ArUco_PE()
    print(Drone_State.str_state)

    # START ARUCO MARKER POSE ESTIMATION FOR SAFE RTH AND LAND
    Tello_Pose_Estimation.ArUco_Pose_Estimation()
    if Session_Service.doLogout() == 200:
        print("logout")
    if not DEBUG_MODE:
        tello.rotate_clockwise(180)
        tello.land()
    tello.streamoff()
    print("Adios!")

