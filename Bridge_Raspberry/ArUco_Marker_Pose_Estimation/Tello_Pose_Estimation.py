from Drone_State_Machine import Drone_State
from Autonomous_Driving import Drone_Object
import cv2.aruco as aruco
import numpy as np
import cv2
import time
import math
import sys

marker_size = 9  # [cm]

""" This file is the core of the 3D project.
    For the 3D pose estimation indeed is very useful the concept of the pinhole camera.
    When an ArUco marker is recognized, first of all we need to roto-translate our reference system 
    (from the camera) with respect to that of the marker and vice versa.
    After that we can estimate also the roll,pitch,yaw with the Euler Angles and the Euler-Rodrigues 3D rotation.
    NB:
    For use this code i need first to calibrate the tello camera to know the intrinsic parameters of the camera
    used for calculate the Distance = (focal length)*(ArUco width)/(pixel size) for example.
"""


# Checks if a matrix is a valid rotation matrix.
def isRotationMatrix(R):
    Rt = np.transpose(R)
    shouldBeIdentity = np.dot(Rt, R)
    I = np.identity(3, dtype=R.dtype)
    n = np.linalg.norm(I - shouldBeIdentity)
    return n < 1e-6


# Calculates rotation matrix to euler angles
# The result is the same as MATLAB except the order
# of the euler angles ( x and z are swapped ).
def rotationMatrixToEulerAngles(R):
    assert (isRotationMatrix(R))

    sy = math.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])

    singular = sy < 1e-6

    if not singular:
        x = math.atan2(R[2, 1], R[2, 2])
        y = math.atan2(-R[2, 0], sy)
        z = math.atan2(R[1, 0], R[0, 0])
    else:
        x = math.atan2(-R[1, 2], R[1, 1])
        y = math.atan2(-R[2, 0], sy)
        z = 0

    return np.array([x, y, z])


# Draws HUD on the screen
def Draw(frame, Distance, angle, Center):
    cv2.putText(frame, ('Distance %d' % Distance), (400, 45), cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255),
                2, cv2.LINE_AA)
    cv2.circle(frame, (int(Center[0]), int(Center[1])), 2, (255, 0, 0), thickness=1)

    cv2.putText(frame, ('Orientation %d' % angle), (400, 60), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 0),
                2,
                cv2.LINE_AA)
    cv2.putText(frame, ('Center %d,%d' % Center), (400, 15), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 0), 2,
                cv2.LINE_AA)

    return


