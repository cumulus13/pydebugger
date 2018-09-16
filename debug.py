#-*- encoding: utf-8 -*-
#encoding: utf-8
from __future__ import print_function
VERSION = "X.X"
import os
import sys
import colorama
import termcolor
import inspect
import random
import socket
if sys.version_info.major == 3:
    import cmdw3 as cmdw
else:
    import cmdw
import datetime
if sys.platform == 'win32':
    from make_colors import make_colors
else:
    from make_colors_tc import make_colors
import configset
import configparser
import re
import traceback
import codecs
PID = os.getpid()

#try:
    #colorama.init(True)
#except:
    #pass
MAX_WIDTH = cmdw.getWidth()
DEBUG = False
if DEBUG == 1 or DEBUG == '1':
    DEBUG = True
elif DEBUG == 0 or DEBUG == '0':
    DEBUG = False
if os.getenv('DEBUG') == 1 or os.getenv('DEBUG') == '1':
    DEBUG = True
if os.getenv('DEBUG') == 0 or os.getenv('DEBUG') == '0':
    DEBUG = False
if isinstance(DEBUG, str):
    DEBUG = bool(DEBUG.title())
DEBUG_SERVER = os.getenv('DEBUG_SERVER')
if DEBUG_SERVER == 1 or DEBUG_SERVER == '1':
    DEBUG_SERVER = True
if DEBUG_SERVER == 0 or DEBUG_SERVER == '0':
    DEBUG_SERVER = False
if DEBUG_SERVER == "True" or DEBUG_SERVER == True:
    DEBUG_SERVER = True

DEBUGGER_SERVER = ['127.0.0.1:50001']
CONFIG_NAME = os.path.join(os.path.dirname(__file__), 'debug.ini')
try:
    cfg = configparser.RawConfigParser(allow_no_value=True)
    cfg.optionxform = str
    cfg.read = CONFIG_NAME
    try:
        cfg = cfg.get('DEBUGGER', 'HOST', value='0.0.0.0')
    except:
        try:
            cfg.set('DEBUGGER', 'HOST', '0.0.0.0')
        except configparser.NoSectionError:
            cfg.add_section('DEBUGGER')
            cfg.set('DEBUGGER', 'HOST', '0.0.0.0')
        cfg_data = open(CONFIG_NAME, 'wb')
        cfg.write(cfg_data)
        cfg_data.close()
        cfg = cfg.get('DEBUGGER', 'HOST', value='0.0.0.0')
    if ";" in cfg:
        DEBUGGER_SERVER = re.split(";", cfg)
    else:
        DEBUGGER_SERVER = [cfg]
except:
    traceback.format_exc()

if os.getenv('DEBUGGER_SERVER'):
    if ";" in os.getenv('DEBUGGER_SERVER'):
        DEBUGGER_SERVER = os.getenv('DEBUGGER_SERVER').strip().split(";")
    else:
        DEBUGGER_SERVER = [os.getenv('DEBUGGER_SERVER')]
    
#print("os.getenv('DEBUGGER_SERVER') =", os.getenv('DEBUGGER_SERVER'))
#print("DEBUGGER_SERVER =", DEBUGGER_SERVER)
FILENAME = ''
if os.getenv('DEBUG_FILENAME'):
    FILENAME = os.getenv('DEBUG_FILENAME')

#def excepthook(type, value, tb):
    #traceback.format_exc(etype = type, value = value, tb = tb)

#try:    
    #sys.excepthook = excepthook
#except:
    #traceback.format_exc()


