# import per utilities e comunicazioni seriali
from Autonomous_Driving import Mission_Thread
from Bridge_Comm import Telegram_Bot
from Telegram_Bot import Bot
import logging
from subprocess import *
import subprocess
import os
import fcntl
from threading import Thread
import threading
import json
import requests
import serial.tools.list_ports
import serial
import time

# import per comandi shell

# import per bot telegram

# from Autonomous_Driving import Mission_Thread

BOTKEY = ''  # removed for security
chatID = 000  # removed for security


user_name = None  # variabile per username per la configurazione dei mac address
password = None  # variabile per password per la configurazione dei mac address

server = '' #removed for security 
test_dict = {}

# dizionario con chiave id sensore e valore MAC address del sensore,
# ricevuto dal telegram bot dopo il setup del posizionamento dei sensori

mac_config = None
sensor_dict = {}
# dizionario per salvare id sensore, MAC address sensori, nome porta seriale, oggetto porta (utilizzato dalla libreria serial)


"""
VARIABILI PER MACCHINA A STATI FINITI
"""

"""
MAPPING DEGLI STATI

-WAIT: il bridge aspetta la lista di MAC address dal telegram bot
-CONFIG: il bridge cerca la lista dei MAC address tramite BT e configura le connessioni seriali con tutti i sensori
-OFF: il bridge rimane collegato ad i sensori aspettando un segnale di ON da telegram. I sensori in questo stato sono spenti
-ON: il bridge accende i sensori e rimane in ascolto per eventuali segnalazioni da parte dei sensori
-ALERT: se il bridge riceve un alert attiva il drone ed inizia un timer di cooldown. Successivamente ritorna allo stato SENSE MODE

"""

wait = "WAIT"
config = "CONFIG"
off = "OFF"
sense_mode = "ON"
alert = "ALERT"
setup_ok = "SETOK"

Input_Symb = wait

Default_State = wait
Present_State = Default_State
Future_State = None


def Get_MAC_list(user_name, password):
    address_list = []

    if user_name is None or password is None:
        return None

    S = requests.Session()

    post = S.post(server +
                  str(user_name) + "/" + str(password))
    if (post.status_code == requests.codes.ok):
        result = S.get(server)
        result = json.loads(result.text)["Sensors"]

        for data in result:
            mac = data["sensor_id"]
            if len(mac) > 15 and ":" in mac:
                address_list.append(mac)
        print(address_list)

        for i, mac in enumerate(address_list):
            test_dict[i] = mac

        print(test_dict)
        return True
    else:
        print("Error connecting to Server: Code Response" + str(post.status_code))
        return False


def non_block_read(output):
    fd = output.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
    try:
        return output.read()
    except:
        return ""


def Setup_BT_connections(mac_dict):
    print("Trying to setup BT connection for devices:")

    stop_hc0 = subprocess.run(['sudo', 'hciconfig', 'hci0', 'down'],
                              capture_output=True)
    print("Turning off rfcomm host...")
    time.sleep(5)

    print("Turning back on rfcomm host...")
    start_hc0 = subprocess.run(['sudo', 'hciconfig', 'hci0', 'up'],
                               capture_output=True)
    time.sleep(5)
    print("Releasing rfcomm past connections...")
    # resest delle connessioni rfcomm
    for i, mac in mac_dict.items():
        proc_rel = subprocess.run(['sudo', 'rfcomm', 'release', str(i)],
                                  capture_output=True)
    time.sleep(0.5)

    # scan dei dispositivi bluetooth finchè tutti i sensori sulla
    # lista sono trovati
    sensor_num_found: int = 0
    while sensor_num_found < len(mac_dict):

        sensor_num_found = 0
        time.sleep(1)
        # scan dei dispositivi bluetooth
        print("Scanning BT devices...")
        proc_scan = subprocess.run(['hcitool', 'scan'],
                                   stdout=subprocess.PIPE)
        # print(proc_scan.stdout.decode('utf-8'))
        line = (proc_scan.stdout.decode('utf-8')).split('\n')
        line.pop(0)

        for devices in line:
            print(devices)
            if "hc-05" in devices.lower() or "oneplus" in devices.lower():
                sensor_num_found += 1
                print("found " + str(sensor_num_found) + " valid sensors")

    # creazione delle porte rfcomm per i vari sensori nella lista mac
    for i, mac in mac_dict.items():

        sb = Popen("sudo rfcomm connect " + str(i) + " " +
                   str(mac) + " " + str(1), shell=True, stdout=PIPE)
        time.sleep(2)
        sb.kill()
        sb.poll()
        non_block_read(sb.stdout)

        time.sleep(2)

        # controllo di avvenuta creazione con successo della connessione
        proc = subprocess.run(['sudo', 'rfcomm', '-a'],
                              capture_output=True, shell=False)

        time.sleep(2)

        if str(mac) in (proc.stdout.decode('utf-8')):
            print("Enstablished connection with sensor " + str(i))
        else:
            print(proc.stderr.decode('utf-8'))
            print("Something went wrong connecting to sensor: " + str(i))
            print("Restarting connection process for all sensors...")
            Setup_BT_connections(mac_dict)

    return mac_dict


