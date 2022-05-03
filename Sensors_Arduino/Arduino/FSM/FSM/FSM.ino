//Librerie (seriale, classificatore, math, etc...)
#include <SoftwareSerial.h>

//DICHIARAZIONE COSTANTI E VARIABILI

//Costanti per l'acquisizione dati
#define SAMPLE_RATE 40  //sample rate del sensore in millisecondi
#define VIB_TRESHOLD 50 //treshold cumulativa del sensore di vibrazione
#define MAX_BUFFER 3500 //massimo valore per il buffer del sensore di vibrazione
#define SENSE_TIME 2000 //tempo in millisecondi di cattura dei dati per il feature vector

//Costanti temporali per la comunicazione con bridge
#define LISTEN_DELTA 1000 //intervallo per ogni ascolto di messaggi dal bridge
#define COMM_DELAY 400    //tempo di delay in millisecondi per l'invio di pacchetti al bridge

//Costanti pin circuito
const int RX_PIN = 2;   //pin per la ricezione seriale Bluetooth
const int TX_PIN = 3;   //pin per la trasmissione seriale Bluetooth
const int vib_sens = 9; //pin sensore di vibrazione
const int pir = 7;      //pin sensore di presenza infrarosso (pir)

//pins per led indicatore rgb, utile per visualizzare gli stati ed il sensing
const int r_led = 11;
const int g_led = 12;
const int b_led = 13;

const int FV_LEN = (int)((SENSE_TIME) / SAMPLE_RATE); //lunghezza del feature vector per il sensing

int SENSOR_ID = -1; //id univoco del sensore, da inizializzare all'accensione del sensore
//l'id associato al MAC address del dongle HC-05 Bluetooth verrà comunicato dal bidge all'accensione
//ovvero al passaggio dallo stato IDLE allo stato PIR

//variabili per il protocollo di comunicazione

int message; //variabile ausiliaria per salvare il payload dei messaggi dal bridge

byte ack_byte = 0x01;   //byte di payload per l'ack del sensore verso il bridge
byte alert_byte = 0x02; //byte di payload per l'alert del sensore verso il bridge
int off_payload = 170;

//Variabili (buffer sensore di vibrazione, variabili temporali, variabili sensori,...)
int pir_val = 0;    //variabiale da associare all'uscita del sensore pir
int vib_val = 0;    //variabiale da associare all'uscita del sensore pir
byte FV[FV_LEN];    //feature vector per il salvataggio dei dati captati dal sensore di vibrazione
int vib_buffer = 0; //buffer di accumulazione per il sensore di vibrazione
int i = 0;          //variabile ausiliara

//variabili di soglia per l'analisi dati del sensore
int tresh_mean = 0;
int tresh_var = 0;
int tresh_delta = 0;

//variabili temporali per delay nel sensing e nelle comunicazioni
unsigned long last_sample;
unsigned long start_sense_time;
unsigned long comm_time;

SoftwareSerial BTSerial(RX_PIN, TX_PIN); // RX, TX
//creazione della comunicazione seriale Bluetooth
//RX è il pin per la ricezione, TX per la trasmissione

//DEFINIZIONE DEI PARAMETRI PER LA MACCHINA A STATI FINITI (FSM)

//Variabile per simbolo da associare agli ingressi
char Symb = ' ';

/*
Mapping dei simboli:

-"O": ricevo un dato di on dal bridge: vado allo stato di PIR (sensing)
-"P": ho un segnale dal sensore pir
-"T": ho completato il campionamento del sensore di vibrazione e la classificazione
-"F": ho ricevuto un segnale di off dal bridge: torno allo stato di IDLE
*/

//Variabili di stato presente e futuro
int present_state;
int future_state;

bool sensed = false; //variabile ausiliaria per aggiornare lo stato di fine sensing

/*
Mapping degli stati

0: "IDLE" : stato di OFF sensing/Idle del sensore
1: "PIR" : stato di sensing costante del sensore pir
2: "SENS": stato di sensing del sensore di vibrazione, 
            creazione del feature vector ed invio dati
*/

int default_state = 0; //impostazione stato di default (IDLE)