class debugger(object):
    
    global VERSION
    global CONFIG_NAME
    
    VERSION = "x.x"
    
    def __init__(self, defname = None, debug = None, filename = None, **kwargs):
        super(debugger, self)
        self.DEBUG = debug
        self.FILENAME = filename
        self.platform = sys.platform
        if DEBUG:
            self.DEBUG = DEBUG
        if FILENAME:
            self.FILENAME = FILENAME
        #print "self.FILENAME =", self.FILENAME
        if os.getenv('DEBUG') and os.getenv('DEBUG') == 1 or os.getenv('DEBUG') and os.getenv('DEBUG') == '1' or os.getenv('DEBUG') and os.getenv('DEBUG') == True or os.getenv('DEBUG') and os.getenv('DEBUG') == "True":
            self.DEBUG = True
        self.color_random_error = False
        # self.errors_count = 1
        
    def version(cls):
        print("version:", VERSION)
        
    version = classmethod(version)
        
    def get_config_file(self, filename='', verbosity=None):
        global CONFIG_NAME
        if filename == '':
            if CONFIG_NAME != '':
                filename = CONFIG_NAME
            # else:
            #     return WindowsError('No Config file found !')
    
        if os.path.isfile(os.path.join(os.getcwd(), filename)):
            #print "FILENAME ZZZ=", f
            CONFIG_NAME = os.path.join(os.getcwd(), filename)
            if verbosity:
                print(os.path.join(os.getcwd(), filename))
            return os.path.join(os.getcwd(), filename)
        elif os.path.isfile(filename):
            CONFIG_NAME = filename
            if verbosity:
                print(os.path.abspath(CONFIG_NAME))
            return filename
        elif os.path.isfile(os.path.join(os.path.dirname(__file__), filename)):
            CONFIG_NAME = os.path.join(os.path.dirname(__file__), filename)
            if verbosity:
                print(os.path.join(os.path.dirname(__file__), filename))
            return os.path.join(os.path.dirname(__file__), filename)
        elif os.path.isfile(CONFIG_NAME):
            if verbosity:
                print(os.path.abspath(CONFIG_NAME))
            return CONFIG_NAME
        elif os.path.isfile(os.path.join(os.path.dirname(__file__), CONFIG_NAME)):
            if verbosity:
                print(os.path.join(os.path.dirname(__file__), CONFIG_NAME))
            return os.path.join(os.path.dirname(__file__), CONFIG_NAME)
        else:
            fcfg = os.path.join(os.path.dirname(__file__), CONFIG_NAME)
            f = open(fcfg, 'w')
            f.close()
            filecfg = fcfg
            if verbosity:
                print("CREATE:", os.path.abspath(filecfg))
            return filecfg
    
        
    def read_config(self, section, option, filename='', verbosity=None): #format result: [aaa.bbb.ccc.ddd, eee.fff.ggg.hhh, qqq.xxx.yyy.zzz]
        """
            option: section, option, filename=''
            format result: [aaa.bbb.ccc.ddd, eee.fff.ggg.hhh, qqq.xxx.yyy.zzz]
            
        """
        filename = get_config_file(filename, verbosity)
        data = []
        cfg = configparser.RawConfigParser(allow_no_value=True, dict_type=MultiOrderedDict) 
        cfg.read(filename)
        cfg = cfg.get(section, option)
        if not cfg == None:
            for i in cfg:
                if "," in i:
                    d1 = str(i).split(",")
                    for j in d1:
                        data.append(str(j).strip())
                else:
                    data.append(i)
            return data
        else:
            return None    
    
    def debug_server_client(self, msg, server_host = '127.0.0.1', port = 50001):
        
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        if DEBUGGER_SERVER:
            for i in DEBUGGER_SERVER:
                if ":" in i:
                    host, port = str(i).strip().split(":")
                    port = int(port.strip())
                    host = host.strip()
                else:
                    host = i.strip()
                if host == '0.0.0.0':
                    host = '127.0.0.1'
                # print ("host =", host)
                # print ("port =", port)
                # print(str(msg))
                try:
                    s.sendto(bytes(msg.encode('utf-8')), (host, port))
                except UnicodeDecodeError:
                    pass
                except:
                    traceback.format_exc()
                s.close()
        else:
            print("self.read_config('DEBUGGER', 'HOST') =", self.read_config('DEBUGGER', 'HOST'))
            if self.read_config('DEBUGGER', 'HOST'):
                if ":" in self.read_config('DEBUGGER', 'HOST'):
                    host, port = str(self.read_config('DEBUGGER', 'HOST')).strip().split(":")
                    port = int(port.strip())
                    host = host.strip()
                else:
                    host = self.read_config('DEBUGGER', 'HOST').strip()
                s.sendto(msg, (host, port))
                s.close()                
            
    def setDebug(self, debug):
        self.DEBUG = debug

    def printlist(self, defname = None, debug = None, filename = '', linenumbers = '', print_function_parameters = False, **kwargs):
        if sys.version_info.major == 2:
            if sys.stdout.encoding != 'cp850':
                sys.stdout = codecs.getwriter('utf-8')(sys.stdout, 'strict')
            if sys.stderr.encoding != 'cp850':
                sys.stderr = codecs.getwriter('utf-8')(sys.stderr, 'strict')
        if DEBUG_SERVER:
            debug_server = True

        if not filename:
            filename = self.FILENAME
        
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        
        if not debug:
            debug = self.DEBUG
        if sys.platform == 'win32':
            try:                
                #color_random_1 = [colorama.Fore.GREEN, colorama.Fore.YELLOW, colorama.Fore.LIGHTWHITE_EX, colorama.Fore.LIGHTCYAN_EX, colorama.Fore.LIGHTMAGENTA_EX, colorama.Fore.GREEN, colorama.Fore.YELLOW, colorama.Fore.LIGHTWHITE_EX, colorama.Fore.LIGHTCYAN_EX, colorama.Fore.LIGHTMAGENTA_EX, colorama.Fore.GREEN, colorama.Fore.YELLOW, colorama.Fore.LIGHTWHITE_EX, colorama.Fore.LIGHTCYAN_EX, colorama.Fore.LIGHTMAGENTA_EX, colorama.Fore.GREEN, colorama.Fore.YELLOW, colorama.Fore.LIGHTWHITE_EX, colorama.Fore.LIGHTCYAN_EX, colorama.Fore.LIGHTMAGENTA_EX, colorama.Fore.GREEN, colorama.Fore.YELLOW, colorama.Fore.LIGHTWHITE_EX, colorama.Fore.LIGHTCYAN_EX, colorama.Fore.LIGHTMAGENTA_EX, colorama.Fore.GREEN, colorama.Fore.YELLOW, colorama.Fore.LIGHTWHITE_EX, colorama.Fore.LIGHTCYAN_EX, colorama.Fore.LIGHTMAGENTA_EX]
                color_random_1 = ['green', 'yellow', 'lightwhite', 'lightcyan', 'lightmagenta']
                self.color_random_error = False
            except:
                self.color_random_error = True
                pass
        else:
            color_random_1 = [colorama.Fore.GREEN, colorama.Fore.YELLOW, colorama.Fore.WHITE, colorama.Fore.CYAN, colorama.Fore.MAGENTA, colorama.Fore.GREEN, colorama.Fore.YELLOW, colorama.Fore.WHITE, colorama.Fore.CYAN, colorama.Fore.MAGENTA, colorama.Fore.GREEN, colorama.Fore.YELLOW, colorama.Fore.WHITE, colorama.Fore.CYAN, colorama.Fore.MAGENTA, colorama.Fore.GREEN, colorama.Fore.YELLOW, colorama.Fore.WHITE, colorama.Fore.CYAN, colorama.Fore.MAGENTA, colorama.Fore.GREEN, colorama.Fore.YELLOW, colorama.Fore.WHITE, colorama.Fore.CYAN, colorama.Fore.MAGENTA, colorama.Fore.GREEN, colorama.Fore.YELLOW, colorama.Fore.WHITE, colorama.Fore.CYAN, colorama.Fore.MAGENTA]
        if not sys.platform == 'win32':
            try:
                colorama.init()
            except:
                pass
        formatlist = ''
        try:
            if self.platform == 'win32':
                arrow = make_colors(' -> ', 'yellow')
            else:
                arrow = colorama.Fore.YELLOW + ' -> '
        except:
            arrow = ' -> '
        if print_function_parameters:
            for i in args:
                if i == 'self':
                    pass
                else:
                    try:
                        if sys.platform == 'win32':
                            formatlist = make_colors((str(i) + ": "), 'white', 'on_blue') + make_colors(str(values[i]), color_random_1[int(args.index(i))]) + arrow
                        else:
                            formatlist = termcolor.colored((str(i) + ": "), 'white', 'on_blue') + color_random_1[int(args.index(i))] + str(values[i]) + arrow
                    except:
                        formatlist = str(i) + ": " + str(values[i]) + arrow
                    if not defname:
                        defname = str(inspect.stack()[1][3])
                    if filename == None:
                        filename = sys.argv[0]
                    linenumbers = str(inspect.stack()[1][2])
                    try:
                        if sys.platform == 'win32':
                            formatlist = make_colors(datetime.datetime.strftime(datetime.datetime.now(), '%Y:%m:%d~%H:%M:%S:%f'), 'white') + " " + make_colors(defname + arrow, 'white', 'on_red') + formatlist + " " + "[" + str(filename) + "]" + " [" + make_colors(str(linenumbers), 'white', 'on_cyan') + "] "
                        else:
                            formatlist = termcolor.colored(datetime.datetime.strftime(datetime.datetime.now(), '%Y:%m:%d~%H:%M:%S:%f'), 'white') + " " + termcolor.colored(defname + arrow, 'white', 'on_red') + formatlist + " " + "[" + str(filename) + "]" + " [" + termcolor.colored(str(linenumbers), 'white', 'on_cyan') + "] "
                    except:
                        formatlist = datetime.datetime.strftime(datetime.datetime.now(), '%Y:%m:%d~%H:%M:%S:%f') + " " + defname + arrow + formatlist + " " + "[" + str(filename) + "]" + " [" + str(linenumbers) + "] "
                    if debug:
                        print(formatlist)
                    if DEBUG_SERVER:
                        self.debug_server_client(formatlist)            
            return formatlist
        if not kwargs == {}:
            for i in kwargs:
                #formatlist += color_random_1[kwargs.keys().index(i)] + i + ": " + color_random_1[kwargs.keys().index(i)] + str(kwargs.get(i)) + arrow
                try:
                    if kwargs.get(i) == '' or kwargs.get(i) == None:
                        if sys.platform == 'win32':
                            formatlist += make_colors((str(i)), 'white', 'on_blue') + arrow
                        else:
                            formatlist += termcolor.colored((str(i)), 'white', 'on_blue') + arrow
                    else:
                        if sys.version_info.major == 2:
                            if sys.platform == 'win32':
                                formatlist += make_colors((str(i) + ": "), 'white', 'on_blue') + make_colors(unicode(kwargs.get(i)), 'cyan') + arrow + make_colors("TYPE:", 'black', 'lightyellow') + make_colors(str(type(kwargs.get(i))), 'lightyellow') + arrow
                            else:
                                formatlist += termcolor.colored((str(i) + ": "), 'white', 'on_blue') + termcolor.colored(unicode(kwargs.get(i)), 'blue') + arrow + termcolor.colored("TYPE:", 'black', 'on_yellow') + termcolor.colored(str(type(kwargs.get(i))), 'yellow') + arrow
                        else:
                            if sys.platform == 'win32':
                                formatlist += make_colors((str(i) + ": "), 'white', 'on_blue') + make_colors(str(kwargs.get(i)), 'cyan') + arrow + make_colors("TYPE:", 'black', 'lightyellow') + make_colors(str(type(kwargs.get(i))), 'lightyellow') + arrow
                            else:
                                formatlist += termcolor.colored((str(i) + ": "), 'white', 'on_blue') + termcolor.colored(str(kwargs.get(i)), 'blue') + arrow + termcolor.colored("TYPE:", 'black', 'on_yellow') + termcolor.colored(str(type(kwargs.get(i))), 'yellow') + arrow                        
                except:
                    # traceback.format_exc()
                    if os.getenv('DEBUG_ERROR'):
                        try:
                            self.debug_server_client(traceback.format_exc(print_msg=False))
                        except:
                            print("Send traceback ERROR [290]")

                    try:
                        if os.getenv('DEBUG_ERROR'):
                            print(termcolor.colored("DEBUGGER ERROR [001] !", 'white', 'on_red', attrs= ['bold', 'blink']))
                    except:
                        # traceback.format_exc()
                        if os.getenv('DEBUG_ERROR'):
                            try:
                                self.debug_server_client(traceback.format_exc(print_msg=False))
                            except:
                                print("Send traceback ERROR [300]")
                    try:
                        if kwargs.get(i) == '' or kwargs.get(i) == None:
                            formatlist += str(i).encode('utf-8') + arrow
                        else:
                            formatlist += str(i) + ": " + str(kwargs.get(i)) + arrow
                    # except UnicodeDecodeError:
                    #     pass
                    except:
                        if os.getenv('DEBUG_ERROR'):
                            try:
                                self.debug_server_client(traceback.format_exc(print_msg=False))
                            except:
                                print("Send traceback ERROR [316]")
        else:
            try:
                formatlist += " " + make_colors("start ... ", random.choice(color_random_1)) + arrow
            except:
                try:
                    formatlist += " start... " + arrow
                except:
                    formatlist += " start... " + ' -> '
        formatlist = formatlist[:-4]
        
        if defname:
            if filename == None:
                #frame = inspect.stack()[1]
                #module = inspect.getmodule(frame[0])
                #filename = module.__file__
                #filename = inspect.stack()[2][3]
                filename = sys.argv[0]
            #defname = defname + " [" + str(inspect.stack()[0][2]) + "] "
            filename = make_colors(filename, 'lightgreen')
            try:
                if sys.platform == 'win32':
                    formatlist = make_colors(datetime.datetime.strftime(datetime.datetime.now(), '%Y:%m:%d~%H:%M:%S:%f'), 'white') + " " + make_colors(defname + arrow, 'white', 'on_red') + formatlist + " " + "[" + str(filename) + "]" + " " + make_colors("[", "cyan") + make_colors(str(linenumbers)[2:-2], 'white', 'on_cyan') + make_colors("]", "cyan")
                else:
                    formatlist = termcolor.colored(datetime.datetime.strftime(datetime.datetime.now(), '%Y:%m:%d~%H:%M:%S:%f'), 'white') + " " + termcolor.colored(defname + arrow, 'white', 'on_red') + formatlist + " " + "[" + str(filename) + "]" + " " + termcolor.colored("[", "cyan") + termcolor.colored(str(linenumbers)[2:-2], 'white', 'on_cyan') + termcolor.colored("]", "cyan")
            except:
                formatlist = datetime.datetime.strftime(datetime.datetime.now(), '%Y:%m:%d~%H:%M:%S:%f') + " " + defname + arrow + formatlist + " " + "[" + str(filename) + "]" + " " + "[" + str(linenumbers)[2:-2] + "]"
        else:
            defname = str(inspect.stack()[1][3])
            try:
                if sys.platform == 'win32':
                    line_number =  " [" + make_colors(str(inspect.stack()[1][2]), 'white', 'on_cyan') + "] "
                else:
                    line_number =  " [" + termcolor.colored(str(inspect.stack()[1][2]), 'white', 'on_cyan') + "] "
            except:
                line_number =  " [" + str(inspect.stack()[1][2]) + "] "
            if filename == None:
                filename = sys.argv[0]
                #filename = inspect.stack()[2][3]
                #frame = inspect.stack()[1]
                #module = inspect.getmodule(frame[0])
                #filename = module.__file__
                #f = sys._current_frames().values()[0]
                #filename = f.f_back.f_globals['__file__']
            try:
                if sys.platform == 'win32':
                    formatlist = make_colors(datetime.datetime.strftime(datetime.datetime.now(), '%Y:%m:%d~%H:%M:%S:%f'), 'white') + " " + make_colors(defname + arrow, 'white', 'on_red') + formatlist + " " + "[" + str(filename) + " [" + make_colors(str(inspect.stack()[1][2]), 'white', 'on_cyan') + "] " + line_number
                else:
                    formatlist = termcolor.colored(datetime.datetime.strftime(datetime.datetime.now(), '%Y:%m:%d~%H:%M:%S:%f'), 'white') + " " + termcolor.colored(defname + arrow, 'white', 'on_red') + formatlist + " " + "[" + str(filename) + " [" + termcolor.colored(str(inspect.stack()[1][2]), 'white', 'on_cyan') + "] " + line_number
            except:
                formatlist = datetime.datetime.strftime(datetime.datetime.now(), '%Y:%m:%d~%H:%M:%S:%f') + " " + defname + arrow + formatlist + " " + "[" + str(filename) + " [" + str(inspect.stack()[1][2]) + "] " + line_number
        if debug:
            try:
                print(formatlist)
                if not sys.platform == 'win32':
                    colorama.reinit()
            except:
                pass
        if DEBUG_SERVER:
            self.debug_server_client(formatlist + " [%s]" % (PID))
        #if debug_server:
            #self.debug_server_client(formatlist)        
        return formatlist
    