def Setup_Serials():  # open serial port

    global sensor_dict
    global test_dict

    valid_ports = []

    try:
        sensor_dict.clear()
    except:
        pass

    print("list of avaialable ports: ")
    ports = serial.tools.list_ports.comports(include_links=True)
    print(ports)

    for port in ports:
        if "dev/rfcomm" in port.device:
            valid_ports.append(port)

    valid_ports.sort()

    if len(valid_ports) == len(test_dict.keys()):
        print("Found all sensor ports!")
    else:
        print("ERROR: can't find all sensors!")
        return False

    for id, port in enumerate(valid_ports):

        if str(id) in port.device.lower():
            print("connecting to sensor: " +
                  str(id) + " with port: " + str(port.device))
            try:
                sensor_serial = serial.Serial(
                    port.device, 9600, timeout=0)
                sensor_dict[id] = [test_dict[id], port.device, sensor_serial]
                print(sensor_dict[id])
                time.sleep(1)
            except:
                print("FAILED TO CONNECT WITH PORT: " + str(port.device))
                time.sleep(4)
                return False

    print("Success!")
    print("Serial connections enstablished for " +
          str(len(sensor_dict.keys())) + " sensors")
    # print(sensor_dict)
    return True


def Bridge_Config():
    # if Setup_BT_connections(test_dict):
    #    print("Successfully connected to all sensors!")
    #    print(test_dict)
    if (Setup_Serials()):
        print(sensor_dict)
        return True
    else:
        print("There was an error")
        return False


def Update_State():
    global Present_State
    global Future_State
    global Input_Symb

    if (Present_State == wait):
        if (Input_Symb == config):
            Future_State = config
            print("START BRIDGE CONFIG...")
            return
        else:
            Future_State = wait
            return

    elif (Present_State == config):
        if (Input_Symb == setup_ok):
            Future_State = off
            print("BRIDGE NOW IN IDLE...")
            return
        else:
            Future_State = config
            return

    elif (Present_State == off):
        if (Input_Symb == sense_mode):
            print("TURNING ON SENSORS...")
            Future_State = sense_mode
            return
        else:
            Future_State = off
            return

    elif (Present_State == sense_mode):
        if (Input_Symb == alert):
            print("ALERT RECEIVED!")
            Future_State = alert
            return
        elif (Input_Symb == off):
            Future_State = off
            print("TURNING OFF SENSORS...")
            return
        else:
            Future_State = sense_mode
            return
    elif (Present_State == alert):
        if (Input_Symb == sense_mode):
            print("RETURNING TO SENSING AFTER COOLDOWN...")
            Future_State = sense_mode
            return
        else:
            Future_State = alert
            return
    else:
        pass


def On_Enter_Actions():
    global Present_State
    global Future_State

    if (Present_State == sense_mode and Future_State == off):

        if BR.Set_Sensors_OFF():
            print("Turned OFF sensors")
            return
        else:
            print("Error turning OFF sensors")
            return

    elif (Present_State == off and Future_State == sense_mode):

        if BR.Set_Sensors_ON():
            print("Turned ON sensors")
            miobot.send_bot_message("Sensori Accesi!")
            return
        else:
            print("Error turning OFF sensors")
            miobot.send_bot_message(
                "Errore di accensione dei sensori...\nRiprovare")
            return
    else:
        return


def Update_Output():
    global Present_State
    global Future_State
    global Input_Symb
    global user_name
    global password
    global miobot

    if (Present_State == wait):
        pass

    elif (Present_State == config):
        if Get_MAC_list(user_name, password) is not None:
            if Bridge_Config():
                Input_Symb = setup_ok
                return
            else:
                print("ERROR IN BRIDGE SETUP: TIME EXPIRED")
                return
        else:
            print("Server connection Error!!!")
            return

    elif (Present_State == sense_mode):
        (id_returned, MAC_returned) = BR.Listen_for_Alert()
        print("Id_returned: " + str(id_returned))
        print("Mac_returned: " + str(MAC_returned))
        if (MAC_returned is not None and id_returned is not None):
            print("Sending Telegram Message and activating Drone!!!")
            print("Username: " + str(user_name))
            print("Password: " + str(password))
            miobot.send_alert_message(id_returned)
            Mission_Thread.mission_tello(MAC_returned, user_name, password)
            Input_Symb = alert
            return

    elif (Present_State == alert):
        Input_Symb = sense_mode
        return
        # passa subito al sense una volta terminato lo script di Tello


