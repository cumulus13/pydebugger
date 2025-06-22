#-*- encoding: utf-8 -*-
#encoding: utf-8
# from __future__ import print_function

import os
import time
import sys
import argparse
import shutil
from rich import traceback as rich_traceback, console
console = console.Console(width = shutil.get_terminal_size()[0])
rich_traceback.install(theme = 'fruity', max_frames = 30, width = shutil.get_terminal_size()[0])
from rich.syntax import Syntax
import inspect
import random
import socket
import cmdw
import datetime
from make_colors import make_colors
import importlib
import re
import traceback
import ctypes
from urllib.parse import quote_plus
import socket
from collections import OrderedDict
import signal
configset = importlib.import_module('configset')
from pathlib import Path
try:
    from .custom_rich_help_formatter import CustomRichHelpFormatter
except:
    from custom_rich_help_formatter import CustomRichHelpFormatter
    
CONFIGNAME = str(Path(__file__).cwd() / 'debug.ini') if (Path(__file__).cwd() / 'debug.ini').is_file() else str(Path(__file__).parent / 'debug.ini')
CONFIG = configset.configset(CONFIGNAME)
USE_SQL = False

#sqlalchemy import
try:
    from sqlalchemy import create_engine, Column, Integer, Text, text, func, TIMESTAMP #, String, Boolean, TIMESTAMP, BigInteger, Text
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
    USE_SQL = True
    Base = declarative_base()
except:
    pass

PID = os.getpid()
HANDLE = None

#width calculation (shtil/cmdw)
if sys.version_info.major == 3:
    MAX_WIDTH = shutil.get_terminal_size()[0]
else:
    MAX_WIDTH = cmdw.getWidth()

DEBUG = False

if os.getenv('DEBUG') and os.getenv('DEBUG') in ['1', 'true', 'True', 1]:
    DEBUG = True
elif DEBUG in ['1', 'true', 'True', 1]:
    DEBUG = True
    os.environ.update({'DEBUG':'1'})
########################################################################################################################################
DEBUG_SERVER = False
if DEBUG_SERVER in ['1', 'true', 'True', 1]: DEBUG_SERVER = True

if os.getenv('DEBUG_SERVER') and os.getenv('DEBUG_SERVER') in ['1', 'true', 'True', 1]: DEBUG_SERVER = True

########################################################################################################################################
DEBUG_PORT = 50001
DEBUG_PORT = os.getenv('DEBUG_PORT') or DEBUG_PORT

DEBUG_PORT2 = 50002
DEBUG_PORT2 = os.getenv('DEBUG_PORT2') or DEBUG_PORT2

DEBUG_PORT3 = 50003
DEBUG_PORT3 = os.getenv('DEBUG_PORT3') or DEBUG_PORT3

DEBUG_PORT4 = 50004
DEBUG_PORT4 = os.getenv('DEBUG_PORT3') or DEBUG_PORT4

########################################################################################################################################
DEBUG_HOST = '127.0.0.1'
DEBUG_HOST = os.getenv('DEBUG_HOST') or DEBUG_HOST

DEBUG_HOST2 = ''
DEBUG_HOST2 = os.getenv('DEBUG_HOST2') or DEBUG_HOST2

DEBUG_HOST3 = ''
DEBUG_HOST3 = os.getenv('DEBUG_HOST3') or DEBUG_HOST3

DEBUG_HOST4 = ''
DEBUG_HOST4 = os.getenv('DEBUG_HOST4') or DEBUG_HOST4

########################################################################################################################################
DEBUGGER_SERVER = [f'{DEBUG_HOST or "127.0.0.1"}:{DEBUG_PORT or 50001}']
DEBUGGER_SERVER2 = []
DEBUGGER_SERVER3 = []

if os.getenv('DEBUGGER_SERVER'):
    env_val = os.getenv('DEBUGGER_SERVER').strip()
    if ";" in env_val or "," in env_val:
        sep = ";" if ";" in env_val else ","
        items = [item.strip() for item in env_val.split(sep) if item.strip()]
        DEBUGGER_SERVER = []
        for item in items:
            if ":" in item:
                host, port = item.split(":")
                host = host or DEBUG_HOST
                port = int(port or DEBUG_PORT)
                DEBUGGER_SERVER.append(f"{host}:{port}")
            elif item.isdigit():
                DEBUGGER_SERVER.append(f"{DEBUG_HOST or '127.0.0.1'}:{item}")
            else:
                DEBUGGER_SERVER.append(item)
    elif ":" in env_val:
        host, port = env_val.split(":")
        host = host or DEBUG_HOST
        port = int(port or DEBUG_PORT)
        DEBUGGER_SERVER = [f"{host}:{port}"]
    elif env_val.isdigit():
        DEBUGGER_SERVER = [f"{DEBUG_HOST or '127.0.0.1'}:{env_val}"]
    else:
        DEBUGGER_SERVER = [env_val]

try:
    from . import __version__
    VERSION = __version__
except:
    try:
        import __version__
        VERSION = __version__
    except:
        VERSION = 'UNKNOWN'

force = False

def get_width():
    width = 80
    try:
        width = shutil.get_terminal_size()[0]
    except:
        width = cmdw.getWidth()
    return width

def get_source(source):
    if sys.version_info.major == 3:
        console.print(Syntax(inspect.getsource(source), "python", theme = 'fruity', line_numbers=True, tab_size=2, code_width=get_width(), word_wrap = True))
        # print("WIDTH:", get_width())
    else:
        try:
            cmd = """python3 -c \"import {};import inspect;from rich.console import Console;from rich.syntax import Syntax;console = Console();console.print(Syntax(inspect.getsource({}), 'python', theme = 'fruity', line_numbers=True, tab_size=2, code_width={}))\"""".format(source.__module__, source.__module__, get_width())
            os.system(cmd)
        except:
            cmd = """python3 -c \"import {};import inspect;from rich.console import Console;from rich.syntax import Syntax;console = Console();console.print(Syntax(inspect.getsource({}), 'python', theme = 'fruity', line_numbers=True, tab_size=2, code_width={}))\"""".format(source.__name__, source.__name__, get_width())
            os.system(cmd)

def debug_server_client(msg, host = '127.0.0.1', port = 50001):
    RECEIVER_HOST = CONFIG.get_config_as_list('RECEIVER', 'HOST') or host
    if not isinstance(RECEIVER_HOST, list): RECEIVER_HOST = [RECEIVER_HOST]
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    if RECEIVER_HOST:
        for i in RECEIVER_HOST:
            if ":" in i:
                host, port = str(i).strip().split(":")
                port = int(port.strip())
                host = host.strip()
            else:
                host = i.strip()
            
            s.sendto(msg, (host, port))
            s.close()

def debug_self(**kwargs):
    return debug(**kwargs)

def get_max_width():
    try:
        MAX_WIDTH = shutil.get_terminal_size()[0]
    except:
        MAX_WIDTH = cmdw.getWidth()
    return MAX_WIDTH