void setup()
{

  //Inizializzazione delle comunicazioni seriali
  Serial.begin(9600);   //solo per debug USB e raccolta dati
  BTSerial.begin(9600); //Setup baud-rate per la comunicazione seriale BT

  //inizializzazione dei pin di INPUT ed OUTPUT
  pinMode(vib_sens, INPUT);
  pinMode(pir, INPUT);
  pinMode(r_led, OUTPUT);
  pinMode(g_led, OUTPUT);
  pinMode(b_led, OUTPUT);

  //setup dello stato di default: stato di "IDLE"
  present_state = default_state;

  comm_time = millis(); //timer per la comunicazione
}

void loop()
{
  Serial.println("-----------------------------------------------------------");

  pir_val = digitalRead(pir); //lettura del sensore pir

  if (pir_val) //se il pir rileva qualcosa, aggiorno il simbolo di input
  {
    Symb = 'P'; //simbolo associato all'input acceso del pir
  }

  //Associazione dei simboli agli inputs

  if (millis() - comm_time > LISTEN_DELTA)
  {
    Serial.println("Sensing for Bridge data...");

    message = Read_Data();

    if (message != -1)
    {
      if (present_state == 1 && message == off_payload)
      {
        Symb = 'F'; //se ho segnale di OFF -> Symb = 'F'
        Send_ACK();
      }

      if (present_state == 0 && message != off_payload)
      {
        SENSOR_ID = message; //l'ack dal bridge comunica anche l'ID univoco del sensore che viene settato
        Symb = 'O';          //se ho segnale di ON -> Symb = 'O'
        Send_ACK();
      }
      //NOTA: [eventuali comandi per la modifica dei parametri di sensing/altre variabili qui]
    }
    else
    {
      Serial.println("no data/valid data received");
    }

    comm_time = millis(); //reset timer per lettura dati in arrivo dal bridge
  }

  if (sensed) //se il sensing è terminato, aggiorno il simbolo di input
  {
    Symb = 'T';
    sensed = false;
  }

  UpdateState();                //aggiorna gli stati (futuri) a seconda dei simboli associati agli input
                                //OnEnterActions();             //funzione (opzionale) per azioni al passaggio tra stato presente e futuro
  present_state = future_state; //aggiornamento dello stato presente(clock edge)
  UpdateOutput();               //aggiorna gli output a seconda dello stato attuale e di alcune variabili
}

void UpdateState()
{

  switch (present_state)
  {

  case 0: //IDLE
  {
    if (Symb == 'O') //se ho ricevuto il comando di ON dal bridge, passo allo stato 1 (PIR)
    {
      future_state = 1;
      Serial.println("Sensing ON!");
    }
    break;
  }

  case 1: //PIR
  {
    if (Symb == 'P') //se il PIR si attiva, allora passo allo stato 2 (SENSE)
    {
      Serial.println("PIR sensed something!");
      future_state = 2;
    }
    else if (Symb == 'F') //se ho ricevuto il comando di OFF dal bridge, passo allo stato 0 (IDLE)
    {
      future_state = 0;
      Serial.println("Shutting OFF!");
    }
    break;
  }

  case 2: //SENS
  {
    if (Symb == 'T') //se ho terminato il sensing, ritorno allo stato 1 (PIR)
    {
      future_state = 1;
      Serial.println("Ended Vibration Sensing");
    }
    break;
  }
  }
}

void OnEnterActions()
{
  //eventuale codice qui per azioni sul cambio di stato
}

void UpdateOutput() //aggiorna gli output a seconda dello stato presente
{
  switch (present_state)
  {

  case 0: //IDLE
  {
    digitalWrite(r_led, HIGH);
    digitalWrite(g_led, LOW);

    Serial.println("IDLE state");
    break;
  }

  case 1: //PIR
  {
    digitalWrite(r_led, LOW);
    digitalWrite(b_led, LOW);
    digitalWrite(g_led, HIGH); //led verde indica lo stato PIR

    Serial.println("PIR state");
    break;
  }

  case 2: //SENS
  {
    digitalWrite(g_led, LOW);
    digitalWrite(b_led, HIGH); //led blu indica lo stato SENS
    Serial.println("SENS state");

    ReadSensor();    //legge il sensore e produce un vettore di features
    Send_and_wait(); //elabora il vettore di features, lo soglia ed invia i dati al bridge aspettando un ACK
    sensed = true;   //variabile ausiliaria per cambiare il simbolo di input in void loop()
    break;
  }
  }
}

