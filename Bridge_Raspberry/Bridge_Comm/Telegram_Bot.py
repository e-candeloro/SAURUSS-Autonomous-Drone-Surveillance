from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import Update
from threading import Thread
import threading
import logging
import json
import requests


class Bot(Thread):

    def __init__(self):

        Thread.__init__(self)
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        self.updater = None

    def ON_Command(self, update, context):
        global Input_Symb
        global sense_mode
        """Send a message when the command /start is issued."""
        update.message.reply_text('Setting Sensors ON')
        print("\n\n\n\n\n\nON Message Received!")
        Input_Symb = sense_mode  # Cambia il simbolo di input della FSM ad "ON"

    """def CONFIG_Command(self, update, context):
        # Send a message when the command / start is issued.
        update.message.reply_text('Starting system setup...')
        # Cambia il simbolo di input della FSM a "CONFIG"
        Serial_setup.Input_Symb = "CONFIG
        """

    def OFF_Command(self, update, context):
        global Input_Symb
        global off
        """Send a message when the command /help is issued."""
        update.message.reply_text('Shutting Sensors OFF')
        print("\n\n\n\n\n\nOFF Message Received!")
        Input_Symb = off  # Cambia il simbolo di input della FSM ad "OFF"

    def send_alert_message(self, sensor_id):
        global chatID
        global BOTKEY

        send_text = 'https://api.telegram.org/bot' + BOTKEY + '/sendMessage?chat_id=' + str(chatID) \
                    + '&parse_mode=Markdown&text=' + \
                    "Warning, drone activated!\nSensor: " + str(sensor_id)

        response = requests.get(send_text)

        return response.json()

    def send_bot_message(self, message):
        global chatID
        global BOTKEY

        send_text = 'https://api.telegram.org/bot' + BOTKEY + '/sendMessage?chat_id=' + str(chatID) \
                    + '&parse_mode=Markdown&text=' + str(message)

        response = requests.get(send_text)

        return response.json()

    def get_new_message(self, update, context):

        global config
        global user_name
        global password
        global Input_Symb

        string = update.message.text.split(" ")
        print(f"il bot mi ha letto il messaggio: {string}")

        if (len(string) == 3 and string[0] == config):
            Input_Symb = config
            user_name = string[1]
            password = string[2]
            sendmessage = "Ricevuto!\nSto tentando di autenticarti :)"
            self.updater.bot.send_message(chat_id=chatID, text=sendmessage)
            print(
                "\n\n\n\n\n\nReceveid CONFIG command from authenticated user: " + str(user_name))
        else:
            errmessage = "Errore di SETUP\nUsare: CONFIG user password"
            self.updater.bot.send_message(chat_id=chatID, text=errmessage)

        print("USER NAME:" + str(user_name))
        print("PASSWORD: " + str(password))

    def run(self):
        self.updater = Updater(BOTKEY, use_context=True)
        dp = self.updater.dispatcher

        # add an handler for each command
        # start and help are usually defined
        dp.add_handler(CommandHandler("ON", self.ON_Command))
        dp.add_handler(CommandHandler("OFF", self.OFF_Command))

        # add an handler for messages
        dp.add_handler(MessageHandler(Filters.text & ~
        Filters.command, self.get_new_message))
        self.updater.start_polling()
        self.updater.idle()