def serve(host = '0.0.0.0', port = 50001, on_top=False, center = False):
    global DEBUGGER_SERVER
    BUFFER_SIZE = CONFIG.get_config('buffer', 'size', '1024')  # Adjust as needed
    END_MARKER = b'<END>'    
    
    if os.getenv('DEBUG_EXTRA') == '1': print("host [1]:", host)
    if os.getenv('DEBUG_EXTRA') == '1': print("port [1]:", port)
    
    on_top = CONFIG.get_config('display', 'on_top') or on_top
    if on_top: set_detach(center = center, on_top = on_top)
    host1 = ''
    port1 = ''
    DEBUGGER_SERVER = debugger.check_debugger_server(host, port) or DEBUGGER_SERVER
    if os.getenv('DEBUG_EXTRA') == '1': print("DEBUGGER_SERVER:", DEBUGGER_SERVER)
    if DEBUGGER_SERVER:
        if isinstance(DEBUGGER_SERVER, list):
            for i in DEBUGGER_SERVER:
                if ":" in i:
                    host1, port1 = str(i).split(":")
                    port1 = int(port1)
                    if not host1: host1 = '127.0.0.1'
                    if os.getenv('DEBUG_EXTRA') == '1': print("host [2]:", host1)
                    if os.getenv('DEBUG_EXTRA') == '1': print("port [2]:", port1)                    
                else:
                    if str(i).isdigit():
                        port1 = int(i)
                    else:
                        host1 = i
                    if os.getenv('DEBUG_EXTRA') == '1': print("host [3]:", host1)
                    if os.getenv('DEBUG_EXTRA') == '1': print("port [3]:", port1)                    
        else:
            if ":" in DEBUGGER_SERVER:
                host1, port1 = str(DEBUGGER_SERVER).split(":")
                port1 = int(port1)
                if not host1: host1 = '127.0.0.1'
                if os.getenv('DEBUG_EXTRA') == '1': print("host [4]:", host1)
                if os.getenv('DEBUG_EXTRA') == '1': print("port [4]:", port1)                
            else:
                if str(DEBUGGER_SERVER).isdigit():
                    port1 = int(i)
                else:
                    host1 = DEBUGGER_SERVER
                if os.getenv('DEBUG_EXTRA') == '1': print("host [5]:", host1)
                if os.getenv('DEBUG_EXTRA') == '1': print("port [5]:", port1)                
    # if host == '0.0.0.0': host = '127.0.0.1'
    if not port: port = 50001
    if not isinstance(port, str) and str(port).isdigit():
        port = int(port)
    
    if os.getenv('DEBUG_EXTRA') == '1': print("host [6]:", host)
    if os.getenv('DEBUG_EXTRA') == '1': print("port [6]:", port)
        
    host = host1 or host or CONFIG.get_config('DEBUGGER', 'HOST')
    port = port1 or port or CONFIG.get_config('DEBUGGER', 'PORT')
    
    if os.getenv('DEBUG_EXTRA') == '1': print("host [7]:", host)
    if os.getenv('DEBUG_EXTRA') == '1': print("port [7]:", port)
    
    # if host == '0.0.0.0': host = '127.0.0.1'
    
    def receive_message(server_socket):
        full_message = b''
        while True:
            #chunk = server_socket.recv(BUFFER_SIZE).decode() #TCP
            chunk, _ = server_socket.recvfrom(BUFFER_SIZE) #UDP
            
            if END_MARKER in chunk:
                full_message += chunk.replace(END_MARKER, b'')
                break
            full_message += chunk
        return full_message
    
    #server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP
    #server_socket.bind((host, port)) #TCP
    #server_socket.listen(1) #TCP
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))    
    
    print(make_colors("BIND: ", 'white', 'green') + make_colors(host, 'white', 'red', attrs= ['bold']) + ":" + make_colors(str(port), 'black', 'yellow', attrs= ['bold']))
    try:
        while True:
            #client_socket, client_address = server_socket.accept() #TCP
            #print(f"Connected to {client_address}")
            
            #msg = receive_message(client_socket) #TCP
            msg = receive_message(server_socket)
            
            #print(f"Received msg: {msg}")
            #print(msg)
            if msg:
                if CONFIG.get_config('display', 'on_top') == 1 or CONFIG.get_config('display', 'on_top') == True:
                    showme()
                    
                if hasattr(msg, 'decode'):# and sys.version_info.major == 2:
                    #msg = msg.decode('utf-8')
                    msg = msg.decode(errors = 'replace')
                    
                if msg == 'cls' or msg == 'clear':
                    if sys.platform == 'win32':
                        os.system('cls')
                    else:
                        os.system('clear')
                else:
                    print(msg)
                    
                print("=" * get_max_width())
    
            #server_socket.close() #TCP
            
    except KeyboardInterrupt:
        print(make_colors("server shutdown ...", 'lw', 'lr'))
        os.kill(os.getpid(), signal.SIGTERM)
        
def serve1(host = '0.0.0.0', port = 50001, on_top=False, center = False):
    on_top = CONFIG.get_config('display', 'on_top') or on_top
    if on_top: set_detach(center = center, on_top = on_top)
    host1 = ''
    port1 = ''
    if DEBUGGER_SERVER:
        if isinstance(DEBUGGER_SERVER, list):
            for i in DEBUGGER_SERVER:
                if ":" in i:
                    host1, port1 = str(i).split(":")
                    port1 = int(port1)
                    if not host1: host1 = '127.0.0.1'
                else:
                    if str(i).isdigit():
                        port1 = int(i)
                    else:
                        host1 = i
        else:
            if ":" in DEBUGGER_SERVER:
                host1, port1 = str(DEBUGGER_SERVER).split(":")
                port1 = int(port1)
                if not host1: host1 = '127.0.0.1'
            else:
                if str(DEBUGGER_SERVER).isdigit():
                    port1 = int(i)
                else:
                    host1 = DEBUGGER_SERVER
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65507)
    
    if not host:
        if CONFIG.get_config('DEBUGGER', 'HOST', value= '0.0.0.0'):
            host = CONFIG.get_config('DEBUGGER', 'HOST')
        else:
            host = host1
    if not port:
        if CONFIG.get_config('DEBUGGER', 'PORT', value= '50001'):
            port = CONFIG.get_config('DEBUGGER', 'PORT')
            port = int(port)
        else:
            port = port1
    
    if not host:
        host = '127.0.0.1'
    if not port:
        port = 50001
        
    while 1:
        try:
            s.bind((host, int(port)))
            break
        except socket.error:
            port = port + 1

    print(make_colors("BIND: ", 'white', 'green') + make_colors(host, 'white', 'red', attrs= ['bold']) + ":" + make_colors(str(port), 'black', 'yellow', attrs= ['bold']))
    try:
        while 1:
            #msg = s.recv(6556500)
            msg = s.recv(65507)
            if msg:
                if hasattr(msg, 'decode'):
                    msg = msg.decode('utf-8')
                if msg == 'cls' or msg == 'clear':
                    if sys.platform == 'win32':
                        os.system('cls')
                    else:
                        os.system('clear')
                else:
                    if CONFIG.get_config('display', 'on_top') == 1 or CONFIG.get_config('display', 'on_top') == True:
                        showme()
                    print(str(msg))
                if sys.platform == 'win32':
                    print("=" * (MAX_WIDTH - 3))
                else:
                    print("=" * ((MAX_WIDTH * 2) - 3))
    except KeyboardInterrupt:
        os.kill(os.getpid(), signal.SIGTERM)

def check_debug():
    DEBUG = os.getenv('DEBUG')
    DEBUG_SERVER = os.getenv("DEBUG_SERVER")
    DEBUGGER_SERVER = os.getenv("DEBUGGER_SERVER")
        
    if DEBUG == 1 or DEBUG == '1': DEBUG = True
    elif DEBUG == 0 or DEBUG == '0': DEBUG = False
    
    if os.getenv('DEBUG') == 1 or os.getenv('DEBUG') == '1': DEBUG = True
    if os.getenv('DEBUG') == 0 or os.getenv('DEBUG') == '0': DEBUG = False
    
    if isinstance(DEBUG, str):
        if not DEBUG.isdigit() and DEBUG.lower() in ['true', 'false']:
            DEBUG = bool(DEBUG.title())
    
    DEBUG_SERVER = os.getenv('DEBUG_SERVER')
    
    if DEBUG_SERVER == 1 or DEBUG_SERVER == '1': DEBUG_SERVER = True
    if DEBUG_SERVER == 0 or DEBUG_SERVER == '0': DEBUG_SERVER = False
    if DEBUG_SERVER == "True": DEBUG_SERVER = True
    if DEBUG_SERVER == "False": DEBUG_SERVER = False
    
    DEBUGGER_SERVER = ['127.0.0.1:50001']
    
    if os.getenv('DEBUGGER_SERVER'):
        if ";" in os.getenv('DEBUGGER_SERVER'):
            DEBUGGER_SERVER = os.getenv('DEBUGGER_SERVER').strip().split(";")
        elif os.getenv('DEBUGGER_SERVER').isdigit():
            DEBUGGER_SERVER = ['127.0.0.1:' + os.getenv('DEBUGGER_SERVER')]
        else:
            DEBUGGER_SERVER = [os.getenv('DEBUGGER_SERVER')]
    
    
    FILENAME = ''
    if os.getenv('DEBUG_FILENAME'): FILENAME = os.getenv('DEBUG_FILENAME')
    
    return DEBUG, DEBUG_SERVER, DEBUGGER_SERVER

