from djitellopy import Tello
import cv2
from subprocess import check_output
import subprocess


# this is for automatic connection but in windows.
# in this case we can say that the connection is alive forever
def connection():
    results = subprocess.check_output(["netsh", "wlan", "show", "network"])

    results = results.decode("ascii") # needed in python 3
    results = results.replace("\r","")
    ls = results.split("\n")
    ls = ls[4:]
    ssids = []
    x = 0

    while x < len(ls):
        if x % 5 == 0:
            ssids.append(ls[x].split(": ")[1:])
        x += 1
    ssids = [name for ssid in ssids for name in ssid]
    if ssids.__contains__("O-TELLO"):
        if check_output("netsh wlan connect name=O-TELLO", shell=True).decode() == "Richiesta di connessione completata.\r\n" :
            print("Connessione a Tello stabilita")
        else:
            print("Impossibile stabilire connessione")
    else:
        print("Tello non attivo")

"""

def initializeTello():
    myDrone = Tello()
    myDrone.connect()
    myDrone.for_back_velocity = 0
    myDrone.left_right_velocity = 0
    myDrone.up_down_velocity = 0
    myDrone.yaw_velocity = 0
    myDrone.speed = 0
    print(myDrone.get_battery())
    myDrone.streamoff()
    myDrone.streamon()
    return myDrone

def telloGetFrame(myDrone, w=1280, h=720):
    myFrame = myDrone.get_frame_read()
    myFrame = myFrame.frame
    img = cv2.resize(myFrame, (w,h))
    return img

def keyPad(tello,x):


    while True:

        key = cv2.waitKey(1) & 0xff

        if key == 27:  # ESC
            break
        elif key == ord('w'):
            tello.move_forward(30)
        elif key == ord('s'):
            tello.move_back(30)
        elif key == ord('a'):
            tello.move_left(30)
        elif key == ord('d'):
            tello.move_right(30)
        elif key == ord('e'):
            tello.rotate_clockwise(30)
        elif key == ord('q'):
            tello.rotate_counter_clockwise(30)
        elif key == ord('r'):
            tello.move_up(30)
        elif key == ord('f'):
            tello.move_down(30)

    tello.land()"""