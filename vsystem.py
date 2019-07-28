import crcmod
import serial, serial.rs485
import threading, logging, time
from decimal import *
import vcmd

logging.basicConfig(
     level=logging.INFO,
     format= '[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
     datefmt='%H:%M:%S'
 )

def ph(b):
    r = ''
    for i in b:
        r += '%3.2X' % i
    return r


class vModule:
    '''
    Class to represent a U27-12XP Rev.2, at least to start.
    '''
    moduleUCVoltage = 0
    moduleVoltage = 0
    moduleTemp = 0
    cellVoltage = [0,0,0,0]
    cellTemp = [0,0,0,0]
    cellBalStatus = [0,0,0,0]
    hiCellT = 0
    hiCellV = 0
    loCellT = 0
    loCellV = 0
    soc = 0
    current = 0
    moduleID = 0
    softCMaxV = 3.800
    hardCMaxV = 3.900
    softCMinV = 3.000
    hardCMinV = 2.800

    softCMaxT = 60.00   # alarm
    hardCMaxT = 65.00   # shutdown
    hardCMinTD = -10.0  # shutdown
    hardCMinTC = 0      # shutdown
    softPCBMaxT = 80
    hardPCBMaxT = 85     # shutdown
    seriesPosition = 0
    stringID = 0

    def __init__(self,moduleID,seriesPosition,stringID):
        '''
        init..
        '''
        self.moduleID = moduleID
        self.seriesPosition = seriesPosition
        self.stringID = stringID

    @property
    def ok(self):
        maxv = max(self.cellVoltage)
        minv = min(self.cellVoltage)
        maxt = max(self.cellTemp)
        mint = max(self.cellTemp)
        if maxv < self.myMaxV and minv > self.myMinV and maxt < self.myMaxT and mint > self.myMinT:
            return True
        return False

    # @proprety
    # def maxV(self):
    #     return max(self.cellVoltage)