def set_detach(width = 700, height = 400, x = 10, y = 50, center = False, buffer_column = 9000, buffer_row = 77, on_top = True):
    if not sys.platform == 'win32':
        return False
    from dcmd import dcmd
    setting = dcmd.dcmd()
    setting.setBuffer(buffer_row, buffer_column)
    screensize = setting.getScreenSize()
    setting.setSize(width, height, screensize[0] - width, y, center)
    if on_top: setting.setAlwaysOnTop(width, height, screensize[0] - width, y, center)
    
# def version():
#     try:
#         try:
#             from . import __version__
#         except:
#             import __version__
#         return __version__.version
#     except:
#         #print(traceback.format_exc())
#         return "UNKNOWN"

def showme():
    if not sys.platform == 'win32':
        return False
    global HANDLE
    # import ctypes
    # import win32gui, win32con
    # import ctypes
    # kernel32 = ctypes.WinDLL('kernel32')
    # handle = kernel32.GetStdHandle(-11)
    # handle1 = win32gui.GetForegroundWindow()
    # handle2 = ctypes.windll.user32.GetForegroundWindow()
    # print("HANDLE 0:", handle)
    # print("HANDLE 1:", handle1)
    # print("HANDLE 2:", handle2)
    #win32gui.MessageBox(None, str(HANDLE), str(HANDLE), 0)
    # handle = HANDLE
    # if not handle:
    #     handle = win32gui.GetForegroundWindow()
    # handle = win32gui.GetForegroundWindow()
    #handle1 = handle = win32gui.GetForegroundWindow()
    # print("HANDLE:", HANDLE)
    if HANDLE:
        # win32gui.ShowWindow(HANDLE, win32con.SW_RESTORE)
        # win32gui.SetForegroundWindow(HANDLE)
        # win32gui.BringWindowToTop(HANDLE)
        ctypes.windll.user32.SetForegroundWindow(HANDLE)
    
    #win32gui.SetWindowPos(handle, win32con.HWND_TOPMOST, 0, 0, 0, 0, 0)
    
    #win32gui.SetForegroundWindow(handle)

    #win32gui.ShowWindow(handle1,9)
    #win32gui.SetForegroundWindow(handle1)
    #win32gui.SetWindowPos(handle, win32con.HWND_TOPMOST, None, None, None, None, 0)

def cleanup(filename):
    import shutil
    from datetime import datetime
    
    file_dir = os.path.dirname(filename)
    file_name = os.path.basename(filename)
    file_ext = os.path.splitext(file_name)
    ext = ''
    if len(file_ext) == 2:
        ext = file_ext[1]

    shutil.copyfile(filename, os.path.join(file_dir, file_ext[0] + "_" + datetime.strftime(datetime.now(), '%Y%m%d_%H%M%S%f') + ext))

    data = ''
    fileout = ''
    fileout1 = ''
    if sys.version_info.major == 2:
        with open(filename, 'rb') as f:
            data = f.readlines()
    else:
        with open(filename, 'r') as f:
            data = f.readlines()
    datax = ""
    for i in data:
        if not re.findall(r'debug\\(.*?\\).*?\\n', i):
            datax += i
    
    if len(file_ext) == 2:
        file_ext = file_ext[1]
    else:
        file_ext = ""
    if not "_debug" in file_name:
        fileout = os.path.join(file_dir, os.path.splitext(file_name)[0] + "_release" + ext)
        fileout1 = filename.replace("_debug", "")
    else:
        fileout = filename.replace("_debug", "")
    print("FILENAME:", filename)
    print("FILEOUT :", fileout)

    if sys.version_info.major == 2:
        with open(fileout, 'wb') as f:
            data = f.write(datax)
        if fileout1:
            with open(fileout1, 'wb') as f:
                data = f.write(datax)
    else:
        with open(fileout, 'w') as f:
            data = f.write(datax)
        if fileout1:
            with open(fileout, 'w') as f:
                data = f.write(datax)
    if not "_debug" in file_name:
        shutil.copyfile(filename, os.path.join(file_dir, os.path.splitext(file_name)[0] + "_debug" + ext))
    
class DebugDB(Base):
    __tablename__ = 'debug'

    id = Column(Integer, primary_key=True,  autoincrement=True)
    created = Column(TIMESTAMP, server_default=func.now())
    message = Column(Text)
    tag = Column(Text, server_default="debug")

class MultiOrderedDict(OrderedDict):
    def __setitem__(self, key, value):
        if isinstance(value, list) and key in self:
            self[key].extend(value)
        else:
            super(OrderedDict, self).__setitem__(key, value)