void ReadSensor()
{
  Serial.println("Reading data...");

  for (i = 0; i < FV_LEN; i++) //inizializzo il vettore di features a valori nulli
  {
    FV[i] = 0;
  }
  start_sense_time = millis(); //inizializzo il timer per iniziare il sensing
  last_sample = millis();      //inizializzo il timer per il tempo di sample (sample rate)
  i = 0;                       //inizializzo la variabile per scorrere il vettore di features
  vib_buffer = 0;              //inizializzo il buffer per il sensore di vibrazione

  while (!(millis() - start_sense_time > SENSE_TIME) && i < FV_LEN)
  /*Mentre il tempo trascorso NON è superiore al tempo per il sensing
  e l'indice che scorre FV non supera la lunghezza di FV,
  continuo a ciclare.
  La condizione negata sul tempo serve a prevenire l'overflow (?)*/
  {
    vib_val = digitalRead(vib_sens); //leggo il valore di output del sensore di vibrazione

    if (vib_val == HIGH)
    {
      vib_buffer++; //se rilevo un valore alto dal sensore, allora incremento un buffer
    }

    if (millis() - last_sample > SAMPLE_RATE) //se sono trascorsi più di SAMPLE_RATE millisecondi...
    {
      if (vib_buffer >= VIB_TRESHOLD) //se il buffer supera una certa treshold...
      {
        if (vib_buffer > MAX_BUFFER) //se il buffer supera il valore massimo consentito, lo limito
        {
          vib_buffer = MAX_BUFFER;
        }
        vib_buffer = vib_buffer - VIB_TRESHOLD;               //offset: inizio da zero se supero la treshold
        FV[i] = (byte)map(vib_buffer, 0, MAX_BUFFER, 0, 255); //mapping dei valori in byte
                                                              //...immetto il valore del buffer nella posizione i-esima del vettore
        //Serial.println(FV[i]);                                //solo per debug
      }
      else
      {
        // FV[i] = 0; ...altrimenti, se non ho superato la treshold, registro uno zero
        //non strettamente necessario in quanto ho già tutti i valori inizializzati nulli
        //Serial.println(0); //solo per debug
      }
      i++;                    //incremento l'indice che scorre il vettore, per il prossimo campionamento
      vib_buffer = 0;         //resetto il buffer per il prossimo campionamento
      last_sample = millis(); //reimposto il timer con il tempo dell'ultimo campionamento eseguito
    }
  }

  Serial.println("Reading ended");
}

int Analyze_Data()
{
  Serial.println("Analyzing data...");
  //inizializzazione di variabili per l'anali del vettore di features
  int val = 0;
  int cum_sum = 0;
  int mean = 0;
  float sq_sum = 0;
  int var = 0;
  int max_val = 0;
  int delta = 0;
  int min_not_zero = 255;

  for (int i = 0; i < FV_LEN; i++) //ciclo per il calcolo di minimo, massimo e somma cumulativa
  {
    val = (int)FV[i];
    cum_sum += val;
    max_val = max(max_val, val);
    if (val != 0)
    {
      min_not_zero = min(min_not_zero, val);
    }
  }

  mean = (int)(cum_sum / FV_LEN); //calcolo media

  for (int i = 0; i < FV_LEN; i++) //ciclo per il calcolo della varianza
  {
    val = (int)FV[i];
    sq_sum += ((val - mean) * (val - mean));
  }

  long int max_var = pow((255 - (int)(255 / FV_LEN)), 2);
  var = (long int)((sq_sum / FV_LEN));

  if (var > max_var)
  {
    var = max_var;
  }

  var = map(var, 0, max_var, 0, 255); //calcolo varianza con mapping
  if (min_not_zero != 255)
  {
    delta = abs(max_val - min_not_zero); //calcolo valore picco-picco massimo rilevato
  }
  else
  {
    delta = 0;
  }

  Serial.println("Data analyzed!");
  Serial.println(mean);
  Serial.println(var);
  Serial.println(delta);

  /*
ANALISI RISULTATI:
i valori di media, varianza e delta(picco-picco max) sono sogliati e se le condizioni
sono superate, un valore positivo è ritornato

NOTA: è facilmente implementabile una soluzione con condizioni diverse e la possibilità di ricevere soglie custom dal bridge 
in qualsiasi momento,per variare la sensibilità dei sensori.
E' anche possibili implementare diversi valori di ritorno delle funzione per diversi livelli di alert, 
per poi comunicarli con diversi flag al bridge
*/
  if ((mean > tresh_mean) && (var > tresh_var) && (delta > tresh_delta))
  {
    return 1;
  }

  else
  {
    Serial.println("Data discarded!");
    return 0;
  }
}

