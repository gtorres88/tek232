import serial
import sys
import time

#special commands
cr = '\x0D' #carriage return
rst = '*RST;' #reset device
idn = '*IDN?' #get identification info

#get id of meter
def getIDN(serialDevice):
    retString = ""
    serialDevice.write(idn+cr)
    x = serialDevice.read()
    while(x != '\n'):
        retString += x
        x = serialDevice.read()
    return retString

#sends reset signal - does everything that cycling power does	
def reset(serialDevice):
    serialDevice.write(rst + cr)

# returns 0 or error string - errors are invalid user strings	
def checkForError(serialDevice):
    retString = ""
    serialDevice.write(':SYST:ERR?' + cr)
    x = serialDevice.read()
    while (x != '\n'):
        retString += x
        x = serialDevice.read()
    errorList = retString.split(',')
    if (int(errorList[0]) == 0):
        return 0
    else:
        return retString

#we don't know what this does		
def initMeter(serialDevice):
    serialDevice.write('*ESE 60;*SRE 56;*CLS;:STAT:QUES:ENAB 32767' + cr)
    return checkForError(serialDevice)

# 0 = off, 1 = on
def setErrorBeeper(serialDevice, setting):
    serialDevice.write('SYSTEM:ERROR:BEEPER ' + str(setting) + cr)
    return checkForError(serialDevice)

# check in manual	
def setAutoZero(serialDevice, setting):
    if (setting == 1):
        serialDevice.write(':ZERO:AUTO ON;' + cr)
    else:
        serialDevice.write(':ZERO:AUTO OFF;' + cr)
    return checkForError(serialDevice)

# sets meter mode to DC current.  samples = num of samples per 1 60 Hz cycle period	
def setCurrentDC(serialDevice, samples):
    serialDevice.write('CONF:CURR:DC;' + cr)
    err = checkForError(serialDevice)
    if (err != 0):
        return err
    serialDevice.write('CURR:DC:NPLC ' + samples + ';' + cr)
    err = checkForError(serialDevice)
    if (err != 0):
        return err
    #serialDevice.write('CURR:DC:RANG 1;' + cr)
    serialDevice.write('CURR:DC:RANG:AUTO ON;' + cr)
    err = checkForError(serialDevice)
    if (err != 0):
        return err
    serialDevice.write('CURR:DC:FILT:STAT ON;' + cr)
    return checkForError(serialDevice)

def setTriggerDelay(serialDevice):
   serialDevice.write(':TRIG:DEL:AUTO ON;:TRIG:SOUR IMM;' + cr)
   return checkForError(serialDevice)
   
def getReading(serialDevice):
   numsamples = 1
   reading = ""
   serialDevice.write(':TRIG:COUN 1;:SAMP:COUN 3;' + cr)
   err = checkForError(serialDevice)
   if (err != 0):
        return err
   serialDevice.write('INIT;' + cr) 
   serialDevice.write('FETC?' + cr) 
   x = serialDevice.read()
   while (x != '\n'):
      if (x == ','):
         x = '\n'
         numsamples  = numsamples + 1
      reading += x
      x = serialDevice.read()
   serialDevice.write(':STAT:QUES:EVEN?' + cr)
   x = serialDevice.read()
   while (x != '\n'):
      x = serialDevice.read()
      
   if (err != 0):
        return err
   return [reading, numsamples]
   
#inputs string of arbitrary number of returned current readings  
def currentTotal(currentIn):
   curTot = 0
   currList = currentIn.split('\n')
   for x in xrange(0,len(currList)):
      curTot += float(currList[x])
   return curTot
      
def finalCalculations(start_time, stop_time, curr_total, samplecount):
    print 'Total Time = ' + str(stop_time - start_time) + ' s'
    print 'Number of Samples = ' + str(samplecount)
    print str(samplecount/(stop_time - start_time)) + ' samples per second'
    #print str(totalCurrent)
    print
    averagecurrent = curr_total/samplecount
    print 'Average Current: ' + str(curr_total/samplecount) + ' Amps'
    return averagecurrent
   
   
def main():
    test_time = 10;
    if (len(sys.argv) != 3):
        print "Argument format: tek232.py serialport duration"
        sys.exit()
        
    portName = sys.argv[1]
    test_time = float(sys.argv[2])
    baud = 230400
    ser = serial.Serial(portName, baud, xonxoff = True, timeout =1)
    reset(ser)
    print getIDN(ser)
    
    #system initialization
    print reset(ser)
    print initMeter(ser)
    print setErrorBeeper(ser, 1)
    print getIDN(ser)
    print setAutoZero(ser, 1)
    print setCurrentDC(ser, '1.0000')
    print setTriggerDelay(ser)
    integral_current = 0
   
    #main loop
    totalCurrent = 0
    numsamples = 0
    t_start = time.time()
    #timeOutFlag = 0;
    time_flag = 0;
    while(time_flag != 1):
        q = getReading(ser)
        print q[0]
        totalCurrent += currentTotal(q[0]) 
        numsamples = numsamples + q[1]
        if(time.time() - t_start >= test_time):
            time_flag = 1;
  
        
        
    #for x in xrange(1,11):
     #  q = getReading(ser)
     #  print q[0]
     #  totalCurrent += currentTotal(q[0]) 
     #  numsamples = numsamples + q[1]
    t_fin = time.time()
    finalCalculations(t_start, t_fin, totalCurrent, numsamples)
    
      

main()