class vSystem:
    modules = []
    sModules = 0
    pStrings = 0
    serialPort = ''
    sthread = None
    crc = None # function.
    dataLock = threading.Lock()
    newModuleData = threading.Event()
    newSysData = threading.Event()

    # we start with hardware rs485.. self.wakeBMS will change it to software if hardware has problems.
    rsfunc = serial.Serial



    def send(self, b):
        buf = b + self.crc(b).to_bytes(2, byteorder='little') + b'\r\n'
        self.ser.write(buf)


    def __init__(self, seriesModules, parallelStrings, serialPort):

        self.sModules = seriesModules
        self.pStrings = parallelStrings
        self.serialPort = serialPort
        self.crc = crcmod.mkCrcFun(poly=0x18005, rev=True, initCrc=0xFFFF, xorOut=0x0000)
        mID = 0
        # if this is a 4s2p bank, then string 1 will have mod id's 1,2,3,4 and string 2 will be 5,6,7,8.
        for p in range(1, self.pStrings+1):
            for s in range(1,self.sModules+1):
                mID +=1
                self.modules.append(vModule(mID, s, p))

        self.sthread = threading.Thread(target=self.serialThread, daemon=True)
        self.sthread.start()


    def payload(self, b):
        p = b[:-4]
        if self.crc(p).to_bytes(2, byteorder='little') == b[-4:-2]:
            p = b[3:-4]
            n = 2
            return [int.from_bytes(p[i:i+n],'big') for i in range(0, len(p), n)]

    def runCmd(self,module,cmdNum):
        self.send(bytes([module.moduleID]) + (vcmd.cmds[cmdNum]['cmd']))
        seg = self.ser.read(vcmd.cmds[cmdNum]['rlen'])
        return self.payload(seg)


    def signed(self,i):
        # converts unsigned word to signed word.
        if i > 32768:
            return i - 65536
        return i


    def printStats(self):
        m = 0
        self.dataLock.acquire()
        for module in self.modules:
            m += 1
            print('Module:%3d    %7.3fv - %7.3fv (%7.3fv)  %5.2fc  current: %5.2fa  SOC: %4.1f%%' % (module.moduleID,module.moduleVoltage,module.moduleUCVoltage,sum(module.cellVoltage),module.moduleTemp,module.current,module.soc))

            for cell in range(0,4):
                cellLine = '      Cell %3d  %5.3fv  %5.2fc' % (cell+1+((m-1)*4), module.cellVoltage[cell],module.cellTemp[cell])
                if module.cellBalStatus[cell] == 1:
                    cellLine += " (Balancing) "
                print(cellLine)
        self.dataLock.release()

    def wakeBMS(self):
        # first, knock knock.
        # DING DING DING  open and send wake command at 9600 baud...
        try:
            with self.rsfunc(port=self.serialPort,
                             baudrate=9600,
                             bytesize=serial.EIGHTBITS,
                             parity=serial.PARITY_MARK,
                             stopbits=serial.STOPBITS_ONE,
                             timeout=.1,
                             xonxoff=False,
                             rtscts=False,
                             dsrdtr=False,
                             ) as ser:
                ser.rs485_mode = serial.rs485.RS485Settings()
                ser.write(vcmd.startBatteries)
                time.sleep(.1)
        except Exception as e:
            # Exception... hopefully it's because the serial port driver does not support the RS485 ioctl.
            # Let's try again using the software emulation:
            self.rsfunc = serial.rs485.RS485
            with self.rsfunc(port=self.serialPort,
                             baudrate=9600,
                             bytesize=serial.EIGHTBITS,
                             parity=serial.PARITY_MARK,
                             stopbits=serial.STOPBITS_ONE,
                             timeout=.1,
                             xonxoff=False,
                             rtscts=False,
                             dsrdtr=False,
                             ) as ser:
                ser.rs485_mode = serial.rs485.RS485Settings()
                ser.write(vcmd.startBatteries)
                time.sleep(.1)
                # If this exceptions out, it's probably due to a bad com port setting. We'll not trap it.

    def serialThread(self):
        self.wakeBMS()
        # next, we can start the real process.
        with self.rsfunc(port=self.serialPort,
                         baudrate=115200,
                         bytesize=serial.EIGHTBITS,
                         parity=serial.PARITY_MARK,
                         stopbits=serial.STOPBITS_ONE,
                         timeout=.2,
                         xonxoff=False,
                         rtscts=False,
                         dsrdtr=False,
                         ) as self.ser:
            self.ser.rs485_mode = serial.rs485.RS485Settings()
            m1 = Decimal('.1')
            m01 = Decimal('.01')
            m001 = Decimal('.001')

            # Core battery communication loop.
            while True:
                for module in self.modules:
                    # 1 get voltages..
                    p4 = self.runCmd(module,4)
                    # 2 get temperatures..
                    p5 = self.runCmd(module,5)
                    # 3 get SOC.
                    p10 = self.runCmd(module,10)
                    # 4 get module voltage
                    p12 = self.runCmd(module,12)
                    # get lock, we're going to set stuff.
                    self.dataLock.acquire(True)
                    try:
                        # 1 get voltages..
                        if p4 is not None:
                            module.cellVoltage = [Decimal(v) * m001 for v in p4[3:7]]
                            module.hiCellV = Decimal(p4[0]) * m001
                            module.loCellV = Decimal(p4[1]) * m001
                            module.moduleUCVoltage = Decimal(p4[2]) * m001
                        # 2 get temperatures..
                        if p5 is not None:
                            module.cellTemp = [Decimal(self.signed(t)) * m01 for t in p5[1:5]]
                            module.moduleTemp =Decimal(self.signed(p5[0])) * m01
                        # 3 get SOC.
                        if p10 is not None:
                            module.soc = Decimal(p10[0]) * m1
                        # 4 get module voltage
                        if p12 is not None:
                            module.current = Decimal(self.signed(p12[7])) * m01
                            module.moduleVoltage = Decimal(p12[9]) * m001
                            module.cellBalStatus = [not (p12[6] >> 8+x) & 1 for x in range(0,4)]
                    except Exception as e:
                        print(e)
                        self.dataLock.release()
                    self.dataLock.release()
                    # Trigger new module data event
                    self.newModuleData.set()
                # Trigger new system data event
                self.newSysData.set()


if __name__ == '__main__':
    sys = vSystem(4,2,'COM7')
    # sys = vSystem(4, 2, '/dev/ttyUSB0')
    while True:
        #print('hi.')
        sys.newSysData.wait()
        sys.newSysData.clear()
        sys.printStats()