def debug_server_client(msg, server_host = '127.0.0.1', port = 50001):
    global CONFIG_NAME
    try:
        if read_config('RECEIVER', 'HOST', CONFIG_NAME):
            RECEIVER_HOST = read_config('RECEIVER', 'HOST', CONFIG_NAME)
    except:
        pass
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if RECEIVER_HOST:
        for i in RECEIVER_HOST:
            if ":" in i:
                host, port = str(i).strip().split(":")
                port = int(port.strip())
                host = host.strip()
            else:
                host = i.strip()
            if host == "0.0.0.0":
                host = '127.0.0.1'
            s.sendto(msg, (host, port))
            s.close()
            
def debug_self(**kwargs):
    return debug(**kwargs)

def get_config(section, option, configname = 'debug.ini', value = ''):
    global CONFIG_NAME
    cfg = configparser.RawConfigParser(allow_no_value=True)
    cfg.optionxform = str
    
    if configname:
        configname = os.path.join(os.path.dirname(__file__), os.path.basename(configname))
    else:
        configname = CONFIG_NAME
    
    debug_self(configname = configname)    
    cfg.read(configname)
    
    try:
        data = cfg.get(section, option)
    except:
        try:
            try:
                cfg.set(section, option, value)
            #except configparser.NoSectionError:
            except:
                cfg.add_section(section)
                cfg.set(section, option, value)
            #except configparser.NoOptionError:
                #pass
            cfg_data = open(configname,'wb')
            cfg.write(cfg_data) 
            cfg_data.close()  
        except configparser.NoOptionError:
            pass
        except:
            traceback.format_exc()
        data = cfg.get(section, option)
    return data    

