import serial
import sys


#special commands
cr = '\x0D' #carriage return
rst = '*RST;' #reset device
idn = '*IDN?' #get identification info


def main():
    portName = "COM1"
    baud = 9600

    ser = serial.Serial(portName, baud, xonxoff = True, timeout =1)
    ser.write(rst + cr)
    ser.write(idn + cr)
    pr = ""
    while(True):
        x = ser.read()
        pr += x
        if (x == '\n'):
            print pr
            break
        

*ESE 60;*SRE 56;*CLS;:STAT:QUES:ENAB 32767	
main()
