from Drone_State_Machine import Drone_State
from djitellopy import Tello
import time


# This class is for the movements of Tello when the ArUco pose estimation is running

class DroneObject:

    # initialize the object
    # Set default state to IdleState() (no person)
    # Create Tello object from the API
    # set default values for coordinate, FPS, distance, and tilt
    def __init__(self):
        self.state = Drone_State.no_person()
        self.tello = Tello()
        self.coordinate = (0, 0)
        self.FPS = 30
        self.distance = 30  # pre defined, to be changed later
        self.tilt = 0

    # setter for member variables
    def set_parameter(self, x, y, dist, tilt):
        self.coordinate = (x, y)
        self.distance = dist
        self.tilt = tilt

    # for tracking the drone, called when the drone is tracking aruco markers
    # when tilt is active, it will prioritize the turning motion over the other motions
    # controls shifting, moving up and down, forward backwards, and turning
    def track(self):
        if self.tilt <= 0.95 and self.tilt != 0:
            self.tello.rotate_clockwise(int((1 - self.tilt) * 100))
            time.sleep(0.05)
        elif self.tilt >= 1.05:
            self.tello.rotate_counter_clockwise(int((self.tilt - 1) * 100))
            time.sleep(0.05)
        else:
            if self.distance > 50:
                forward = int((self.distance - 50))
                if forward < 20:
                    self.tello.move_forward(20)
                else:
                    self.tello.move_forward(forward)
                time.sleep(0.05)
            elif self.distance < 40:
                backward = int(abs(self.distance - 40))
                if backward < 20:
                    self.tello.move_back(20)
                else:
                    self.tello.move_back(backward)
                time.sleep(0.05)

            if 266 > self.coordinate[0] >= 0:
                self.tello.move_left(20)
                time.sleep(0.05)

            elif 639 > self.coordinate[0] >= 372:
                self.tello.move_right(20)
                time.sleep(0.05)

            if 0 < self.coordinate[1] <= 133:
                self.tello.move_up(20)
                time.sleep(0.05)

            elif 346 <= self.coordinate[1] < 479:
                self.tello.move_down(20)
                time.sleep(0.05)

    def action(self):
        self.track()


# public instance
tello = DroneObject()