class Bridge:

    def __init__(self):
        self.header = b'\xff'
        self.footer = b'\xfe'
        self.ack = b'\x01'
        self.off_sensor = b'\xaa'
        self.alert = b'\x02'
        self.packet_len = 4
        self.ack_pakcet = b'\xff\x01\xfe'

    def Sensor_ON(self, sens_id, sensor_info):

        sensor_port = sensor_info[-1]
        sensor_port.reset_output_buffer()
        print("Sending ON signal to sensor: " + str(sens_id))

        bsens_id = sens_id.to_bytes(1, byteorder='little')
        data = (self.header + bsens_id + self.footer)

        while (True):

            sensor_port.write(data)
            time.sleep(2)

            (received_id, payload) = self.ReadPacket(sensor_port)

            if received_id == sens_id:
                print("Turned ON sensor: " + str(sens_id))
                return True

    def Sensor_OFF(self, sens_id, sensor_info):

        sensor_port = sensor_info[-1]
        sensor_port.reset_output_buffer()

        print("Sending OFF signal to sensor: " + str(sens_id))

        data = (self.header + self.off_sensor + self.footer)

        while (True):

            sensor_port.write(data)
            time.sleep(2)

            (received_id, payload) = self.ReadPacket(sensor_port)

            if received_id == sens_id:
                print("Turned OFF sensor: " + str(sens_id))
                return True

    def Set_Sensors_ON(self):

        # for sens_id, sensor_info in sensor_dict.items():
        # sensor_port = sensor_info[-1]
        # sensor_port.reset_input_buffer()

        for sens_id, sensor_info in sensor_dict.items():
            print(sens_id)
            print(sensor_info)

            if self.Sensor_ON(sens_id, sensor_info):
                time.sleep(5)
            else:
                print("There was an error turning on sensor " + str(sens_id))
                return False

        return True

    def Set_Sensors_OFF(self):

        for sens_id, sensor_info in sensor_dict.items():
            sensor_port = sensor_info[-1]
            sensor_port.reset_input_buffer()

        for sens_id, sensor_info in sensor_dict.items():
            if self.Sensor_OFF(sens_id, sensor_info):
                pass
            else:
                print("There was an error turning off sensor " + str(sens_id))
                return False

        return True

    def useData(self, buffer):
        # I have received a line from the serial port. I can use it
        if len(buffer) < (self.packet_len):  # at least header, size, footer
            return (-1, -1)
        # split parts
        if buffer[0] != self.header:  # se il pacchetto contiene solo il footer, lo scarto!
            return (-1, -1)

        # converto il byte in un int nella parte del pacchetto che mi dice il payload
        sensor_id = int.from_bytes(buffer[1], byteorder='little')
        # converto in byte il payload partendo dalla posizione 2
        payload = int.from_bytes(buffer[2], byteorder='little')
        print("sensor_id = " + str(sensor_id))
        print("payload = " + str(payload))

        return (sensor_id, payload)

    def ReadPacket(self, sensor_ser):

        # ritorna

        Sensor_ID = -1
        payload = -1
        timer = time.perf_counter()
        new_data = False
        receiving = False
        buffer = []

        timer = time.perf_counter()

        while (time.perf_counter() - timer <= 1):

            if sensor_ser.in_waiting > 0:
                # data available from the serial port
                lastchar = sensor_ser.read(1)  # legge un byte dalla porta

                # EOL (???) se ricevo il footer allora faccio il processing dei pacchetti
                if lastchar == self.footer:
                    buffer.append(lastchar)
                    print("\nValue received")
                    Sensor_ID, payload = self.useData(
                        buffer)  # chiama il metodo useData
                    print(buffer)
                    buffer = []  # svuota buffer+
                    break

                else:
                    # aggiungi alla lista l'ultimo byte
                    buffer.append(lastchar)

        if payload == 2:
            print("MANDO ACK!!!!!!!!!!")
            sensor_ser.write(self.ack_pakcet)
            time.sleep(0.1)
            sensor_ser.write(self.ack_pakcet)
            time.sleep(0.1)
            sensor_ser.write(self.ack_pakcet)
            time.sleep(0.1)

        return (Sensor_ID, payload)

    def Listen_for_Alert(self):
        id_alert = None
        Mac_alert = None
        alert = False
        timer = time.perf_counter()
        alert_payload = 2

        for sensor_id, sensor_info in sensor_dict.items():
            sens_port = sensor_info[-1]
            MAC = sensor_info[0]

            id_received = None
            payload = None
            print("Reading sensor with MAC: " + str(MAC))
            print(sens_port)

            (id_received, payload) = self.ReadPacket(sens_port)

            if (id_received == -1 and payload == -1):
                print("Nothing interesting to read")

            if payload == alert_payload:
                alert = True
                Mac_alert = MAC
                id_alert = id_received

        if alert:
            print("Received Alert!")
            print("Activating Drone!")
            return id_alert, Mac_alert

        else:
            return (None, None)


if __name__ == '__main__':

    # Inizializza con un thread lo script bot telegram
    # Questo script invia i messaggi all'utente in caso di alarme
    # e/o modifica gli input symbol per la macchina a stati finiti
    miobot = Telegram_Bot.Bot()
    new_bot = threading.Thread(target=miobot.run)
    new_bot.start()

    BR = Bridge()  # inizializza l'oggetto bridge

    while (True):  # ciclo infinito per la macchina a stati finiti

        print("---------------------------------------------")

        Update_State()
        On_Enter_Actions()
        Present_State = Future_State
        Update_Output()
        time.sleep(0.2)