def serve(host = '0.0.0.0', port = 50001):
    global DEBUGGER_SERVER
    import socket
    host1 = ''
    port1 = ''
    if DEBUGGER_SERVER:
        if isinstance(DEBUGGER_SERVER, list):
            for i in DEBUGGER_SERVER:
                if ":" in i:
                    host1, port1 = str(i).split(":")
                    port1 = int(port1)
                else:
                    host1 = i
        else:
            if ":" in DEBUGGER_SERVER:
                host1, port1 = str(i).split(":")
                port1 = int(port1)
            else:
                host1 = DEBUGGER_SERVER    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if not host:
        if get_config('DEBUGGER', 'HOST', value= '0.0.0.0'):
            host = get_config('DEBUGGER', 'HOST')
        else:
            host = host1
    if not port:
        if get_config('DEBUGGER', 'PORT', value= '50001'):
            port = get_config('DEBUGGER', 'PORT')
            port = int(port)
        else:
            port = port1
    #print ("DEBUGGER_SERVER =", DEBUGGER_SERVER)
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
    while 1:
        msg = s.recv(6556500)
        if msg:
            print(msg)
            print("=" * (MAX_WIDTH - 3))

def debug(defname = None, debug = None, debug_server = False, line_number = '', print_function_parameters = False, **kwargs):
    isdebug = DEBUG
    #if DEBUG_SERVER:
        #debug_server = True
    if not defname:
        #print "inspect.stack =", inspect.stack()[1][2]
        defname = inspect.stack()[1][3]
        if sys.platform == 'win32':
            line_number =  " [" + make_colors(str(inspect.stack()[1][2]), 'white', 'on_cyan') + "] "
        else:
            line_number =  " [" + termcolor.colored(str(inspect.stack()[1][2]), 'white', 'on_cyan') + "] "
        #defname = str(inspect.stack()[1][3]) + " [" + str(inspect.stack()[1][2]) + "] "
    c = debugger(defname, debug)
    msg = c.printlist(defname, debug, linenumbers = line_number, print_function_parameters= print_function_parameters, **kwargs)
    return msg
    
    #if DEBUG_SERVER:
        #debug_server_client(msg)
    #if debug_server:
        #debug_server_client(msg)
        
def usage():
    import argparse
    parser = argparse.ArgumentParser(description= 'run debugger as server receive debug text default port is 50001', version= "1.0", formatter_class= argparse.RawTextHelpFormatter)
    parser.add_argument('-b', '--host', action = 'store', help = 'Bind / listen ip address, default all network device: 0.0.0.0', default = '0.0.0.0', type = str)
    parser.add_argument('-p', '--port', action = 'store', help = 'Bind / listen port number, default is 50001', default = 50001, type = int)
    if len(sys.argv) == 1:
        print("\n")
        parser.print_help()
        try:
            args = parser.parse_args()
            serve(args.host, args.port)
        except KeyboardInterrupt:
            sys.exit()
    else:
        try:
            args = parser.parse_args()
            serve(args.host, args.port)
        except KeyboardInterrupt:
            sys.exit()

if __name__ == '__main__':
    print("PID:", PID)
    usage()