class debugger(object):
    
    def __init__(self, defname = None, debug = None, FILENAME = None, **kwargs):
        global DEBUG
        super(debugger, self)
        # print(f'os.getenv("DEBUG") [00]: {os.getenv("DEBUG")}')
        # print(f'debug [00]: {debug}')
        # print(f'DEBUG [00]: {DEBUG}')
        # DEBUG = debug or DEBUG
        self.FILENAME = FILENAME or os.getenv("DEBUG_FILENAME")
    
    @classmethod    
    def create_db(self, username = None, password = None, hostname = None, dbname = None, dbtype = None):
        if USE_SQL:
            username = username or CONFIG.get_config('postgres', 'username') or 'debug_admin'
            password = password or CONFIG.get_config('postgres', 'password') or 'Xxxnuxer13'
            hostname = hostname or CONFIG.get_config('postgres', 'hostname') or '127.0.0.1'
            dbname = dbname or CONFIG.get_config('postgres', 'dbname') or 'pydebugger'
            dbtype = dbtype or CONFIG.get_config('database', 'dbtype') or 'postgresql'
            
            password_encoded = quote_plus(password)
            
            #engine_config = f'{dbtype}://{username}:{password_encoded}@{hostname}/{dbname}'
            engine_config ="{0}://{1}:{2}@{3}/{4}".format(
                dbtype,
                username,
                password_encoded,
                hostname,
                dbname
            )            

            engine = create_engine(engine_config, echo=CONFIG.get_config('logging', 'verbose', 'False'))
            
            while 1:
                try:
                    Base.metadata.create_all(engine)
                    break
                except:
                    pass
        
            Session = sessionmaker(bind=engine)
            session = Session()
            
            return session      

    def version(cls):
        print("version:", cls.VERSION)

    version = classmethod(version)

    @classmethod
    def check_debugger_server(self, host = '127.0.0.1', port = '50001'):
        global DEBUGGER_SERVER
        BUFFER_SIZE = CONFIG.get_config('buffer', 'size', '1024')  # Adjust as needed
        END_MARKER = '<END>'
        
        if os.getenv('DEBUG_EXTRA') == '1': print("DEBUGGER_SERVER [0]:", DEBUGGER_SERVER)
        port = port or 50001
        if os.getenv('DEBUG_EXTRA') == '1': print("PORT:", port)
        
        if host and port:
            DEBUGGER_SERVER = [str(host) + ":" + str(port)]
            if os.getenv('DEBUG_EXTRA') == '1': print("DEBUGGER_SERVER [2]:", DEBUGGER_SERVER)
        #print("DEBUGGER_SERVER 1:", DEBUGGER_SERVER)
        DEBUGGER_SERVER = os.getenv('DEBUGGER_SERVER') or DEBUGGER_SERVER
        if os.getenv('DEBUG_EXTRA') == '1': print("DEBUGGER_SERVER [3]:", DEBUGGER_SERVER)
        DEBUGGER_SERVER = DEBUGGER_SERVER or '127.0.0.1'
        if os.getenv('DEBUG_EXTRA') == '1': print("DEBUGGER_SERVER [4]:", DEBUGGER_SERVER)
        if isinstance(DEBUGGER_SERVER, str) and not "[" in DEBUGGER_SERVER.strip()[0] and not "]" in DEBUGGER_SERVER.strip()[-1]:
            if str(DEBUGGER_SERVER).isdigit():
                DEBUGGER_SERVER = ['127.0.0.1:' + str(DEBUGGER_SERVER)]
                if os.getenv('DEBUG_EXTRA') == '1': print("DEBUGGER_SERVER [5]:", DEBUGGER_SERVER)
            elif not ":" in DEBUGGER_SERVER:
                DEBUGGER_SERVER = [str(DEBUGGER_SERVER) + ":" + str(port)]
                if os.getenv('DEBUG_EXTRA') == '1': print("DEBUGGER_SERVER [5]:", DEBUGGER_SERVER)
            elif str(DEBUGGER_SERVER).strip()[0] == ":":
                DEBUGGER_SERVER = ['127.0.0.1' + str(DEBUGGER_SERVER).strip()]
                if os.getenv('DEBUG_EXTRA') == '1': print("DEBUGGER_SERVER [6]:", DEBUGGER_SERVER)
        if os.getenv('DEBUG_EXTRA') == '1': print("DEBUGGER_SERVER [8]:", DEBUGGER_SERVER)
        return DEBUGGER_SERVER
        
    @classmethod
    def debug_server_client(self, msg, host = None, port = None):
        #client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP
        debugger_server = DEBUGGER_SERVER
        if host and port: debugger_server = [f"{host}:{port}"]
            
        total_sent = 0
        
        def send_message(message, client_socket, host, port):
            total_sent = 0
            while total_sent < len(message):
                BUFFER_SIZE = CONFIG.get_config('buffer', 'size', '1024')  # Adjust as needed
                END_MARKER = '<END>'                
                #print(f'total_sent: {total_sent}, type(total_sent): {type(total_sent)}')
                #print(f'BUFFER_SIZE: {BUFFER_SIZE}, type(BUFFER_SIZE): {type(BUFFER_SIZE)}')
                if isinstance(BUFFER_SIZE, list):
                    BUFFER_SIZE = 1024
                chunk = message[total_sent:total_sent + BUFFER_SIZE]
                if not hasattr(chunk, 'decode'):
                    #client_socket.sendall(chunk.encode())
                    client_socket.sendto(chunk.encode(), (host, port))  # UDP
                else:
                    #client_socket.sendall(chunk)
                    client_socket.sendto(chunk, (host, port))  # UDP
                total_sent += BUFFER_SIZE
            #client_socket.sendall(END_MARKER.encode())  # TCP Send end marker to indicate end of message
            client_socket.sendto(END_MARKER.encode(), (host, port))  # UDP
        
        for i in debugger_server:
            if ":" in i:
                host, port = str(i).strip().split(":")
                port = int(port.strip() or DEBUG_PORT)
                host = host.strip() if host else '127.0.0.1'
            else:
                if str(i).isdigit():
                    host = '127.0.0.1'
                    port = int(i)
                else:
                    host = i.strip()
                    port = port or 50001
                    
            if host == '0.0.0.0': host = '127.0.0.1'
            
            if os.getenv('DEBUG_EXTRA') == '1': print("server_host:", host)
            if os.getenv('DEBUG_EXTRA') == '1': print("port:", port)
            
            #client_socket.connect((server_host, port)) #TCP
            
            try:
                if not hasattr(msg, 'decode'):
                    send_message(bytes(msg.encode('utf-8')), client_socket, host, port)
                else:
                    send_message(msg, client_socket, host, port)
            except:
                print(traceback.format_exc())
    
        client_socket.close()        
        
    @classmethod
    def setDebug(self, debug):
        DEBUG = debug

    @classmethod
    def get_len(self, objects):
        if isinstance(objects, list) or isinstance(objects, tuple) or isinstance(objects, dict):
            return len(objects)
        else:
            if sys.platform == 'win32':
                if sys.version_info.major == 2:
                    return len(bytes(objects, encoding = 'utf-8'))
                else:
                    return len(str(objects))
            else:
                return len(str(objects))
        return 0

    @classmethod
    def track(self, check = False):
        if not check and CONFIG.get_config('DEBUG', 'debug') == 1 or os.getenv('DEBUG') or os.getenv('DEBUG_SERVER'):
            traceback.format_exc()
        elif CONFIG.get_config('DEBUG', 'debug') == 1:
            return True
        return False

    @classmethod
    def colored(self, strings, fore, back = None, with_colorama = False, attrs = []):
        if CONFIG.get_config('COLORS', 'colorama') == 1 or os.getenv('colorama') == 1 or with_colorama:
            if back:
                return fore + strings + back
            else:
                return fore + strings
        else:
            return make_colors(strings, fore, back, attrs)

    @classmethod
    def insert_db(self, message, username=None, password=None, hostname=None, dbname=None, tag = 'debug'):
        tag = os.getenv('DEBUG_TAG') or os.getenv('DEBUG_APP') or CONFIG.get_config('DEBUG', 'tag') or CONFIG.get_config('app', 'name') or tag or 'debug'
        if USE_SQL:
            session = self.create_db()
            try:
                session = self.create_db()
                new_data = DebugDB(message=message, tag = tag)
                session.add(new_data)
                session.commit()
                session.close()
                return True
            except:
                if os.getenv('DEBUG') == '1':
                    print(traceback.format_exc())
                return False
    
    @classmethod
    def printlist(self, defname = None, debug = None, host = None, port = None, FILENAME = '', linenumbers = '', print_function_parameters = False, source = False, **kwargs):
        
        # print(f"KWARGS: {kwargs}")
        
        # print(f'os.getenv("DEBUG") [0]: {os.getenv("DEBUG")}')
        # print(f'debug [0]: {debug}')
        # print(f'DEBUG [0]: {DEBUG}')
        
        force = os.getenv('MAKE_COLORS_FORCE') or CONFIG.get_config('make_colors', 'force') == 1 or CONFIG.get_config('make_colors', 'force') == True
        
        cls = False
        formatlist = ''
        if DEBUG_SERVER: debug_server = True
        
        FILENAME = FILENAME

        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)

        debug = debug or DEBUG
        color_random_1 = ['lightgreen', 'lightyellow', 'lightwhite', 'lightcyan', 'lightmagenta']
        
        arrow = make_colors(' -> ', 'lg')
            
        if print_function_parameters:
            for i in args:
                if i == 'self':
                    pass
                else:
                    try:
                        if sys.platform == 'win32':
                            formatlist = make_colors((str(i) + ": "), 'lw', 'bl') + make_colors(str(values[i]), color_random_1[int(args.index(i))]) + arrow
                        else:
                            formatlist = termcolor.colored((str(i) + ": "), 'lw', 'bl') + color_random_1[int(args.index(i))] + str(values[i]) + arrow
                    except:
                        formatlist = str(i) + ": " + str(values[i]) + arrow
                    if not defname:
                        defname = str(inspect.stack()[1][3])
                    FILENAME = FILENAME or sys.argv[0]
                    linenumbers = str(inspect.stack()[1][2])
                    try:
                        if sys.platform == 'win32':
                            formatlist = make_colors(datetime.datetime.strftime(datetime.datetime.now(), '%Y:%m:%d~%H:%M:%S:%f'), 'white') + " " + make_colors(defname + arrow, 'lw', 'lr') + formatlist + " " + "[" + str(FILENAME) + "]" + " " + " [" + make_colors(str(linenumbers), 'lw', 'lc') + "] "
                        else:
                            formatlist = termcolor.colored(datetime.datetime.strftime(datetime.datetime.now(), '%Y:%m:%d~%H:%M:%S:%f'), 'white') + " " + termcolor.colored(defname + arrow, 'lw', 'lr') + formatlist + " " + "[" + str(FILENAME) + "]" + " "  + " [" + termcolor.colored(str(linenumbers), 'lw', 'lc') + "] "
                    except:
                        formatlist = datetime.datetime.strftime(datetime.datetime.now(), '%Y:%m:%d~%H:%M:%S:%f') + " " + defname + arrow + formatlist + " " + "[" + str(FILENAME) + "]" + " " + " [" + str(linenumbers) + "] "
                    if debug:
                        print(formatlist)
                    if DEBUG_SERVER:
                        self.debug_server_client(formatlist)            
            return formatlist
        
        if kwargs:
            for i in kwargs:
                if sys.version_info.major == 2: i = i.encode('utf-8')
                if str(i)in ["cls", "clear"]: cls = True                
                try:
                    if kwargs.get(i) == '' or kwargs.get(i) == None:
                        formatlist += make_colors((str(i)), 'lw', 'bl') + arrow
                    else:
                        if sys.version_info.major == 2:
                            formatlist += make_colors(str(i) + ": ", 'b', 'ly') + make_colors(bytes(kwargs.get(i), encoding='utf-8'), 'lc') + arrow + make_colors("TYPE:", 'b', 'ly') + make_colors(str(type(kwargs.get(i))), 'b', 'lc') + arrow + make_colors("LEN:", 'lw', 'lm') + make_colors(str(self.get_len(kwargs.get(i))), 'lightmagenta') + arrow 
                        else:
                            formatlist += make_colors((str(i) + ": "), 'b', 'ly') + make_colors(str(kwargs.get(i)), 'lc') + arrow + make_colors("TYPE:", 'b', 'ly') + make_colors(str(type(kwargs.get(i))), 'b', 'lc') + arrow + make_colors("LEN:", 'lw', 'lm') + make_colors(str(self.get_len(kwargs.get(i))), 'lightmagenta') + arrow
                except:
                    if os.getenv('DEBUG'):
                        traceback.format_exc()
                    if os.getenv('DEBUG_ERROR'):
                        try:
                            self.debug_server_client(traceback.format_exc(print_msg=False))
                        except:
                            print("Send traceback ERROR [290]")

                    try:
                        if kwargs.get(i) == '' or kwargs.get(i) == None:
                            formatlist += str(i).encode('utf-8') + arrow
                        else:
                            formatlist += str(i) + ": " + str(kwargs.get(i)) + arrow
                    except:
                        if os.getenv('DEBUG_ERROR'):
                            try:
                                self.debug_server_client(traceback.format_exc(print_msg=False))
                            except:
                                print("Send traceback ERROR [290]")
        else:
            try:
                formatlist += " " + make_colors("start ... ", random.choice(color_random_1)) + arrow
            except:
                try:
                    formatlist += " start... " + arrow
                except:
                    formatlist += " start... " + ' -> '

        formatlist = formatlist[:-4]
        defname_parent = ''
        defname_parent1 = ''
        the_class = ''
        
        if defname and isinstance(defname, str):
            if not FILENAME:
                #frame = inspect.stack()[1]
                #module = inspect.getmodule(frame[0])
                #filename = module.__file__
                #filename = inspect.stack()[2][3]
                FILENAME = sys.argv[0]
            #defname = defname + " [" + str(inspect.stack()[0][2]) + "] "

            FILENAME = make_colors(FILENAME, 'lightgreen')

            try:
                formatlist = make_colors(datetime.datetime.strftime(datetime.datetime.now(), '%Y:%m:%d~%H:%M:%S:%f'), 'lw') + " " + make_colors(defname + arrow, 'lw', 'r') + formatlist + " " + "[" + str(FILENAME) + "]" + " "  + make_colors("[", "cyan") + make_colors(str(linenumbers)[2:-2], 'lw', 'lc') + make_colors("]", "lc") + " " + make_colors("PID:", 'red', 'lg') + make_colors(str(PID), 'lw')
            except:
                formatlist = datetime.datetime.strftime(datetime.datetime.now(), '%Y:%m:%d~%H:%M:%S:%f') + " " + defname + arrow + formatlist + " " + "[" + str(FILENAME) + "]" + " "  + "[" + str(linenumbers)[2:-2] + "]"
        else:
            defname = str(inspect.stack()[2][3])
            if defname == "<module>": defname = sys.argv[0]
            try:
                the_class = re.split(f"'|>|<|\\.", str(inspect.stack()[1][0].f_locals.get('self').__class__))[-3]
            except:
                pass
            
            if len(inspect.stack()) > 2:
                for h in inspect.stack()[3:]:
                    if isinstance(h[2], int):
                        if not h[3] == '<module>':
                            defname_parent1 += "[%s]" % (h[3]) + arrow
                            defname_parent += "%s" % (make_colors(h[3], 'lc')) + "[%s]" % (make_colors(str(h[2]), 'lightwhite', 'lightred')) + arrow
                #defname_parent = inspect.stack()[1][3]
            if the_class and not the_class == "NoneType":

                defname_parent += "(%s)" % (make_colors(the_class, 'lightwhite', 'blue')) + arrow
                defname_parent1 += "(%s)" % (the_class) + arrow
            
            if not linenumbers:
                try:
                    #line_number =  " [" + make_colors(str(inspect.stack()[1][2]), 'white', 'on_cyan') + "] " + " " + make_colors("PID:", 'red', 'lightgreen') + make_colors(str(PID), 'lightwhite')
                    line_number = " " + make_colors("PID:", 'red', 'lightgreen') + make_colors(str(PID), 'lightwhite')
                except:
                    self.track()
                    line_number =  " [" + str(inspect.stack()[1][2]) + "] "
            else:
                linenumbers = str(linenumbers).strip()
                line_number = linenumbers + " " + make_colors("PID:", 'r', 'lg') + make_colors(str(PID), 'lw')
                linenumbers = " [" + make_colors(str(linenumbers)[1:], 'r', 'lw') + " " + make_colors("PID:", 'r', 'lg') + make_colors(str(PID), 'lw')
            FILENAME = FILENAME or sys.argv[0]
            try:
                formatlist = make_colors(datetime.datetime.strftime(datetime.datetime.now(), '%Y:%m:%d~%H:%M:%S:%f'), 'b', 'lc') + " " + make_colors(defname, 'lw', 'lr') + make_colors(arrow, 'lr') + defname_parent + formatlist + "[" + make_colors(defname + ":", 'lw', 'lr') + make_colors(str(FILENAME) + "]", 'lg') + " " + line_number
            except:
                self.track()
                formatlist = datetime.datetime.strftime(datetime.datetime.now(), '%Y:%m:%d~%H:%M:%S:%f') + " " + defname + arrow + defname_parent1 + formatlist + "[" + str(FILENAME) + "] [" + str(inspect.stack()[1][2]) + "] "  + line_number
                
        #print('os.getenv("DEBUG")     =', os.getenv("DEBUG"))
        #print('DEBUG                  =', DEBUG)
        #print('self.track(True)       =', self.track(True))

        if self.track(True):
            try:
                if os.getenv("DEBUG") == '1' or debug or DEBUG == '1' or DEBUG == True or DEBUG == 1:
                    print(formatlist)
                    if source:
                        # call get_source
                        frame_globals = inspect.stack()[2][0].f_globals
                        if defname in frame_globals and inspect.isfunction(frame_globals[defname]):
                            get_source(frame_globals[defname])
                        # else:
                            # print("Source not found for defname:", defname)
                        
                    
            except:
                pass
        else:
            if (os.getenv('DEBUG') and os.getenv('DEBUG') in [1, '1', 'true', 'True']) or debug:
                # print(f'os.getenv("DEBUG"): {os.getenv("DEBUG")}')
                # print(f'debug: {debug}')
                # print(f'DEBUG: {DEBUG}')
                
                try:
                    if not formatlist == 'cls':
                        if sys.version_info.major == 2:
                            print(formatlist.encode('utf-8'))
                        else:
                            print(formatlist)
                        if source:
                            # call get_source
                            frame_globals = inspect.stack()[2][0].f_globals
                            if defname in frame_globals and inspect.isfunction(frame_globals[defname]):
                                get_source(frame_globals[defname])
                            # else:
                                # print("Source not found for defname:", defname)
                            
                        
                except:
                    print("TRACEBACK =", traceback.format_exc())
            
        # print("DEBUG_SERVER [0]:", DEBUG_SERVER)
        if (os.getenv('DEBUG_SERVER') and os.getenv('DEBUG_SERVER') in [1, '1', 'true', 'True']) or DEBUG_SERVER:# or debug:
            # self.debug_server_client(formatlist + " [%s] [%s]" % (make_colors(ATTR_NAME, 'white', 'on_blue'), PID))
            if cls: formatlist = 'cls'
            
            # print(f"host: {host}")
            # print(f"port: {port}")
            self.debug_server_client(formatlist, host, port)
        
        cls = False
        #if debug_server:
            #self.debug_server_client(formatlist)
        
        return formatlist

    @classmethod
    def db_log(self, tag = None):
        session = self.create_db()
        last_id_first = None
        if tag == None:
            tag = ''
        tag = tag.strip()
        try:
            if tag:
                last_id_first = session.query(DebugDB.id).filter(DebugDB.tag == tag).order_by(DebugDB.id.desc()).first()[0]
            else:
                last_id_first = session.query(DebugDB.id).order_by(DebugDB.id.desc()).first()[0]
        except:
            pass
        try:
            while 1:
                if last_id_first:
                    if tag:
                        data = session.query(DebugDB).filter(DebugDB.tag == tag).order_by(DebugDB.id.desc()).first()
                    else:
                        data = session.query(DebugDB).order_by(DebugDB.id.desc()).first()
                    last_id = data.id
                    if not last_id == last_id_first:
                        #data = ActivityLog.objects.filter(id__range=(last_id_first, last_id)).order_by('id')[:obj.count()]
                        # Query the data using SQLAlchemy
                        if tag:
                            query = session.query(DebugDB).filter(DebugDB.id > last_id_first, DebugDB.id <= last_id, DebugDB.tag == tag).order_by(DebugDB.id)
                        else:
                            query = session.query(DebugDB).filter(DebugDB.id > last_id_first, DebugDB.id <= last_id).order_by(DebugDB.id)
                        
                        # Retrieve the count using SQLAlchemy's count method
                        count = query.count()
                        
                        # Specify the limit for the number of results
                        limit = count  # Retrieve all rows within the specified range
                        
                        # Apply the limit to the query
                        query = query.limit(limit)
                        
                        # Execute the query to get the results
                        data = query.all()
                        
                        data = query.all()
                        last_id_first = last_id
                        for i in data:
                            message = i.message
                            if hasattr(message, 'decode'): message = message.decode('utf-8')
                            print(message + " " + make_colors(i.tag, 'm', 'lw'))
                time.sleep(0.5)
                    
        except KeyboardInterrupt:
            sys.exit(0)
            
