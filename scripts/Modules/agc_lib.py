from dolphin import gui, memory
from .mkw_classes import quatf, vec3
from .mkw_classes import VehiclePhysics, KartMove, RaceConfig, Timer, RaceManagerPlayer, RaceConfigPlayer, RaceScenario
import math

class AGCFrameData:
    """Class to represent a set of value accessible each frame in the memory"""
    def __init__(self, usedefault=False, read_slot = 0):
        if not usedefault:            
            self.position = VehiclePhysics.position(read_slot)
            self.rotation = VehiclePhysics.rotation(read_slot)
            self.IV = VehiclePhysics.internal_velocity(read_slot)
            self.EV = VehiclePhysics.external_velocity(read_slot)
            self.maxIV = KartMove.soft_speed_limit(read_slot)
            self.curIV = KartMove.speed(read_slot)
            self.ODA = KartMove.outside_drift_angle(read_slot)
            self.dir = KartMove.dir(read_slot)
            self.dive = KartMove.diving_rotation(read_slot)
            #todo inputs
            self.input = None            
        else:
            self.position = vec3(0,0,0)
            self.rotation = quatf(0,0,0,0)
            self.IV = vec3(0,0,0)
            self.EV = vec3(0,0,0)
            self.maxIV = 0
            self.curIV = 0
            self.ODA = 0
            self.dir = vec3(0,0,0)
            self.dive = 0
            #todo inputs
            self.input = None 

    def __iter__(self)
        return iter([self.position,
              self.rotation,
              self.IV,
              self.EV,
              self.maxIV,
              self.curIV,
              self.ODA,
              self.dir,
              self.dive,
              self.input])

    def __str__(self):
        return ';'.join(map(str, self))

    @staticmethod
    def read_from_string(string):
        res = AGCFrameData(usedefault = True)
        temp = string.split(';')
        assert len(temp) == 10
        
        res.position = vec3.from_string(temp[0])
        res.rotation = quatf.from_string(temp[1])
        res.IV = vec3.from_string(temp[2])
        res.EV = vec3.from_string(temp[3])
        res.maxIV = float(temp[4])
        res.curIV = float(temp[5])
        res.ODA = float(temp[6])
        res.dir = vec3.from_string(temp[7])
        res.dive = float(temp[8])
        res.input #todo

        return res

    def interpolate(self,other, selfi, otheri):
        #Call only if self.value[0] represent a vec3
        v1 = vec3.from_bytes(self.values[0])
        v2 = vec3.from_bytes(other.values[0])
        v = (v1*selfi)+(v2*otheri)
        self.values[0] = v.to_bytes()

    def load(self, write_slot):
        kma = KartMove.chain(write_slot)
        vpa = VehiclePhysics.chain(write_slot)

        self.position.write(vpa + 0x68)
        self.rotation.write(vpa + 0xF0)
        self.IV.write(vpa + 0x14C)
        self.EV.write(vpa + 0x74)
        memory.write_f32(kma + 0x18, self.maxIV)
        memory.write_f32(kma + 0x20, self.curIV)
        memory.write_f32(kma + 0x9C, self.ODA)
        self.dir.write(kma + 0x5C)
        memory.write_f32(kma + 0xF4, self.dive)
        #todo play inputs



class MetaData:
    "Class for the metadata of a ghost."

    def __init__(self, useDefault = false, read_id = 0):
        if not useDefault:
            rcp = RaceConfigPlayer(RaceScenario(RaceConfig.race_scenario()).player(read_id))
            self.charaID = int(rcp.character_id())
            self.vehicleID = int(rcp.vehicle_id())
            self.driftID = None
            self.timer_data = [Split.from_timer(RaceManagerPlayer.lap_finish_time(read_id, lap)) for lap in range(3)]
        else:
            self.charaID = 0
            self.vehicleID = 0
            self.driftID = 0
            self.timer_data = []

    def __str__(self):
        return ";".join(map(str, self))

    def __iter__(self):
        return iter([self.charaID, self.vehicleID, self.driftID]+self.timer_data)

    @staticmethod
    def read_from_string(string):
        res = Metadata(useDefault = True)
        temp = string.split(";")

        assert len(temp) >= 3

        res.charaID = int(temp[0])
        res.vehicleID = int(temp[1])
        res.driftID = int(temp[2])
        res.timer_data = [Split.from_string(temp[i]) for i in range(3, len(temp))]

        return res

    def load(self, write_slot):
        

        

