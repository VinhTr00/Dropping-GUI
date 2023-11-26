from pymavlink import mavutil
from tkinter import *
from tkinter import ttk
import threading
import time

UINT16_MAX = 65535
DROP_NONE = 0
DROP_ONE  = 1
DROP_ALL  = 2
last_heartbeat_hera_recv = time.time()
flag_drop = DROP_NONE
# connection_string = 'tcp:192.168.0.210:20002'
connection_string = 'tcp:192.168.0.215:5760'

flag_connected = 0

root = Tk()
root.title("DROPPING CONTROLLER")
root.geometry("380x200")
root.resizable(False, False)
root.configure(bg="white")
# Status Label
state1 = Label(root, width=300, height=1, bg='white')
state1.pack()

State = Label(root, text="Disconnected",font=("Arial",10,'bold'), width=380, height=1, bg='red')
State.pack(side = BOTTOM)

# the_connection = mavutil.mavlink_connection('tcp:192.168.0.210:20002')
the_connection = 0

def send_rc_override(sec):
    global the_connection
    the_connection.mav.rc_channels_override_send(1, 1, UINT16_MAX, UINT16_MAX, UINT16_MAX, UINT16_MAX, UINT16_MAX, UINT16_MAX, 2000, UINT16_MAX)
    time.sleep(sec)
    the_connection.mav.rc_channels_override_send(1, 1, UINT16_MAX, UINT16_MAX, UINT16_MAX, UINT16_MAX, UINT16_MAX, UINT16_MAX, 1000, UINT16_MAX)

def thread_connect_hera():
    def connecting_hera():
        global the_connection, flag_connected
        while True:
            try:
                if flag_connected == 0:
                    the_connection = mavutil.mavlink_connection(connection_string)
            except:
                pass
            time.sleep(1)
    _thread_connect_hera = threading.Thread(target=connecting_hera, daemon=True)
    _thread_connect_hera.start()
# the_connection = mavutil.mavlink_connection(connection_string)

def thread_check_connection():
    """
    Check connection between GCS and Hera
    """
    def check_connection():
        global last_heartbeat_hera_recv, the_connection, flag_connected
        while True:
            try:
                the_connection.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_GCS,
                                                mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0)
                msg = the_connection.recv_match(type=['HEARTBEAT'])
                print(msg)
                if msg is not None:
                    last_heartbeat_hera_recv = time.time()
                if (time.time() - last_heartbeat_hera_recv) > 5:
                    flag_connected = 0
                    State.config(text="Disconnected", bg="red")
                else:
                    flag_connected = 1
                    State.config(text="Connected", bg="green")          
            except:
                pass
            time.sleep(1)
    _thread_check_connection = threading.Thread(target=check_connection, daemon=True)
    _thread_check_connection.start()
    
def thread_drop():
    """
    Check condition of drop
    """
    def drop_func():
        global flag_drop
        while True:
            try:
                if flag_drop == DROP_ONE:
                    send_rc_override(0.3)
                elif flag_drop == DROP_ALL:
                    send_rc_override(3)
                flag_drop = DROP_NONE
            except:
                pass
            time.sleep(0.5)
    _thread_drop_all = threading.Thread(target=drop_func, daemon=True)
    _thread_drop_all.start()
  
thread_connect_hera()  
thread_check_connection()
thread_drop()

def callback_drop():
    global flag_drop
    print("Drop One")
    flag_drop = DROP_ONE
    
def callback_drop_all():
    global flag_drop
    print("Drop All")
    flag_drop = DROP_ALL

# DropImage = PhotoImage(file='img/air-bomb.png')
# DropImage = DropImage.subsample(4,4)
# DropButton = Button(root,image = DropImage, state= NORMAL, command=callback_drop)
# DropButton.pack(anchor = NW, side = LEFT) 


# DropAllImage = PhotoImage(file='img/bombs.png')
# DropAllImage = DropAllImage.subsample(4,4)
# DropAllButton = Button(root,image = DropAllImage, state= NORMAL, command=callback_drop_all)
# DropAllButton.pack(anchor = NE, side = RIGHT) 

DropButton = Button(root, text="Single Drop", font=("Arial",11,'bold'), state= NORMAL, command=callback_drop, height=6, width=20, bg="#F1948A", activebackground="#F5B7B1")
DropButton.pack(anchor = NW, side = LEFT) 
DropAllButton = Button(root, text="All Drop", font=("Arial",11,'bold'), state= NORMAL, command=callback_drop_all, height=6, width=20, bg="#F1948A", activebackground="#F5B7B1")
DropAllButton.pack(anchor = NE, side = RIGHT)



root.mainloop()