void Send_and_wait()
{
  if (Analyze_Data() > 0) //se ho dati validi, li invio al bridge
  {
    Serial.println("SENDING DATA (and waiting for bridge ACK...)");

    digitalWrite(r_led, HIGH);
    digitalWrite(g_led, HIGH);
    digitalWrite(b_led, HIGH);

    int delaycom = COMM_DELAY;
    unsigned long comtime = millis();
    int ack = 0;

    while (ack == 0) //finché non ricevo un ack dal bridge invio dati e leggo dalla seriale
    {
      if (millis() - comtime > delaycom) //comunico ogni delaycom millisecondi se non ricevo ack
      {

        BTSerial.write(0xff);            //header
        BTSerial.write((byte)SENSOR_ID); //comunico anche l'ID del sensore
        BTSerial.write(alert_byte);      //byte = 0x02 per comunicare la presenza di intrusi
        BTSerial.write(0xfe);            //footer

        comtime = millis(); //reset timer
      }

      if (Read_Data() == 1) //se ricevo un pacchetto valido con ACK, smetto di trasmettere
      {
        ack = 1;
        Serial.println("ACK succesfully received from bridge!");
        Send_ACK();
      }
    }
  }

  digitalWrite(r_led, LOW); //led di indicazione
  digitalWrite(g_led, LOW);
  digitalWrite(b_led, LOW);
}

void Send_ACK()
//invia un pacchetto dati al bridge con il proprio ID per segnalare la ricezione dei dati
{

  Serial.println("Sending ACK to Bridge!");
  Serial.println("Sensor ID");
  Serial.println(SENSOR_ID);

  BTSerial.write(0xff);            //byte di header
  BTSerial.write((byte)SENSOR_ID); //comunico anche l'ID del sensore
  BTSerial.write(ack_byte);        //byte = 0x01 per comunicare un ACK
  BTSerial.write(0xfe);            //byte di footer
}

int Read_Data()
{
  /*
La funzione legge dati ricevuti dal bridge. Sono previsti un byte di header e footer per future implementazioni e maggiore robustezza nelle comunicazioni.
Se viene ricevuto un byte di payload valido la funzione lo ritorna come integer, altrimenti ritorna il valore -1.
*/
  Serial.println("reading BT input serial...");

  bool new_data = false;
  bool receiving = false;
  byte rc;

  byte header = 0xff;
  byte footer = 0xfe;
  int payload = -1;

  unsigned long read_time = millis();

  while (!(millis() - read_time > COMM_DELAY) && new_data == false) //leggo per un tempo COMM_DELAY, ma se ricevo subito dati validi interrompo il ciclo
  {
    if (BTSerial.available() > 0) //eseguo solo se ho dati nel buffer
    {
      //Serial.println("Reading a byte");
      rc = BTSerial.read(); //leggo un byte dal buffer

      if (receiving == true) //se ho già letto un header, procedo
      {
        if (rc != footer) //se non ho letto un footer, leggo il payload
        {
          payload = (int)rc;
          //Serial.println("Read payload:");
          //Serial.print(payload);
        }
        else
        {
          //se leggo il footer, ho concluso la lettura e resetto le variabili ausiliarie
          receiving = false;
          new_data = true; //fa si che il ciclo finisca appena sono stati letti dati validi
          //Serial.println("Packet ended");
        }
      }
      else if (rc == header) //se leggo un header, allora inizio la lettura del pacchetto fino al footer
      {
        //Serial.println("Packet Started");
        receiving = true;
      }
    }
  }

  if (payload != -1)
  {
    Serial.println("VALID DATA RECEIVED!");
  };
  Serial.println(payload);
  Serial.println(byte(payload));
  return payload;
}
