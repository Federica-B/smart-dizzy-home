import serial
import logging

#################### SCRIPT RASPBERRY ###############

logger = logging.getLogger('ArduinoSerial')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

logger.addHandler(ch)
############# si ipotizza che sia """"real time"""""
# 1) funzione che chiama il file csv e lo trasforma in un file json riga per riga
# 2) funzone che chiama il file json e lo trasforma in csv riga per riga
# 3) """""""rel time"""""""""" l'output della funzione csvriga va in pasto al modello
# 4) il modello restituisce stress/non stress
# 5) controllo:
#   - se state = si & prev_state = si then hold == do nothing
#   - se state = si & prev_state = no then serialwrite
#   - se state = no & prev = si then serialwrite
#   - se state = no & prev = no then hold == do nothing
######## CASO TEMPERATURA #########
# 5) controllo:
#   - se state = si & prev_state = si then hold == do nothing
#   - se state = si & prev_state = no & temp > 16 or <16  then
#     serial write: request temp --> wait response --> response received
#       - if temp > 16 then serialwrite -4° else serialwrite +4°
#   - se state = no & prev = si then serialwrite
#   - se state = no & prev = no then hold == do nothing

'''
0a) 
1) chamata alla funzione che legge il csv 
2) dal csv lo dò in pasto al modello che dà in output stress sì/stress no 
3) controlla previous state
4) manda attuazione ad arduino
'''
class ArduinoSerial:
    def __init__(self, port, baud_rate):
        self.serial_port = serial.Serial(port, baud_rate, timeout=1)

    def read_data(self):
        # read data from serial port and return as string -> BLOCCANTE
        ack = self.serial_port.readline().decode('utf-8')

        # code return 2-> 200 OK (http) 5 -> 500 server error responcs
        if ack == 2:
            logger.debug("Information correcly delivered")
        if ack == 5:
            logger.debug("Some error occured during the transmission\n The data has been transmitted")
        else:
            logger.error("Not valid code returned")
        return ack


    def write_data(self, data):
        # write data to serial port
        self.serial_port.write(data.encode('utf-8'))

    def close(self):
        # close serial port connection
        self.serial_port.close()


class SerialRoom1 (ArduinoSerial):
    def __init__(self, port, baud_rate, stereo, led):
        super().__init__(port, baud_rate)
        self.stereo = 0
        self.led = 0

    def write_data(self, stereo, led):
        temp = '{'+str(stereo) + ',' + str(led)+'}'
        self.serial_port.write(temp)


class SerialRoom2 (ArduinoSerial):
    def __init__(self, port, baud_rate, thermo, shutter):
        super().__init__(port, baud_rate)
        self.thermo = 0
        self.led = 0

    def write_data(self, stereo, led):
        temp = '{'+str(stereo) + ',' + str(led)+'}'
        self.serial_port.write(temp)

# visto che noi dobbiamo mandare dati e non riceverli, possiamo ipotizzare
# "un ack di ricevimento dell'attuazione" -> AKA mi è arrivato il tuo pacco
# ma non so se effettivamente sia stato attuato perché il mio thread se ne
# lava le mani, mi sono solo arrivati i dati corretti. In questo modo sarebbe
# tipo un main cosi:



message = '{1,124}'
if __name__ == '__main__':

    arduinoSerial = ArduinoSerial('/dev/ttyACM0', 9600)
    room = SerialRoom1('/dev/ttyACM0', 9600)
    try:
        room.write_data(1,50)
        print(room.__getattribute__())
        arduinoSerial.write_data(message)
        #read line
        ack = arduinoSerial.read_data()
    except:
        logger.error("Some error occured in transmission - Arduino Serial")
    finally:
        arduinoSerial.close()