# With this function I can obtain the spatial coordinates of the drone camera
def ArUco_Pose_Estimation():
    drone = Drone_Object.tello
    frame_read = drone.tello.get_frame_read()

    # --- Get the camera calibration path
    path = '../ArUco_Marker_Pose_Estimation/'
    camera_matrix = np.loadtxt(path + 'cameraMatrix.txt', delimiter=',')
    camera_distortion = np.loadtxt(path + 'cameraDistortion.txt', delimiter=',')

    # --- 180 deg rotation matrix around the x axis
    R_flip = np.zeros((3, 3), dtype=np.float32)
    R_flip[0, 0] = 1.0
    R_flip[1, 1] = -1.0
    R_flip[2, 2] = -1.0

    # --- Define the aruco dictionary
    aruco_dict = aruco.Dictionary_get(aruco.DICT_ARUCO_ORIGINAL)
    parameters = aruco.DetectorParameters_create()

    # -- Font for the text in the image
    font = cv2.FONT_HERSHEY_PLAIN
    timer = time.perf_counter()
    # run for 10 seconds
    while time.perf_counter() - timer <= 10:

        # -- Read the camera frame
        frame = frame_read.frame
        frame = cv2.resize(frame, (640, 480))
        # -- Convert in gray scale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # -- remember, OpenCV stores color images in Blue, Green, Red

        # -- Find all the aruco markers in the image
        corners, ids, rejected = aruco.detectMarkers(image=gray, dictionary=aruco_dict, parameters=parameters,
                                                     cameraMatrix=camera_matrix, distCoeff=camera_distortion)

        if ids is not None:  # when the drone detect something
            # -- ret = [rvec, tvec, ?]
            # -- array of rotation and position of each marker in camera frame
            # -- rvec = [[rvec_1], [rvec_2], ...]    attitude of the marker respect to camera frame
            # -- tvec = [[tvec_1], [tvec_2], ...]    position of the marker in camera frame
            print(corners)
            ret = aruco.estimatePoseSingleMarkers(corners, marker_size, camera_matrix, camera_distortion)

            # -- Unpack the output, get only the first
            rvec, tvec = ret[0][0, 0, :], ret[1][0, 0, :]

            # -- Draw the detected marker and put a reference frame over it
            aruco.drawDetectedMarkers(frame, corners)
            aruco.drawAxis(frame, camera_matrix, camera_distortion, rvec, tvec, 10)

            # -- Print the tag position in camera frame
            str_position = "MARKER Position x=%4.0f  y=%4.0f  z=%4.0f" % (tvec[0], tvec[1], tvec[2])
            cv2.putText(frame, str_position, (0, 40), font, 1, (0, 255, 0), 2, cv2.LINE_AA)

            # -- Obtain the rotation matrix tag->camera from Rodrigues formula
            R_ct = np.matrix(cv2.Rodrigues(rvec)[0])
            R_tc = R_ct.T

            # -- Get the attitude in terms of euler 321 (Needs to be flipped first)
            roll_marker, pitch_marker, yaw_marker = rotationMatrixToEulerAngles(R_flip * R_tc)

            # -- Print the marker's attitude respect to camera frame
            str_attitude = "MARKER Attitude r=%4.0f  p=%4.0f  y=%4.0f" % (
                math.degrees(roll_marker), math.degrees(pitch_marker),
                math.degrees(yaw_marker))
            cv2.putText(frame, str_attitude, (0, 20), font, 1, (0, 255, 0), 2, cv2.LINE_AA)

            # -- Now get Position and attitude f the camera respect to the marker
            pos_camera = -R_tc * np.matrix(tvec).T

            str_position = "CAMERA Position x=%4.0f  y=%4.0f  z=%4.0f" % (pos_camera[0], pos_camera[1], pos_camera[2])
            cv2.putText(frame, str_position, (0, 80), font, 1, (0, 255, 0), 2, cv2.LINE_AA)

            # -- Get the attitude of the camera respect to the frame
            roll_camera, pitch_camera, yaw_camera = rotationMatrixToEulerAngles(R_flip * R_tc)
            str_attitude = "CAMERA Attitude r=%4.0f  p=%4.0f  y=%4.0f" % (
                math.degrees(roll_camera), math.degrees(pitch_camera),
                math.degrees(yaw_camera))

            cv2.putText(frame, str_attitude, (0, 60), font, 1, (0, 255, 0), 2, cv2.LINE_AA)

            # Calculated data from orientation and position vectors
            Distance = tvec[2]
            Angle = math.degrees(yaw_marker)
            coordinates = tuple(corners[0])
            centerY = int((coordinates[0][0][1] + coordinates[0][2][1]) / 2)
            centerX = int((coordinates[0][0][0] + coordinates[0][2][0]) / 2)
            Center = (centerX, centerY)
            Tilt = math.degrees(pitch_marker) / 400 + 1
            drone.set_parameter(Center[0], Center[1], Distance, Tilt)
            drone.action()

            Draw(frame, Distance, Angle, Center)
        # --- Display the frame
        cv2.putText(frame, str(Drone_State.str_state), (600, 90), font, 1, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.imshow('frame', frame)

        # --- use 'q' to quit
        key = cv2.waitKey(1) & 0xFF
        if key == ord('l'):
            time.sleep(1)
            drone.tello.land()

        if key == ord('q'):
            cv2.destroyAllWindows()
            sys.exit()
