import tkinter as tk
import pytz
from datetime import datetime
import socket
import PyIndi
import time

class IndiClient(PyIndi.BaseClient):
    def __init__(self):
        super(IndiClient, self).__init__()
    def newDevice(self, d):
        global dmonitor
        # We catch the monitored device
        dmonitor=d
    def newProperty(self, p):
        global monitored
        global cmonitor
        # we catch the "CONNECTION" property of the monitored device
        if (p.getDeviceName()==monitored and p.getName() == "CONNECTION"):
            cmonitor=p.getSwitch()
    def removeProperty(self, p):
        pass
    def newBLOB(self, bp):
        pass
    def newSwitch(self, svp):
        pass
    def newNumber(self, nvp):
        global newval
        global prop
        # We only monitor Number properties of the monitored device
        prop=nvp
        newval=True
    def newText(self, tvp):
        pass
    def newLight(self, lvp):
        pass
    def newMessage(self, d, m):
        pass
    def serverConnected(self):
        pass
    def serverDisconnected(self, code):
        pass

def mkhrs(time):
  hours = int(time)
  minutes = (time*60) % 60
  seconds = (time*3600) % 60
  outstring = "%d:%02d:%02d" % (hours, minutes, seconds)
  return outstring

# Set up tkinter
root=tk.Tk()
# root.wm_attributes('-fullscreen','true')

# Set up INDI
monitored="Telescope Simulator"
dmonitor=None
cmonitor=None

indiclient=IndiClient()
indiclient.setServer("localhost",7624)

# we are only interested in the telescope device properties
indiclient.watchDevice(monitored)
indiclient.connectServer()

# wait CONNECTION property be defined
while not(cmonitor):
    time.sleep(0.05)

# if the monitored device is not connected, we do connect it
if not(dmonitor.isConnected()):
    # Property vectors are mapped to iterable Python objects
    # Hence we can access each element of the vector using Python indexing
    # each element of the "CONNECTION" vector is a ISwitch
    cmonitor[0].s=PyIndi.ISS_ON  # the "CONNECT" switch
    cmonitor[1].s=PyIndi.ISS_OFF # the "DISCONNECT" switch
    indiclient.sendNewSwitch(cmonitor) # send this new value to the device

# Determine our IP address
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
  # doesn't even have to be reachable
  s.connect(('10.255.255.255', 1))
  IP = s.getsockname()[0]
except:
  IP = '127.0.0.1'
finally:
  s.close()

# Set up grid
root.geometry("480x320")
for x in range(4):
    tk.Grid.columnconfigure(root, x, weight=1)
tk.Grid.rowconfigure(root, 2, weight=1)
tk.Grid.rowconfigure(root, 3, weight=1)
tk.Grid.rowconfigure(root, 4, weight=1)
tk.Grid.rowconfigure(root, 5, weight=1)
tk.Grid.rowconfigure(root, 6, weight=1)

# Top row
currDateText = tk.Label(root, text="", anchor="w") 
currDateText.configure(font='helvetica 12')
currDateText.grid(row=0, column=0, sticky="nsew")
currTimeText = tk.Label(root, text="", anchor="w") 
currTimeText.configure(font='helvetica 12')
currTimeText.grid(row=1, column=0, sticky="nsew")

# Middle Rows
currObjText = tk.Label(root, text="") 
currObjText.configure(font='helvetica 24')
currObjText.grid(row=3, column=0, columnspan=4, sticky="nsew")
currRAText = tk.Label(root, text="") 
currRAText.configure(font='helvetica 24')
currRAText.grid(row=4, column=0, columnspan=4, sticky="nsew")
currDECText = tk.Label(root, text="") 
currDECText.configure(font='helvetica 24')
currDECText.grid(row=5, column=0, columnspan=4,sticky="nsew")

# Bottom Rows
currUTDateText = tk.Label(root, text="", anchor="w") 
currUTDateText.configure(font='helvetica 12')
currUTDateText.grid(row=7, column=0, sticky="nsew")
currUTTimeText = tk.Label(root, text="", anchor="w") 
currUTTimeText.configure(font='helvetica 12')
currUTTimeText.grid(row=8, column=0, sticky="nsew")
currIPtext = tk.Label(root, text=IP, anchor="e") 
currIPText.configure(font='helvetica 12')
currIPtext.grid(row=8, column=3, sticky="nsew")

# ************************ MAINLINE **************************
utc = pytz.utc
newval=False
prop=None
nrecv=0
currObjText.configure(text="Object: Unknown")

while (1):
    if (newval):
      if prop.name == "EQUATORIAL_EOD_COORD":
        for n in prop:
          if n.name == "RA":
             currRA =  n.value
          else:
             currDEC = n.value
        dateTimeObj = datetime.now()
        currDateText.configure(text=dateTimeObj.strftime("%d-%b-%Y"))
        currTimeText.configure(text=dateTimeObj.strftime("%H:%M:%S"))
        dateTimeObj = datetime.now(tz=utc)
        currUTDateText.configure(text=dateTimeObj.strftime("%d-%b-%Y"))
        currUTTimeText.configure(text=dateTimeObj.strftime("%H:%M:%S")+" UT")
        currRAText.configure(text="RA: "+mkhrs(currRA))
        currDECText.configure(text="DEC: "+str(currDEC))
        root.update_idletasks()
        root.update()
        newval=False