def debug(defname = None, debug = None, host = None, port = None, line_number = None, tag = 'debug', print_function_parameters = False, source = False, **kwargs):
    # print(f'os.getenv("DEBUG") [YY]: {os.getenv("DEBUG")}')
    # print(f'debug [YY]: {debug}')
    # print(f'DEBUG [YY]: {DEBUG}')
    # global DEBUG
    # global DEBUG_SERVER
    # global DEBUGGER_SERVER
    # print("debug:", debug)
    # print("os.getenv('DEBUG'):", os.getenv('DEBUG'))
    # print("os.getenv('DEBUG_SERVER'):", os.getenv('DEBUG_SERVER'))
    # print("os.getenv('DEBUGGER_SERVER'):", os.getenv('DEBUGGER_SERVER'))
    
    # print("DEBUG:", DEBUG)
    # print("DEBUG_SERVER:", DEBUG_SERVER)
    # print("DEBUGGER_SERVER:", DEBUGGER_SERVER)
    
    # kwargs.update({'host':host})
    # kwargs.update({'port':port})
    
    # print(f"KWARGS [1]: {kwargs}")
    
    if not debug and not DEBUG and not os.getenv('DEBUG') and not os.getenv('DEBUG_SERVER') and not DEBUG_SERVER:
        return None
    
    tag = os.getenv('DEBUG_TAG') or os.getenv('DEBUG_APP') or CONFIG.get_config('DEBUG', 'tag') or CONFIG.get_config('app', 'name') or tag or 'debug'
    
    #if not defname:
        #print "inspect.stack =", inspect.stack()[1][2]
    #    defname = inspect.stack()[1][3]
    #print("inspect.stack() =", inspect.stack())
    #print("inspect.stack()[1][2] =", inspect.stack()[1][2])
    #print("inspect.stack()[1][2] =", type(inspect.stack()[1][2]))
    #print("line_number =", line_number)
    #defname = str(inspect.stack()[1][3]) + " [" + str(inspect.stack()[1][2]) + "] "
    #if any('debug' in i.lower() for i in  os.environ):
    #print("debug: ", debug)
    #print("DEBUG: ", DEBUG)
    #print("check_debug() :", check_debug())
    
    line_number =  " [" + make_colors(str(inspect.stack()[1][2]), 'red', 'lightwhite') + "] "
    msg = ''
        
    if (os.getenv('DEBUG') and os.getenv('DEBUG') in [1, '1', 'true', 'True']) or debug or (os.getenv('DEBUG_SERVER') and os.getenv('DEBUG_SERVER') in [1, '1', 'true', 'True']) or DEBUG_SERVER:
        # print(f'os.getenv("DEBUG") [ZZ]: {os.getenv("DEBUG")}')
        # print(f'debug [ZZ]: {debug}')
        # print(f'DEBUG [ZZ]: {DEBUG}')
        
        c = debugger(defname, debug)
        msg = c.printlist(defname, debug, host, port, linenumbers = line_number, print_function_parameters= print_function_parameters, source = source, **kwargs)
    
    if CONFIG.get_config('database', 'active') == 1 or CONFIG.get_config('database', 'active') == True:
        if not msg:
            c = debugger(defname, debug)
            msg = c.printlist(defname, debug, linenumbers = line_number, print_function_parameters= print_function_parameters, **kwargs)        
        c.insert_db(msg, tag)
    
    return msg

