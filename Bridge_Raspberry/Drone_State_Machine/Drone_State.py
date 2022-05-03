""" This State machine is used for the reasoning of the drone.
"""
str_state = "IDLE"
int_state = 0


def no_person():
    global str_state
    global int_state

    str_state = "No Person Found Yet"
    int_state = 0


def running_YOLO():
    global str_state
    global int_state

    str_state = "YOLO"
    int_state = 1


def running_ArUco_PE():
    global str_state
    global int_state

    str_state = "ArUco Pose Estimation"
    int_state = 2


def person_found():
    global str_state
    global int_state

    str_state = "Person Already Found"
    int_state = 3