class Split:
    """Class for a lap split. Contain just a float, representing the split in s"""
    def __init__(self, f):
        self.val = f
    def __str__(self):
        return f"{self.val:.3f}"
    def __add__(self,other):
        return Split(max(0, self.val+other.val)) 

    @staticmethod
    def from_string(string):
        return Split(float(string))

    @staticmethod
    def from_time_format(m,s,ms):
        return Split(m*60+s+ms/1000)
    
    @staticmethod
    def from_timer(timer_inst):
        return Split(timer_inst.minutes()*60+timer_inst.seconds()+timer_inst.milliseconds()/1000)
    
    @staticmethod
    def from_bytes(b):
        data_int = b[0]*256*256+b[1]*256+b[2]
        ms = data_int%1024
        data_int = data_int//1024
        s = data_int%128
        data_int = data_int//128
        m = data_int%128
        return Split(m*60+s+ms/1000)

    @staticmethod
    def from_rkg(rkg_addr,lap):
        timer_addr = rkg_addr+0x11+0x3*(lap-1)
        b = memory.read_bytes(timer_addr, 3)
        return Split.from_bytes(b)
        
    
    def time_format(self):
        #return m,s,ms corresponding
        f = self.val
        ms = round((f%1)*1000)
        s = math.floor(f)%60
        m = math.floor(f)//60
        return m,s,ms
    
    def bytes_format(self):
        #return a bytearray of size 3 for rkg format
        m,s,ms = self.time_format()
        data_int = ms+s*1024+m*1024*128
        b3 = data_int%256
        data_int = data_int//256
        b2 = data_int%256
        data_int = data_int//256
        b1 = data_int%256
        return bytearray((b1,b2,b3))

    def time_format_bytes(self):
        #return a bytearray of size 6, for the timer format.
        #2 first bytes are m, then s on 1 byte, then 00, then ms on 2 bytes
        m,s,ms = self.time_format()
        return bytearray([m//256, m%256, s%256, 0, ms//256, ms%256])


class TimerData:
    """Class for the laps splits, both in RKG and Timer format
        Cumulative convention (lap2 split is stored as lap1+lap2)"""
    def __init__(self,string =None, readid=0, splits = None):
        #Call with a string OR when the race is finished
        if string is None:
            if splits is None:
                self.splits = [] #List of Split (size 3)
                timerlist = [RaceManagerPlayer.lap_finish_time(readid, lap) for lap in range(3)]
                for timer in timerlist:
                    self.splits.append(Split.from_time_format(timer.minutes(), timer.seconds(), timer.milliseconds()))
            else:
                self.splits = splits
        else:
            self.splits = []
            laps = string.split(';')
            for lap in laps:
                self.splits.append(Split.from_string(lap))

    @staticmethod
    def from_sliced_rkg(rkg_metadata):
        sliced_bytes = rkg_metadata.values[3]
        l1 = Split.from_bytes(sliced_bytes[1:4])
        l2 = Split.from_bytes(sliced_bytes[4:7])+l1
        l3 = Split.from_bytes(sliced_bytes[7:10])+l2
        return TimerData(splits = [l1,l2,l3])

    def __str__(self):
        text = 't'
        for split in self.splits:
            text += str(split)+";"
        text = text[:-1]
        return text+'\n'

    def add_delay(self, delay):
        s = -delay/59.94
        for i in range(len(self.splits)):
            self.splits[i] = Split(max(self.splits[i].val+s, 0))


    def to_bytes(self):
        #A lap split is 3 bytes, so there is 9 bytes total
        #Non cumulative format, ready to be written in a rkg
        r = bytearray()
        prev = 0
        for split in self.splits:
            r = r + Split(split.val - prev).bytes_format()
            prev = split.val
        return r
    
    def write_rkg(self):
        r = rkg_addr()
        memory.write_bytes(r+0x11, self.to_bytes())
            
                 
def metadata_to_file(filename, readid):
    #Should be called before the countdown
    metadata = FrameData(get_metadata_addr(readid))
    file = open(filename, 'w')
    if file is None :
        gui.add_osd_message("Error : could not create the data file")
    else :
        file.write(str(metadata))
        file.close()
        gui.add_osd_message(f"{filename} successfully opened")

def get_metadata(readid):
    return FrameData(get_metadata_addr(readid))

def get_rkg_metadata():
    return FrameData(get_rkg_metadata_addr())

def rkg_metadata_to_file(filename):
    rkg_metadata = get_rkg_metadata()
    file = open(filename, 'w')
    if file is None :
        gui.add_osd_message("Error : could not create the data file")
    else :
        file.write("r"+str(rkg_metadata))
        file.close()
        gui.add_osd_message(f"{filename} successfully opened")   

def frame_to_file(filename, frame_data):
    file = open(filename, 'a')
    if file is None :
        gui.add_osd_message("Error : could not create the data file")
    else :
        file.write(str(frame_data)+ "\n")
        file.close()

def get_framedata(readid):
    return FrameData(read_slot = readid)
    
def timerdata_to_file(filename, rid):
    timerdata = TimerData(readid = rid)
    file = open(filename, 'a')
    if file is None :
        gui.add_osd_message("Error : could not create the data file")
    else :
        file.write(str(timerdata))
        file.close()

def get_timerdata(rid):
    return TimerData(readid = rid)
        
def file_to_framedatalist(filename):
    datalist = []
    file = open(filename, 'r')
    if file is None :
        gui.add_osd_message("Error : could not load the data file")
    else:
        timerdata = None
        metadata = None
        rkg_metadata = None
        listlines = file.readlines()
        if listlines[0][0] == 'r':           
            rkg_metadata = FrameData(string = listlines[0][1:])
            timerdata = TimerData.from_sliced_rkg(rkg_metadata)
        else:
            metadata = FrameData(string = listlines[0])
            if listlines[-1][0]=='t':
                timerdata = TimerData(string = listlines.pop()[1:])
        for i in range(1, len(listlines)):
            datalist.append(FrameData.read_from_string(listlines[i]))
        file.close()
        gui.add_osd_message(f"Data successfully loaded from {filename}")
        return metadata, datalist, timerdata, rkg_metadata


def framedatalist_to_file(filename, datalist, rid):
    metadata = get_metadata(rid)
    timerdata = get_timerdata(rid)
    file = open(filename, 'w')
    if file is None :
        gui.add_osd_message("Error : could not create the data file")
    else:
        file.write(str(metadata))
        for frame in range(max(datalist.keys())+1):
            if frame in datalist.keys():
                file.write(str(datalist[frame]))
            else:
                file.write(str(FrameData(usedefault=True)))
        file.write(str(timerdata))
        file.close()

def framedatalist_to_file_rkg(filename, datalist):
    metadata = get_rkg_metadata()
    file = open(filename, 'w')
    if file is None :
        gui.add_osd_message("Error : could not create the data file")
    else:
        file.write('r'+str(metadata))
        for frame in range(max(datalist.keys())+1):
            if frame in datalist.keys():
                file.write(str(datalist[frame])+"\n")
            else:
                file.write(str(FrameData(get_addr(rid), usedefault=True))+"\n")
        file.close()


def get_addr(player_id):
    a = VehiclePhysics.chain(player_id)
    b = KartMove.chain(player_id)
    return [(a+0x68, 12), #Position
            (a+0xF0, 16), #Rotation
            (a+0x74, 12), #EV
            (a+0x14C, 12), #IV
            (b+0x18, 4), #MaxEngineSpd
            (b+0x20, 4), #EngineSpd
            (b+0x9C, 4), #OutsideDriftAngle
            (b+0x5C, 12)]#Dir

def get_metadata_addr(player_id):
    a = RaceConfig.chain() + player_id*0xF0
    return [(a+0x30, 8)]#CharacterID and VehicleID

def rkg_addr():
    return memory.read_u32(RaceConfig.chain() + 0xC0C)

def get_rkg_metadata_addr():
    r = rkg_addr()
    return [(r+0x4, 3), #Skipping track ID
            (r+0x8, 4), #Skipping Compression flag
            (r+0xD, 1), #Skipping Input Data Length
            (r+0x10, 0x78)]

def is_rkg():
        s = bytearray('RKGD', 'ASCII')
        r = rkg_addr()
        return s == memory.read_bytes(r, 4)    