def debug1(*args, **kwargs):
    return debug(*args, **kwargs)

def debug2(defname = None, debug = None, host = None, port = None, line_number = None, tag = 'debug', print_function_parameters = False, source = False, **kwargs):
    global DEBUGGER_SERVER2
    # print(f"DEBUGGER_SERVER: {DEBUGGER_SERVER}")
    sig = inspect.signature(debug1)
    bound_args = sig.bind_partial(defname, debug, host, port, line_number, tag, print_function_parameters, **kwargs)
    _debug_ = bound_args.arguments.get('debug', None) or kwargs.get('debug') or DEBUG or '0'
    host = CONFIG.get_config('debug2', 'host') or kwargs.get('host') or os.getenv('DEBUG2_HOST') or DEBUG_HOST2 or DEBUGGER_SERVER[0].split(":")[0] or DEBUG_HOST or '127.0.0.1'
    port = CONFIG.get_config('debug2', 'port') or kwargs.get('port') or os.getenv('DEBUG2_PORT') or DEBUG_PORT2 or DEBUGGER_SERVER[0].split(":")[1] or DEBUG_PORT or 50001
    
    # print(f"DEBUG_HOST2: {DEBUG_HOST2}")
    # print(f"host2 [1]: {host}")
    # print(f"port2 [1]: {port}")

    if DEBUGGER_SERVER2 and isinstance(DEBUGGER_SERVER2, list):
        for item in DEBUGGER_SERVER2:
            if ":" in item:
                host, port = item.split(":")
                host = host or host
                port = int(port or port)
            
    if os.getenv('DEBUGGER_SERVER2'):
        env_val = os.getenv('DEBUGGER_SERVER2').strip()
        if ";" in env_val or "," in env_val:
            sep = ";" if ";" in env_val else ","
            items = [item.strip() for item in env_val.split(sep) if item.strip()]
            DEBUGGER_SERVER2 = []
            for item in items:
                if ":" in item:
                    host, port = item.split(":")
                    host = host or host
                    port = int(port or port)
                    DEBUGGER_SERVER2.append(f"{host}:{port}")
                elif item.isdigit():
                    DEBUGGER_SERVER2.append(f"{host or '127.0.0.1'}:{item}")
                else:
                    DEBUGGER_SERVER2.append(item)
        elif ":" in env_val:
            host, port = env_val.split(":")
            host = host or host
            port = int(port or port)
            DEBUGGER_SERVER2 = [f"{host}:{port}"]
        elif env_val.isdigit():
            DEBUGGER_SERVER2 = [f"{host or '127.0.0.1'}:{env_val}"]
        else:
            DEBUGGER_SERVER2 = [env_val]
    if (DEBUG_HOST2 or DEBUG_PORT2) and not DEBUGGER_SERVER2:
        DEBUGGER_SERVER2 = [f"{DEBUG_HOST2}:{DEBUG_PORT2}"]
    
    # print(f"host2 [2]: {host}")
    # print(f"port2 [2]: {port}")
    # print(f"kwargs [2]: {kwargs}")
    # print(f"_debug_: {_debug_}")
    # print(f"DEBUG_SERVER: {DEBUG_SERVER}")
    # print(f"DEBUGGER_SERVER3: {DEBUGGER_SERVER3}")
    
    if (str(_debug_).isdigit() and str(_debug_) == '2') or DEBUG_SERVER:
        for ds in DEBUGGER_SERVER2:
            if ":" in ds:
                host, port = ds.split(":")
                host = host or host
                port = int(port or port)
            elif str(ds).isdigit():
                host = DEBUG_HOST2 or '127.0.0.1'
                port = int(ds)
            else:
                host = ds.strip()
            
            # print(f"host2 [2]: {host}")
            # print(f"port2 [2]: {port}")
            
            debug1(defname, debug, host, port, line_number, tag, print_function_parameters, **kwargs)        
        # return debug1(defname, debug, host, port, line_number, tag, print_function_parameters, **kwargs)
    return 

def debug3(defname = None, debug = None, host = None, port = None, line_number = None, tag = 'debug', print_function_parameters = False, source = False, **kwargs):
    global DEBUGGER_SERVER3
    
    sig = inspect.signature(debug1)
    bound_args = sig.bind_partial(defname, debug, host, port, line_number, tag, print_function_parameters, **kwargs)
    _debug_ = bound_args.arguments.get('debug', None) or kwargs.get('debug') or DEBUG or '0'
    
    host = CONFIG.get_config('debug3', 'host') or kwargs.get('host') or os.getenv('DEBUG3_HOST') or DEBUG_HOST3
    port = CONFIG.get_config('debug3', 'port') or kwargs.get('port') or os.getenv('DEBUG3_PORT') or DEBUG_PORT3
    
    # print(f"DEBUG_HOST3: {DEBUG_HOST3}")
    # print(f"host3 [1]: {host}")
    # print(f"port3 [1]: {port}")

    if os.getenv('DEBUGGER_SERVER3'):
        env_val = os.getenv('DEBUGGER_SERVER3').strip()
        if ";" in env_val or "," in env_val:
            sep = ";" if ";" in env_val else ","
            items = [item.strip() for item in env_val.split(sep) if item.strip()]
            DEBUGGER_SERVER3 = []
            for item in items:
                if ":" in item:
                    host, port = item.split(":")
                    host = host or host
                    port = int(port or port)
                    DEBUGGER_SERVER3.append(f"{host}:{port}")
                elif item.isdigit():
                    DEBUGGER_SERVER3.append(f"{host or '127.0.0.1'}:{item}")
                else:
                    DEBUGGER_SERVER3.append(item)
        elif ":" in env_val:
            host, port = env_val.split(":")
            host = host or host
            port = int(port or port)
            DEBUGGER_SERVER3 = [f"{host}:{port}"]
        elif env_val.isdigit():
            DEBUGGER_SERVER3 = [f"{host or '127.0.0.1'}:{env_val}"]
        else:
            DEBUGGER_SERVER3 = [env_val]
    if (DEBUG_HOST3 or DEBUG_PORT3) and not DEBUGGER_SERVER3:
        DEBUGGER_SERVER3 = [f"{DEBUG_HOST3}:{DEBUG_PORT3}"]
    
    # print(f"kwargs [3]: {kwargs}")
    # print(f"_debug_: {_debug_}")
    # print(f"DEBUG_SERVER: {DEBUG_SERVER}")
    # print(f"DEBUGGER_SERVER3: {DEBUGGER_SERVER3}")
    
    if (str(_debug_).isdigit() and str(_debug_) == '3') or DEBUG_SERVER:
        for ds in DEBUGGER_SERVER3:
            if ":" in ds:
                host, port = ds.split(":")
                host = host or host
                port = int(port or port)
            elif str(ds).isdigit():
                host = DEBUG_HOST3 or '127.0.0.1'
                port = int(ds)
            else:
                host = ds.strip()
            
            # print(f"host3 [2]: {host}")
            # print(f"port3 [2]: {port}")
            
            debug1(defname, debug, host, port, line_number, tag, print_function_parameters, **kwargs)        
        # return debug1(defname, debug, host, port, line_number, tag, print_function_parameters, **kwargs)
    return 

def make_debug_func(idx):
    def debug_func(defname=None, debug=None, host=None, port=None, line_number=None, tag='debug', print_function_parameters=False, **kwargs):
        env_name = f'DEBUGGER_SERVER{idx}'
        host_name = f'DEBUG_HOST{idx}'
        port_name = f'DEBUG_PORT{idx}'
        global_vars = globals()
        # Ambil host dan port default
        host_val = CONFIG.get_config(f'debug{idx}', 'host') or kwargs.get('host') or os.getenv(f'DEBUG{idx}_HOST') or global_vars.get(host_name, '127.0.0.1')
        port_val = CONFIG.get_config(f'debug{idx}', 'port') or kwargs.get('port') or os.getenv(f'DEBUG{idx}_PORT') or global_vars.get(port_name, 50000 + idx)
        # Ambil server list dari env
        server_list = []
        env_val = os.getenv(env_name)
        if env_val:
            env_val = env_val.strip()
            if ";" in env_val or "," in env_val:
                sep = ";" if ";" in env_val else ","
                items = [item.strip() for item in env_val.split(sep) if item.strip()]
                for item in items:
                    if ":" in item:
                        h, p = item.split(":")
                        h = h or host_val
                        p = int(p or port_val)
                        server_list.append(f"{h}:{p}")
                    elif item.isdigit():
                        server_list.append(f"{host_val}:{item}")
                    else:
                        server_list.append(item)
            elif ":" in env_val:
                h, p = env_val.split(":")
                h = h or host_val
                p = int(p or port_val)
                server_list = [f"{h}:{p}"]
            elif env_val.isdigit():
                server_list = [f"{host_val}:{env_val}"]
            else:
                server_list = [env_val]
        else:
            server_list = [f"{host_val}:{port_val}"]

        # Cek trigger debug
        _debug_ = kwargs.get('debug') or debug or DEBUG or '0'
        if (str(_debug_).isdigit() and str(_debug_) == str(idx)) or DEBUG_SERVER:
            for ds in server_list:
                if ":" in ds:
                    h, p = ds.split(":")
                    h = h or host_val
                    p = int(p or port_val)
                elif str(ds).isdigit():
                    h = host_val
                    p = int(ds)
                else:
                    h = ds.strip()
                    p = port_val
                # print(f"host{idx}: {h}")
                # print(f"port{idx}: {p}")
                debug1(defname, debug, h, p, line_number, tag, print_function_parameters, **kwargs)
        return
    return debug_func

def version():
    """
    Get the version of the ddf module.
    Version is taken from the __version__.py file if it exists.
    The content of __version__.py should be:
    version = "0.33"
    """
    try:
        version_file = Path(__file__).parent / "__version__.py"
        if version_file.is_file():
            with open(version_file, "r") as f:
                for line in f:
                    if line.strip().startswith("version"):
                        parts = line.split("=")
                        if len(parts) == 2:
                            return parts[1].strip().strip('"').strip("'")
    except Exception as e:
        debug(error=str(e))

    return "UNKNOWN VERSION"
    
# Register the debug4 function to debug10 automatically
for i in range(4, 11):
    globals()[f'debug{i}'] = make_debug_func(i)

def handle_windows():
    global HANDLE
    if sys.platform == 'win32':
        HANDLE = ctypes.windll.user32.GetForegroundWindow()

# if not __name__ == '__main__':
#         global HANDLE
#         # import win32gui, win32con
#         if sys.platform == 'win32':
#             #kernel32 = ctypes.WinDLL('kernel32')
#             # handle = kernel32.GetStdHandle(-11)
#             # handle1 = win32gui.GetForegroundWindow()
#             handle2 = ctypes.windll.user32.GetForegroundWindow()
#             HANDLE = handle2
            
    # if len(sys.argv) > 1 and sys.argv[1].isdigit():
    #     serve(port = int(*sys.argv[1:]))
        
def usage():
    parser = argparse.ArgumentParser(
        prog='debug', 
        description= '🐍 Run debugger as server, receive debug message with default port is 50001', 
        formatter_class= CustomRichHelpFormatter
    )
    
    # === Global Command ===
    parser.add_argument('-a', '--on-top', action = 'store_true', help = 'Always On Top')
    parser.add_argument('-C', '--center', action = 'store_true', help = 'Centering window')
    parser.add_argument('-c', '--cleanup', action = 'store', help = 'CleanUp File')
    parser.add_argument('-v', '--version', action = 'store_true', help = 'Get version number')
    
    # === Subcommand: serve ===        
    subparsers = parser.add_subparsers(dest = 'COMMAND', help = 'Available subCommands')
    serve_parser = subparsers.add_parser('serve', help='Run debug message UDP server', formatter_class= CustomRichHelpFormatter)
    serve_parser.add_argument('--host', default='0.0.0.0', help='Host to bind, default: 0.0.0.0')
    serve_parser.add_argument('--port', type=int, default=50001, help='Port to bind, default: 50001')
    serve_parser.add_argument('--on-top', action='store_true', help='Always On Top')
    serve_parser.add_argument('--center', action='store_true', help='Center the window')

    # === Subcommand: log ===
    log_parser = subparsers.add_parser('log', help='Database log inspection', formatter_class= CustomRichHelpFormatter)
    log_parser.add_argument('-l', '--db-log', action = 'store_true', help = 'Get Database log')
    log_parser.add_argument('-L', '--db-log-tag', action = 'store', help = 'Filter Database log by tag')
    
    # === Subcommand: cleanup ===
    cleanup_parser = subparsers.add_parser('cleanup', help='Cleanup file', formatter_class= CustomRichHelpFormatter)
    cleanup_parser.add_argument('path', help='Path file to clean')

    # === Subcommand: version ===
    version_parser = subparsers.add_parser('version', help='Print version info')
    
    # === Subcommand: cleaner ===
    cleaner_parser = subparsers.add_parser('cleaner', help='Print version info', formatter_class= CustomRichHelpFormatter)
    cleaner_parser.add_argument(
        'path',
        help='📁 Path to directory or Python file for processing'
    )
    
    cleaner_parser.add_argument(
        '--dry-run',
        action='store_true',
        help='👁️ Preview changes without modifying files'
    )
    
    action_group = cleaner_parser.add_mutually_exclusive_group()
    action_group.add_argument(
        '-co', '--comment-out',
        action='store_true',
        help='💬 Comment out debug lines (add # in front)'
    )
    
    action_group.add_argument(
        '-ci', '--comment-in',
        action='store_true',
        help='🔓 Uncomment debug lines (remove # in front)'
    )
    
    return parser

def main():        
    handle_windows()
    
    from cleaner import DebugCleaner
    
    if len(sys.argv) == 3:
        if len(sys.argv[1].split(".")) == 4 and not str(sys.argv[1]).isdigit():
            if str(sys.argv[2]).isdigit():
                serve(sys.argv[1], int(sys.argv[2]))
            else:
                serve(sys.argv[1], 50001)
        elif len(sys.argv[2].split(".")) == 4 and not str(sys.argv[2]).isdigit():
            if str(sys.argv[1]).isdigit():
                serve(sys.argv[2], int(sys.argv[1]))
            else:
                serve(sys.argv[2], 50001)
    elif len(sys.argv) == 2:
        # print(f"str(sys.argv[1]).isdigit(): {str(sys.argv[1]).isdigit()}")
        if str(sys.argv[1]).isdigit():
            serve(port = int(sys.argv[1] or 50001))
        elif len(sys.argv[1].split(".")) == 4 and not str(sys.argv[1]).isdigit():
            serve(sys.argv[1], 50001)
    # serve(port = int(*sys.argv[1:]))
    
    parser = usage()
    
    if len(sys.argv) <= 1:
        print("\n")
        parser.print_help()
        print("\n💡 Use 'debug.py <command> --help' for more details.")
        try:
            serve()
        except KeyboardInterrupt:
            return
        except Exception as e:
            console.print(f"\n ❌ [white on red blink]ERROR:[/] [black on #FFFF00]\[run server][/]: [white on blue]{e}[/]")
            sys.exit(0)

    
    args = parser.parse_args()

    if args.command == 'cleaner':
        manager = DebugCleaner()
        python_files = manager.find_python_files(args.path)

        if not python_files:
            print("\u26a0\ufe0f No Python files found.")
            return

        action = 'clean'
        if getattr(args, 'comment_out', False):
            action = 'comment_out'
        elif getattr(args, 'comment_in', False):
            action = 'comment_in'

        results = []
        for file_path in python_files:
            result = manager.process_file(file_path, action, args.dry_run)
            results.append(result)

        manager.display_results(results, args.dry_run, action)

    elif args.command == 'serve':
        serve(args.host, args.port, args.on_top, args.center)

    elif args.command == 'log':
        if args.db_log:
            debugger.db_log()
        elif args.db_log_tag:
            debugger.db_log(args.db_log_tag)

    elif args.command == 'cleanup':
        cleanup(args.path)

    elif args.command == 'version':
        print("VERSION:", version())


    # if args.cleanup:
    #     cleanup(args.cleanup)
    # elif args.db_log:
    #     debugger.db_log()
    # elif args.db_log_tag:
    #     debugger.db_log(args.db_log_tag)
    # elif args.version:
    #     print("VERSION:", version())
    # else:
    #     try:
    #         serve(args.host, args.port, args.on_top, args.center)
    #     except KeyboardInterrupt:
    #         sys.exit()

# from cleaner import DebugCleaner

# def main():
#     parser = argparse.ArgumentParser(
#         description="Debug Framework CLI",
#         formatter_class=CustomRichHelpFormatter
#     )

#     subparsers = parser.add_subparsers(dest='command', help='Available subcommands')

#     # === Subparser untuk "cleaner" ===
#     cleaner_parser = subparsers.add_parser(
#         "cleaner",
#         help="Manage debug statements in Python files",
#         formatter_class=CustomRichHelpFormatter
#     )

#     # Ambil parser dari DebugCleaner dan merge argument-nya ke subparser cleaner
#     cleaner_args = DebugCleaner().usage()
#     for action in cleaner_args._actions:
#         if action.option_strings:
#             cleaner_parser._add_action(action)
#         elif action.dest != 'help':  # skip duplicate help
#             cleaner_parser._add_action(action)

#     # === Subparser lain bisa ditambahkan di sini, contoh:
#     # log_parser = subparsers.add_parser("log", help="View debug logs")

#     # Show help if no args
#     if len(sys.argv) <= 1:
#         parser.print_help()
#         sys.exit(0)

#     args = parser.parse_args()

#     if args.command == "cleaner":
#         # Jalankan fungsi utama dari cleaner
#         manager = DebugCleaner()
#         python_files = manager.find_python_files(args.path)

#         if not python_files:
#             print("⚠️ No Python files found.")
#             return

#         if args.comment_out:
#             action = 'comment_out'
#         elif args.comment_in:
#             action = 'comment_in'
#         else:
#             action = 'clean'

#         results = []
#         for file_path in python_files:
#             result = manager.process_file(file_path, action, args.dry_run)
#             results.append(result)

#         manager.display_results(results, args.dry_run, action)

if __name__ == '__main__':
    if sys.platform == 'win32':
        kernel32 = ctypes.WinDLL('kernel32')
        handle2 = ctypes.windll.user32.GetForegroundWindow()
        HANDLE = handle2
        console.print(f"HANDLE: [#FFFF00]{HANDLE}[/]| PID: [#00FFFF]{PID}[/]")
    else:
        print(f"PID: {PID}")
    # print("PID:", PID)
    # usage()
    main()
