#-*- encoding: utf-8 -*-
#encoding: utf-8
from __future__ import print_function

import os
import time
import sys
import inspect
import random
import socket
import cmdw
import datetime
from make_colors import make_colors
try:
    import configparser
    ConfigParser = configparser
except ImportError:
    import ConfigParser
    configparser = ConfigParser
    
import re
import traceback
import ctypes
if not sys.platform == 'win32': import ctypes
from urllib.parse import quote_plus
import socket
from collections import OrderedDict
import ast, json

USE_SQL = False

try:
    from sqlalchemy import create_engine, Column, Integer, Text, text, func, TIMESTAMP #, String, Boolean, TIMESTAMP, BigInteger, Text
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
    USE_SQL = True
    Base = declarative_base()
except:
    pass

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

class configset(ConfigParser.RawConfigParser):
    def __init__(self, configfile = ''):
        ConfigParser.RawConfigParser.__init__(self)
        self.allow_no_value = True
        self.optionxform = str

        #self.cfg = ConfigParser.RawConfigParser(allow_no_value=True)
        self.path = None

        configfile = configfile or os.path.splitext(os.path.realpath(sys.argv[0]))[0] + ".ini"
        
        self.configname = configfile + ".ini"

        self.configname = configfile
        self.configname_str = configfile

        try:
            if os.path.isfile(self.configname):
                if os.getenv('SHOW_CONFIGNAME'):
                    print("CONFIGNAME:", os.path.realpath(self.configname))
        except:
            pass

        configpath = ''
        configpath = inspect.stack()[1][3]

        if os.path.isfile(configpath):
            configpath = os.path.dirname(configpath)
        else:
            configpath = os.getcwd()

        configpath = os.path.realpath(configpath)

        if not self.path:
            self.path = os.path.dirname(inspect.stack()[0][1])

        if not os.path.isfile(self.configname):
            f = open(self.configname, 'w')
            f.close()
        self.read(self.configname)
        
        if not os.path.isfile(self.configname):
            print("CONFIGNAME:", os.path.abspath(self.configname), " NOT a FILE !!!")
            sys.exit("Please Set configname before !!!")

    def configfile(self, configfile):
        self.configname = os.path.realpath(configfile)
        return self.configname

    def config_file(self, configfile):
        return self.configfile(configfile)

    def set_configfile(self, configfile):
        return self.configfile(configfile)

    def set_config_file(self, configfile):
        return self.set_configfile(configfile)

    def filename(self):
        return os.path.realpath(self.configname)

    def get_configfile(self):
        return os.path.realpath(self.configname)

    def get_config_file(self):
        return os.path.realpath(self.configname)

    def write_config(self, section, option, value='', configfile = None):
        self.configname = configfile or self.configname
        if os.path.isfile(self.configname):
            self.read(self.configname)
        else:
            print("Not a file:", self.configname)
            sys.exit("Not a file: " + self.configname)

        value = value or ''

        try:
            self.set(section, option, value)
        except ConfigParser.NoSectionError:
            self.add_section(section)
            self.set(section, option, value)
        except ConfigParser.NoOptionError:
            self.set(section, option, value)

        if sys.version_info.major == '2':
            cfg_data = open(self.configname,'wb')
        else:
            cfg_data = open(self.configname,'w')

        try:
            self.write(cfg_data)
        except:
            print(traceback.format_exc())
            #import io
            #io_data = io.BytesIO(cfg_data.read().encode('utf-8'))
            #self.write(io_data)
        cfg_data.close()

        return self.read_config(section, option)

    def write_config2(self, section, option, value='', configfile=''):
        self.configname = configfile or self.configname
        
        if os.path.isfile(self.configname):
            self.read(self.configname)
        else:
            print("Not a file:", self.configname)
            sys.exit("Not a file: " + self.configname)

        if not value == None:

            try:
                self.get(section, option)
                self.set(section, option, value)
            except ConfigParser.NoSectionError:
                return "\tNo Section Name: '%s'" %(section)
            except ConfigParser.NoOptionError:
                return "\tNo Option Name: '%s'" %(option)
            
            if sys.version_info.major == '2':
                cfg_data = open(self.configname,'wb')
            else:
                cfg_data = open(self.configname,'w')

            self.write(cfg_data)
            cfg_data.close()
            return self.read_config(section, option)
        else:
            return None

    def read_config(self, section, option, value = None):
        """
            option: section, option, value=None
        """
        
        self.read(self.configname)
        
        try:
            data = self.get(section, option)

            if value and not data:
                self.write_config(section, option, value)
        except:
            try:
                self.write_config(section, option, value)
            except:
                print ("error:", traceback.format_exc())

        return self.get(section, option)

    def read_config2(self, section, option, value = None, configfile=''): #format ['aaa','bbb','ccc','ddd']
        """
            option: section, option, filename=''
            format output: ['aaa','bbb','ccc','ddd']

        """

        return self.get_config_as_list(section, option, value)

    def read_config_as_list(self, section, option, value = None, configfile=''): #format ['aaa','bbb','ccc','ddd']
        return self.get_config_as_list(section, option, value)

    def read_config3(self, section, option, value = None, filename=''): #format result: [[aaa.bbb.ccc.ddd, eee.fff.ggg.hhh], qqq.xxx.yyy.zzz]
        """
            option: section, option, filename=''
            format output first: [[aaa.bbb.ccc.ddd, eee.fff.ggg.hhh], qqq.xxx.yyy.zzz]
            note: if not separated by comma then second output is normal

        """

        self.dict_type = MultiOrderedDict
        if filename:
            if os.path.isfile(filename):
                self.read(filename)
        else:
            self.read(self.configname)

        data = []
        cfg = self.get(section, option)

        for i in cfg:
            if "," in i:
                d1 = str(i).split(",")
                d2 = []
                for j in d1:
                    d2.append(str(j).strip())
                data.append(d2)
            else:
                data.append(i)
        self.dict_type = None
        self.read(self.configname)
        return data

    def read_config4(self, section, option, value = '', filename='', verbosity=None): #format result: [aaa.bbb.ccc.ddd, eee.fff.ggg.hhh, qqq.xxx.yyy.zzz]
        """
            option: section, option, filename=''
            format result: [aaa.bbb.ccc.ddd, eee.fff.ggg.hhh, qqq.xxx.yyy.zzz]
            note: all output would be array/tuple

        """
        self.dict_type = MultiOrderedDict
        if filename:
            if os.path.isfile(filename):
                self.read(filename)
        else:
            self.read(self.configname)
        data = []
        try:
            cfg = self.get(section, option)
            if not cfg == None:
                for i in cfg:
                    if "," in i:
                        d1 = str(i).split(",")
                        for j in d1:
                            data.append(str(j).strip())
                    else:
                        data.append(i)
                self.dict_type = None
                self.read(self.configname)
                return data
            else:
                self.dict_type = None
                self.read(self.configname)
                return None
        except:
            data = self.write_config(section, option, filename, value)
            self.dict_type = None
            self.read(self.configname)
            return data

    def read_config5(self, section, option, filename='', verbosity=None): #format result: {aaa:bbb, ccc:ddd, eee:fff, ggg:hhh, qqq:xxx, yyy:zzz}
        """
            option: section, option, filename=''
            input separate is ":" and commas example: aaa:bbb, ccc:ddd
            format result: {aaa:bbb, ccc:ddd, eee:fff, ggg:hhh, qqq:xxx, yyy:zzz}

        """
        self.dict_type = MultiOrderedDict
        if filename:
            if os.path.isfile(filename):
                self.read(filename)
        else:
            self.read(self.configname)
        data = {}

        cfg = self.get(section, option)
        for i in cfg:
            if "," in i:
                d1 = str(i).split(",")
                for j in d1:
                    d2 = str(j).split(":")
                    data.update({str(d2[0]).strip():int(str(d2[1]).strip())})
            else:
                for x in i:
                    e1 = str(x).split(":")
                    data.update({str(e1[0]).strip():int(str(e1[1]).strip())})
        self.dict_type = None
        self.read(self.configname)
        return data

    def read_config6(self, section, option, filename='', verbosity=None): #format result: {aaa:[bbb, ccc], ddd:[eee, fff], ggg:[hhh, qqq], xxx:[yyy:zzz]}
        """

            option: section, option, filename=''
            format result: {aaa:bbb, ccc:ddd, eee:fff, ggg:hhh, qqq:xxx, yyy:zzz}

        """
        self.dict_type = MultiOrderedDict
        if filename:
            if os.path.isfile(filename):
                self.read(filename)
        else:
            self.read(self.configname)
        data = {}

        cfg = self.get(section, option)
        for i in cfg:
            if ":" in i:
                d1 = str(i).split(":")
                d2 = int(str(d1[0]).strip())
                for j in d1[1]:
                    d3 = re.split("['|','|']", d1[1])
                    d4 = str(d3[1]).strip()
                    d5 = str(d3[-2]).strip()
                    data.update({d2:[d4, d5]})
            else:
                pass
        self.dict_type = None
        self.read(self.configname)
        return data

    def get_config(self, section, option, value=None):
        data = None
        if value and not isinstance(value, str):
            value = str(value)

        if not value or value == 'None':
            value = ''
        self.read(self.configname)
        try:
            data = self.read_config(section, option, value)
        except ConfigParser.NoSectionError:
            if os.getenv('DEBUG'):
                print (traceback.format_exc())
            self.write_config(section, option, value)
            data = self.read_config(section, option, value)
        except ConfigParser.NoOptionError:
            if os.getenv('DEBUG'):
                print (traceback.format_exc())
            self.write_config(section, option, value)
            data = self.read_config(section, option, value)
        except:
            if os.getenv('DEBUG'):
                print (traceback.format_exc())
        #self.read(self.configname)
        if data == 'False' or data == 'false':
            return False
        elif data == 'True' or data == 'true':
            return True
        elif str(data).isdigit():
            return int(data)
        else:
            return data

    def get_config_as_list(self, section, option, value=None):
        '''
            value (str): string comma delimiter or string tuple/list : data1, data2, datax or [data1, data2, datax] or (data1, data2, datax)
        '''
        if value and not isinstance(value, str):
            value = str(value)

        if not value:
            value = ''
        self.read(self.configname)
        try:
            data = self.read_config(section, option, value)
        except ConfigParser.NoSectionError:
            print (traceback.format_exc())
            self.write_config(section, option, value)
            data = self.read_config(section, option, value)
        except ConfigParser.NoOptionError:
            print (traceback.format_exc())
            self.write_config(section, option, value)
            data = self.read_config(section, option, value)
        except:
            print (traceback.format_exc())
        data = re.split("\n|, |,| ", data)
        data = list(filter(None, data))
        data_list = []
        dlist = []
        
        for i in data:
            
            if "[" in str(i) and "]" in str(i):
                dl = re.findall("\[.*?\]", i)
                
                if dl:
                    for x in dl:
                        
                        
                        try:
                            dlist.append(ast.literal_eval(re.sub("\[|\]", "", x)))
                        except:
                            try:
                                dlist.append(json.loads(x))
                            except Exception as e:
                                print("ERROR:", e, "list string must be containt ' or \" example: ['data1', 'data2'] ")
                                return False
                        
                        # data = re.sub(x, "", data)
                        data.remove(x)
                        
                        
            else:
                if "'" in i or '"' in i:
                    
                    x = re.sub("'|\"", "", i)
                    
                    dlist.append(x)
                    data.remove(i)
        
        for i in data:
            if i.strip() == 'False' or i.strip() == 'false':
                data_list.append(False)
            elif i.strip() == 'True' or i.strip() == 'true':
                data_list.append(True)
            elif str(i).strip().isdigit():
                data_list.append(int(i.strip()))
            else:
                  data_list.append(i.strip())
        return dlist + data_list

    def get_config2(self, section, option, value = '', filename='', verbosity=None):
        if os.path.isfile(filename):
            self.read(filename)
        else:
            filename = self.configname
            self.read(self.configname)
        try:
            data = self.read_config2(section, option, filename)
        except ConfigParser.NoSectionError:
            print (traceback.format_exc())
            self.write_config(section, option, value)
            data = self.read_config2(section, option, filename)
        except ConfigParser.NoOptionError:
            print (traceback.format_exc())
            self.write_config(section, option, value)
            data = self.read_config2(section, option, filename)
        return data

    def get_config3(self, section, option, value = '', filename='', verbosity=None):
        if os.path.isfile(filename):
            self.read(filename)
        else:
            filename = self.configname
            self.read(self.configname)
        try:
            data = self.read_config3(section, option, filename)
        except ConfigParser.NoSectionError:
            print (traceback.format_exc())
            self.write_config(section, option, value)
            data = self.read_config3(section, option, filename)
        except ConfigParser.NoOptionError:
            print (traceback.format_exc())
            self.write_config(section, option, value)
            data = self.read_config3(section, option, filename)
        return data

    def get_config4(self, section, option, value = '', filename='', verbosity=None):
        if os.path.isfile(filename):
            self.read(filename)
        else:
            filename = self.configname
            self.read(self.configname)
        try:
            data = self.read_config4(section, option, filename)
        except ConfigParser.NoSectionError:
            #print "Error 1 =", traceback.format_exc()
            self.write_config(section, option, value)
            data = self.read_config4(section, option, filename)
            #print "data 1 =", data
        except ConfigParser.NoOptionError:
            #print "Error 2 =", traceback.format_exc()
            self.write_config(section, option, value)
            data = self.read_config4(section, option, filename)
            #print "data 2 =", data
        #print "DATA =", data
        return data

    def get_config5(self, section, option, value = '', filename='', verbosity=None):
        if os.path.isfile(filename):
            self.read(filename)
        else:
            filename = self.configname
            self.read(self.configname)
        try:
            data = self.read_config5(section, option, filename)
        except ConfigParser.NoSectionError:
            print (traceback.format_exc())
            self.write_config(section, option, value)
            data = self.read_config5(section, option, filename)
        except ConfigParser.NoOptionError:
            print (traceback.format_exc())
            self.write_config(section, option, value)
            data = self.read_config5(section, option, filename)
        return data

    def get_config6(self, section, option, value = '', filename='', verbosity=None):
        if os.path.isfile(filename):
            self.read(filename)
        else:
            filename = self.configname
            self.read(self.configname)
        try:
            data = self.read_config6(section, option, filename)
        except ConfigParser.NoSectionError:
            print (traceback.format_exc())
            self.write_config(section, option, value)
            data = self.read_config6(section, option, filename)
        except ConfigParser.NoOptionError:
            print (traceback.format_exc())
            self.write_config(section, option, value)
            data = self.read_config6(section, option, filename)
        return data

    def write_all_config(self, filename='', verbosity=None):
        if os.path.isfile(filename):
            self.read(filename)
        else:
            filename = self.configname
            self.read(self.configname)

    def read_all_config(self, section=[]):
        print("CONFIGFILE:", self.configname)
        self.read(self.configname)
        dbank = []
        if section:
            for i in section:
                print("[" + i + "]")
                options = self.options(i)
                data = {}
                for o in options:
                    d = self.get(i, o)
                    print("   " + o + "=" + d)
                    data.update({o: d})
                dbank.append([i, data])
        else:
            for i in self.sections():
                #section.append(i)
                print("[" + i + "]")
                data = {}
                for x in self.options(i):
                    d = self.get(i, x)
                    print("   " + x + "=" + d)
                    data.update({x:d})
                dbank.append([i,data])
        print("\n")
        return dbank

    def read_all_section(self, filename='', section='server'):
        if os.path.isfile(filename):
            self.read(filename)
        else:
            filename = self.configname
            self.read(self.configname)

        dbank = []
        dhost = []
        for x in self.options(section):
            d = self.get(section, x)
            #data.update({x:d})
            dbank.append(d)
            if d:
                if ":" in d:
                    data = str(d).split(":")
                    host = str(data[0]).strip()
                    port = int(str(data[1]).strip())
                    dhost.append([host,  port])

        return [dhost,  dbank]

    
PID = os.getpid()
HANDLE = None
MAX_WIDTH = cmdw.getWidth()
CONFIG_NAME = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'debug.ini')
CONFIG = configset(CONFIG_NAME)
PATH = ''
if PATH: CONFIG_NAME = os.path.join(PATH, os.path.basename(CONFIG_NAME))

DEBUG = False
if DEBUG == 1 or DEBUG == '1': DEBUG = True
elif DEBUG == 0 or DEBUG == '0': DEBUG = False

if os.getenv('DEBUG') == 1 or os.getenv('DEBUG') == '1': DEBUG = True
if os.getenv('DEBUG') == 0 or os.getenv('DEBUG') == '0': DEBUG = False

if isinstance(DEBUG, str):
    if not DEBUG.isdigit():
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
    else:
        DEBUGGER_SERVER = [os.getenv('DEBUGGER_SERVER')]

FILENAME = ''
if os.getenv('DEBUG_FILENAME'): FILENAME = os.getenv('DEBUG_FILENAME')

ConfigParser = configparser

force = False

class debugger(object):

    CONFIG_NAME = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'debug.ini')
    VERSION = "x.x"
    DEBUG = DEBUG
    CONFIG = configset(CONFIG_NAME)
    FILENAME = FILENAME
    
    def __init__(self, defname = None, debug = None, filename = None, **kwargs):
        super(debugger, self)
        self.DEBUG = debug or self.DEBUG
        self.FILENAME = filename or FILENAME
    
    @classmethod    
    def create_db(self, username = None, password = None, hostname = None, dbname = None, dbtype = None):
        if USE_SQL:
            username = username or self.CONFIG.get_config('postgres', 'username') or 'debug_admin'
            password = password or self.CONFIG.get_config('postgres', 'password') or 'Xxxnuxer13'
            hostname = hostname or self.CONFIG.get_config('postgres', 'hostname') or '127.0.0.1'
            dbname = dbname or self.CONFIG.get_config('postgres', 'dbname') or 'pydebugger'
            dbtype = dbtype or self.CONFIG.get_config('database', 'dbtype') or 'postgresql'
            
            password_encoded = quote_plus(password)
            
            #engine_config = f'{dbtype}://{username}:{password_encoded}@{hostname}/{dbname}'
            engine_config = '{0}://{1}:{2}@{3}/{4}'.format(dbtype, username, password_encoded, hostname, dbname)
            engine = create_engine(engine_config, echo=self.CONFIG.get_config('logging', 'verbose', 'False'))
            
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
        print("version:", VERSION)

    version = classmethod(version)

    @classmethod
    def debug_server_client(self, msg, server_host = '127.0.0.1', port = None):
        global DEBUGGER_SERVER
        #print("PORT 1:", port)
        #print("DEBUGGER_SERVER 1:", DEBUGGER_SERVER)
        if isinstance(DEBUGGER_SERVER, list) and str(DEBUGGER_SERVER[0]).isdigit() and port:
            DEBUGGER_SERVER = [str(port)]
        else:
            port = port or 50001
        
        #print("PORT 2:", port)
        #print("DEBUGGER_SERVER 2:", DEBUGGER_SERVER)
        
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        if DEBUGGER_SERVER:
            for i in DEBUGGER_SERVER:
                if ":" in i:
                    host, port = str(i).strip().split(":")
                    port = int(port.strip())
                    host = host.strip()
                    if not host: host = '127.0.0.1'
                else:
                    if str(i).isdigit():
                        host = '127.0.0.1'
                        port = int(i)
                    else:
                        host = i.strip()
                        
                if host == '0.0.0.0': host = '127.0.0.1'
                
                try:
                    if hasattr(msg, 'decode') and sys.version_info.major == 2:
                        msg = msg.encode('utf-8')
                        s.sendto(msg, (host, port))
                    else:
                        if not hasattr(msg, 'decode'):
                            s.sendto(bytes(msg.encode('utf-8')), (host, port))
                        else:
                            s.sendto(msg, (host, port))
                #except UnicodeDecodeError:
                    #pass
                #except OSError:
                    #pass
                except:
                    print(traceback.format_exc())
                s.close()
        else:
            if self.CONFIG.get_config('DEBUGGER', 'HOST'):
                if ":" in self.CONFIG.get_config('DEBUGGER', 'HOST'):
                    host, port = str(self.CONFIG.get_config('DEBUGGER', 'HOST')).strip().split(":")
                    port = int(port.strip())
                    host = host.strip()
                else:
                    host = self.CONFIG.get_config('DEBUGGER', 'HOST').strip()
                s.sendto(msg, (host, port))
                s.close()                
    
    @classmethod
    def setDebug(self, debug):
        self.DEBUG = debug

    @classmethod
    def get_len(self, objects):
        if isinstance(objects, list) or isinstance(objects, tuple) or isinstance(objects, dict):
            return len(objects)
        else:
            if sys.platform == 'win32':
                if sys.version_info.major == 2:
                    return len(unicode(objects))
                else:
                    return len(str(objects))
            else:
                return len(str(objects))
        return 0

    @classmethod
    def track(self, check = False):
        if not check:
            if self.CONFIG.get_config('DEBUG', 'debug') == 1 or os.getenv('DEBUG') or os.getenv('DEBUG_SERVER'):
                traceback.format_exc()
        else:
            if self.CONFIG.get_config('DEBUG', 'debug') == 1: #or os.getenv('DEBUG') or os.getenv('DEBUG_SERVER'):
                return True
        return False

    @classmethod
    def colored(self, strings, fore, back = None, with_colorama = False, attrs = []):
        if self.CONFIG.get_config('COLORS', 'colorama') == 1 or os.getenv('colorama') == 1 or with_colorama:
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
    
        
    #def printlist(self, defname = None, debug = None, filename = '', linenumbers = '', print_function_parameters = False, **kwargs):    
    @classmethod
    def printlist(self, *args, **kwargs):
        
        print("args [1]   =", args)
        print("kwargs [1] =", kwargs)
        
        defname = None
        debug = None
        filename = ''
        linenumbers = ''
        
        for i in kwargs:
            if i == 'filename' and value:
                filename = kwargs.get(i)
            elif i == 'defname' and kwargs.get(i):
                defname = kwargs.get(i)
            elif i == 'debug' and kwargs.get(i):
                debug = kwargs.get(i)
            elif i == 'linenumbers' and kwargs.get(i):
                linenumbers = kwargs.get(i)
                
        if not filename: filename = self.FILENAME
        
        force = os.getenv('MAKE_COLORS_FORCE') or self.CONFIG.get_config('make_colors', 'force') == 1 or self.CONFIG.get_config('make_colors', 'force') == True
        
        cls = False
        formatlist = ''
        if DEBUG_SERVER: debug_server = True
        
        arrow = make_colors(' -> ', 'lg', force = force)
        
        caller_locals = inspect.currentframe().f_back.f_locals
        
        print("args [2] =", args)
        
        if args:
            try:
                for arg in args:
                    if isinstance(arg, str):
                        found = False
                        for name, value in caller_locals.items():
                            if name not in ['filename', 'debug', 'defname', 'linenumbers']:
                                if arg == name or (callable(value) and hasattr(value, '__name__') and value.__name__ == arg):
                                    found = True
                                    printed = True
                                    
                                    if sys.version_info.major == 2:
                                        name = name.encode('utf-8')
                                    if str(name) == "cls" or str(name) == "clear":
                                        cls = True                            
                                    
                                    if value == '' or value == None:
                                        formatlist += make_colors(str(name), 'lw', 'bl', force = force) + arrow
                                    else:
                                        if sys.version_info.major == 2:
                                            formatlist += make_colors((str(name) + ": "), 'b', 'ly', force = force) + make_colors(unicode(value), 'lc', force = force) + arrow + make_colors("TYPE:", 'b', 'ly', force = force) + make_colors(str(type(value)), 'b', 'lc', force = force) + arrow + make_colors("LEN:", 'lw', 'lm', force = force) + make_colors(str(self.get_len(value)), 'lightmagenta', force = force) + arrow 
                                        else:
                                            formatlist += make_colors((str(name) + ": "), 'b', 'ly', force = force) + make_colors(str(value), 'lc', force = force) + arrow + make_colors("TYPE:", 'b', 'ly', force = force) + make_colors(str(type(value)), 'b', 'lc', force = force) + arrow + make_colors("LEN:", 'lw', 'lm', force = force) + make_colors(str(self.get_len(value)), 'lightmagenta', force = force) + arrow
                                    break
                                
                        if not found:
                            printed = True
                            print(f"start {arg} ..........")                
                                            
                    else:
                        variables = [name for name, value in caller_locals.items() if value == arg]
                        if variables:
                            printed = True
                            for name in variables:
                                print(f"{name} [2] = {arg}")
                                
                                if sys.version_info.major == 2:
                                    name = name.encode('utf-8')
                                if str(name) == "cls" or str(name) == "clear":
                                    cls = True                            
                                
                                if arg == '' or arg == None:
                                    formatlist += make_colors(str(name), 'lw', 'bl', force = force) + arrow
                                else:
                                    if sys.version_info.major == 2:
                                        formatlist += make_colors((str(name) + ": "), 'b', 'ly', force = force) + make_colors(unicode(arg), 'lc', force = force) + arrow + make_colors("TYPE:", 'b', 'ly', force = force) + make_colors(str(type(arg)), 'b', 'lc', force = force) + arrow + make_colors("LEN:", 'lw', 'lm', force = force) + make_colors(str(self.get_len(arg)), 'lightmagenta', force = force) + arrow 
                                    else:
                                        formatlist += make_colors((str(name) + ": "), 'b', 'ly', force = force) + make_colors(str(arg), 'lc', force = force) + arrow + make_colors("TYPE:", 'b', 'ly', force = force) + make_colors(str(type(arg)), 'b', 'lc', force = force) + arrow + make_colors("LEN:", 'lw', 'lm', force = force) + make_colors(str(self.get_len(arg)), 'lightmagenta', force = force) + arrow                        
                                
                                                        
                        if value == arg:
                            print(f"{name} = {value}")
                            
                            if name not in ['filename', 'debug', 'defname', 'linenumbers']:
                                if sys.version_info.major == 2:
                                    name = name.encode('utf-8')
                                if str(name) == "cls" or str(name) == "clear":
                                    cls = True
                                    
                                try:
                                    if value == '' or value == None:
                                        formatlist += make_colors(str(name), 'lw', 'bl', force = force) + arrow
                                    else:
                                        if sys.version_info.major == 2:
                                            formatlist += make_colors((str(name) + ": "), 'b', 'ly', force = force) + make_colors(unicode(value), 'lc', force = force) + arrow + make_colors("TYPE:", 'b', 'ly', force = force) + make_colors(str(type(value)), 'b', 'lc', force = force) + arrow + make_colors("LEN:", 'lw', 'lm', force = force) + make_colors(str(self.get_len(value)), 'lightmagenta', force = force) + arrow 
                                        else:
                                            formatlist += make_colors((str(name) + ": "), 'b', 'ly', force = force) + make_colors(str(value), 'lc', force = force) + arrow + make_colors("TYPE:", 'b', 'ly', force = force) + make_colors(str(type(value)), 'b', 'lc', force = force) + arrow + make_colors("LEN:", 'lw', 'lm', force = force) + make_colors(str(self.get_len(value)), 'lightmagenta', force = force) + arrow
                                except:
                                    if os.getenv('DEBUG'):
                                        traceback.format_exc()
                                    if os.getenv('DEBUG_ERROR'):
                                        try:
                                            self.debug_server_client(traceback.format_exc(print_msg=False))
                                        except:
                                            try:
                                                self.debug_server_client(traceback.format_exc())
                                            except:
                                                print("Send traceback ERROR [290]")
                
                                    try:
                                        if value == '' or value == None:
                                            formatlist += str(name).encode('utf-8') + arrow
                                        else:
                                            formatlist += str(name) + ": " + str(value) + arrow
                                    except:
                                        if os.getenv('DEBUG_ERROR'):
                                            try:
                                                self.debug_server_client(traceback.format_exc(print_msg=False))
                                            except:
                                                try:
                                                    self.debug_server_client(traceback.format_exc())
                                                except:
                                                    print("Send traceback ERROR [290]")                        
                
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
                                                
            if not printed:
                print("No matching variables or functions found.")
               
        else:
            color_random_1 = ['lightgreen', 'lightyellow', 'lightwhite', 'lightcyan', 'lightmagenta']
            debug = debug or self.DEBUG
            try:
                formatlist += " " + make_colors("start ... ", random.choice(color_random_1), force = force) + arrow
            except:
                try:
                    formatlist += " start... " + arrow
                except:
                    formatlist += " start... " + ' -> '
                    
        
        formatlist = formatlist[:-4]
        defname_parent = ''
        defname_parent1 = ''
        the_class = ''        
                    
        #######################################################################
        #if not filename: filename = self.FILENAME

        #frame = inspect.currentframe()
        #args, _, _, values = inspect.getargvalues(frame)

        #debug = debug or self.DEBUG
        #color_random_1 = ['lightgreen', 'lightyellow', 'lightwhite', 'lightcyan', 'lightmagenta']
        
        #arrow = make_colors(' -> ', 'lg', force = force)
            
        #if print_function_parameters:
            #for i in args:
                #if i == 'self':
                    #pass
                #else:
                    #try:
                        #if sys.platform == 'win32':
                            #formatlist = make_colors((str(i) + ": "), 'lw', 'bl', force = force) + make_colors(str(values[i]), color_random_1[int(args.index(i))], force = force) + arrow
                        #else:
                            #formatlist = termcolor.colored((str(i) + ": "), 'lw', 'bl') + color_random_1[int(args.index(i))] + str(values[i]) + arrow
                    #except:
                        #formatlist = str(i) + ": " + str(values[i]) + arrow
                    #if not defname:
                        #defname = str(inspect.stack()[1][3])
                    #if filename == None:
                        #filename = sys.argv[0]
                    #linenumbers = str(inspect.stack()[1][2])
                    #try:
                        #if sys.platform == 'win32':
                            #formatlist = make_colors(datetime.datetime.strftime(datetime.datetime.now(), '%Y:%m:%d~%H:%M:%S:%f'), 'white') + " " + make_colors(defname + arrow, 'lw', 'lr') + formatlist + " " + "[" + str(filename) + "]" + " " + " [" + make_colors(str(linenumbers), 'lw', 'lc') + "] "
                        #else:
                            #formatlist = termcolor.colored(datetime.datetime.strftime(datetime.datetime.now(), '%Y:%m:%d~%H:%M:%S:%f'), 'white') + " " + termcolor.colored(defname + arrow, 'lw', 'lr') + formatlist + " " + "[" + str(filename) + "]" + " "  + " [" + termcolor.colored(str(linenumbers), 'lw', 'lc') + "] "
                    #except:
                        #formatlist = datetime.datetime.strftime(datetime.datetime.now(), '%Y:%m:%d~%H:%M:%S:%f') + " " + defname + arrow + formatlist + " " + "[" + str(filename) + "]" + " " + " [" + str(linenumbers) + "] "
                    #if debug:
                        #print(formatlist)
                    #if DEBUG_SERVER:
                        #self.debug_server_client(formatlist)            
            #return formatlist
        #if not kwargs == {}:
            #for i in kwargs:
                #if sys.version_info.major == 2:
                    #i = i.encode('utf-8')
                #if str(i) == "cls" or str(i) == "clear":
                    #cls = True                
                #try:
                    #if kwargs.get(i) == '' or kwargs.get(i) == None:
                        #formatlist += make_colors((str(i)), 'lw', 'bl', force = force) + arrow
                    #else:
                        #if sys.version_info.major == 2:
                            #formatlist += make_colors(str(i) + ": ", 'b', 'ly', force = force) + make_colors(unicode(kwargs.get(i)), 'lc', force = force) + arrow + make_colors("TYPE:", 'b', 'ly', force = force) + make_colors(str(type(kwargs.get(i))), 'b', 'lc', force = force) + arrow + make_colors("LEN:", 'lw', 'lm', force = force) + make_colors(str(self.get_len(kwargs.get(i))), 'lightmagenta', force = force) + arrow 
                        #else:
                            #formatlist += make_colors((str(i) + ": "), 'b', 'ly', force = force) + make_colors(str(kwargs.get(i)), 'lc', force = force) + arrow + make_colors("TYPE:", 'b', 'ly', force = force) + make_colors(str(type(kwargs.get(i))), 'b', 'lc', force = force) + arrow + make_colors("LEN:", 'lw', 'lm', force = force) + make_colors(str(self.get_len(kwargs.get(i))), 'lightmagenta', force = force) + arrow
                #except:
                    #if os.getenv('DEBUG'):
                        #traceback.format_exc()
                    #if os.getenv('DEBUG_ERROR'):
                        #try:
                            #self.debug_server_client(traceback.format_exc(print_msg=False))
                        #except:
                            #print("Send traceback ERROR [290]")

                    #try:
                        #if kwargs.get(i) == '' or kwargs.get(i) == None:
                            #formatlist += str(i).encode('utf-8') + arrow
                        #else:
                            #formatlist += str(i) + ": " + str(kwargs.get(i)) + arrow
                    #except:
                        #if os.getenv('DEBUG_ERROR'):
                            #try:
                                #self.debug_server_client(traceback.format_exc(print_msg=False))
                            #except:
                                #print("Send traceback ERROR [290]")
        #else:
            #try:
                #formatlist += " " + make_colors("start ... ", random.choice(color_random_1), force = force) + arrow
            #except:
                #try:
                    #formatlist += " start... " + arrow
                #except:
                    #formatlist += " start... " + ' -> '

        #formatlist = formatlist[:-4]
        #defname_parent = ''
        #defname_parent1 = ''
        #the_class = ''
        
        if defname and isinstance(defname, str):
            if not filename:
                #frame = inspect.stack()[1]
                #module = inspect.getmodule(frame[0])
                #filename = module.__file__
                #filename = inspect.stack()[2][3]
                filename = sys.argv[0]
            #defname = defname + " [" + str(inspect.stack()[0][2]) + "] "

            filename = make_colors(filename, 'lightgreen')

            try:
                formatlist = make_colors(datetime.datetime.strftime(datetime.datetime.now(), '%Y:%m:%d~%H:%M:%S:%f'), 'lw', force = force) + " " + make_colors(defname + arrow, 'lw', 'lr', force = force) + formatlist + " " + "[" + str(filename) + "]" + " "  + make_colors("[", "cyan", force = force) + make_colors(str(linenumbers)[2:-2], 'lw', 'lc', force = force) + make_colors("]", "lc", force = force) + " " + make_colors("PID:", 'red', 'lg', force = force) + make_colors(str(PID), 'lw', force = force)
            except:
                formatlist = datetime.datetime.strftime(datetime.datetime.now(), '%Y:%m:%d~%H:%M:%S:%f') + " " + defname + arrow + formatlist + " " + "[" + str(filename) + "]" + " "  + "[" + str(linenumbers)[2:-2] + "]"
        else:
            defname = str(inspect.stack()[2][3])
            if defname == "<module>":
                defname = sys.argv[0]
            try:
                the_class = re.split("'|>|<|\.", str(inspect.stack()[1][0].f_locals.get('self').__class__))[-3]
            except:
                pass
            if len(inspect.stack()) > 2:
                for h in inspect.stack()[3:]:
                    if isinstance(h[2], int):
                        if not h[3] == '<module>':
                            defname_parent1 += "[%s]" % (h[3]) + arrow
                            defname_parent += "%s" % (make_colors(h[3], 'lc', force = force)) + "[%s]" % (make_colors(str(h[2]), 'lightwhite', 'lightred', force = force)) + arrow
                #defname_parent = inspect.stack()[1][3]
            if the_class and not the_class == "NoneType":

                defname_parent += "(%s)" % (make_colors(the_class, 'lightwhite', 'blue', force = force)) + arrow
                
                defname_parent1 += "(%s)" % (the_class) + arrow
            
            if not linenumbers:
                try:
                    #line_number =  " [" + make_colors(str(inspect.stack()[1][2]), 'white', 'on_cyan') + "] " + " " + make_colors("PID:", 'red', 'lightgreen') + make_colors(str(PID), 'lightwhite')
                    line_number = make_colors("PID:", 'red', 'lightgreen', force = force) + make_colors(str(PID), 'lightwhite', force = force)
                except:
                    self.track()
                    line_number =  " [" + str(inspect.stack()[1][2]) + "] "
            else:
                linenumbers = str(linenumbers).strip()
                line_number = linenumbers + make_colors("PID:", 'r', 'lg', force = force) + make_colors(str(PID), 'lw', force = force)
                linenumbers = " [" + make_colors(str(linenumbers)[1:], 'r', 'lw', force = force) + make_colors("PID:", 'r', 'lg', force = force) + make_colors(str(PID), 'lw', force = force)
            if not filename: filename = sys.argv[0]
            try:
                formatlist = make_colors(datetime.datetime.strftime(datetime.datetime.now(), '%Y:%m:%d~%H:%M:%S:%f'), 'b', 'lc', force = force) + " " + make_colors(defname, 'lw', 'lr', force = force) + make_colors(arrow, 'lr', force = force) + defname_parent + formatlist + "[" + make_colors(defname + ":", 'lw', 'lr', force = force) + make_colors(str(filename) + "]", 'lg', force = force) + " " + line_number
            except:
                self.track()
                formatlist = datetime.datetime.strftime(datetime.datetime.now(), '%Y:%m:%d~%H:%M:%S:%f') + " " + defname + arrow + defname_parent1 + formatlist + "[" + str(filename) + "] [" + str(inspect.stack()[1][2]) + "] "  + line_number
                
        #print('os.getenv("DEBUG")     =', os.getenv("DEBUG"))
        #print('DEBUG                  =', DEBUG)
        #print('self.track(True)       =', self.track(True))

        if self.track(True):
            try:
                if os.getenv("DEBUG") == '1' or debug or DEBUG == '1' or DEBUG == True or DEBUG == 1:
                    print(formatlist)
            except:
                pass
        else:
            if os.getenv("DEBUG") == '1' or debug or DEBUG == '1' or DEBUG == True or DEBUG == 1:
                try:
                    if not formatlist == 'cls':
                        if sys.version_info.major == 2:
                            print(formatlist.encode('utf-8'))
                        else:
                            print(formatlist)
                except:
                    print("TRACEBACK =", traceback.format_exc())

        if DEBUG_SERVER or debug:
            # self.debug_server_client(formatlist + " [%s] [%s]" % (make_colors(ATTR_NAME, 'white', 'on_blue'), PID))
            if cls: formatlist = 'cls'
            
            self.debug_server_client(formatlist, port = kwargs.get('port', 50001))
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
            
def debug_server_client(msg, server_host = '127.0.0.1', port = 50001):
    if CONFIG.get_config('RECEIVER', 'HOST', CONFIG_NAME):
        RECEIVER_HOST = CONFIG.get_config('RECEIVER', 'HOST', CONFIG_NAME)
    
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

def serve(host = '0.0.0.0', port = 50001, on_top=False, center = False):
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

    print(make_colors("BIND: ", 'white', 'green', force = force) + make_colors(host, 'white', 'red', attrs= ['bold'], force = force) + ":" + make_colors(str(port), 'black', 'yellow', attrs= ['bold'], force = force))
    while 1:
        msg = s.recv(6556500)
        if msg:
            if hasattr(msg, 'decode'):
                msg = msg.decode('utf-8')
            if msg == 'cls' or msg == 'clear':
                if sys.platform == 'win32':
                    os.system('cls')
                else:
                    os.system('clear')
            else:
                #print("CONFIG.get_config('display', 'on_top') =", CONFIG.get_config('display', 'on_top'))
                #print("CONFIG.get_config('display', 'on_top') == 1 or CONFIG.get_config('display', 'on_top') == True =", CONFIG.get_config('display', 'on_top') == 1 or CONFIG.get_config('display', 'on_top') == True)
                if CONFIG.get_config('display', 'on_top') == 1 or CONFIG.get_config('display', 'on_top') == True:
                    showme()
                print(str(msg))
            if sys.platform == 'win32':
                print("=" * (MAX_WIDTH - 3))
            else:
                print("=" * ((MAX_WIDTH * 2) - 3))

def debug(defname = None, debug = None, debug_server = False, line_number = '', tag = 'debug', print_function_parameters = False, **kwargs):
    tag = os.getenv('DEBUG_TAG') or os.getenv('DEBUG_APP') or CONFIG.get_config('DEBUG', 'tag') or CONFIG.get_config('app', 'name') or tag or 'debug'
    
    #if not defname:
        #print "inspect.stack =", inspect.stack()[1][2]
    #    defname = inspect.stack()[1][3]
    #print("inspect.stack() =", inspect.stack())
    #print("inspect.stack()[1][2] =", inspect.stack()[1][2])
    #print("inspect.stack()[1][2] =", type(inspect.stack()[1][2]))
    line_number =  " [" + make_colors(str(inspect.stack()[1][2]), 'red', 'lightwhite', force = force) + "] "
    #print("line_number =", line_number)
    #defname = str(inspect.stack()[1][3]) + " [" + str(inspect.stack()[1][2]) + "] "
    c = debugger(defname, debug)
    
    msg = c.printlist(defname, debug, linenumbers = line_number, print_function_parameters= print_function_parameters, **kwargs)
    
    if CONFIG.get_config('database', 'active') == 1 or CONFIG.get_config('database', 'active') == True:
        c.insert_db(msg, tag)
    
    return msg

def set_detach(width = 700, height = 400, x = 10, y = 50, center = False, buffer_column = 9000, buffer_row = 77, on_top = True):
    if not sys.platform == 'win32':
        return False
    from dcmd import dcmd
    setting = dcmd.dcmd()
    setting.setBuffer(buffer_row, buffer_column)
    screensize = setting.getScreenSize()
    setting.setSize(width, height, screensize[0] - width, y, center)
    if on_top: setting.setAlwaysOnTop(width, height, screensize[0] - width, y, center)
    
def version():
    try:
        try:
            from . import __version__
        except:
            import __version__
        return __version__.version
    except:
        #print(traceback.format_exc())
        return "ERROR"

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
        if not re.findall('debug\(.*?\).*?\n', i):
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

def usage():
    if not __name__ == '__main__':
        global HANDLE
        # import win32gui, win32con
        if sys.platform == 'win32':
            #kernel32 = ctypes.WinDLL('kernel32')
            # handle = kernel32.GetStdHandle(-11)
            # handle1 = win32gui.GetForegroundWindow()
            handle2 = ctypes.windll.user32.GetForegroundWindow()
            HANDLE = handle2
    # print("HANDLE 3:", handle)
    # print("HANDLE 4:", handle1)
    # print("HANDLE 5:", handle2)
    import argparse
    parser = argparse.ArgumentParser(description= 'run debugger as server receive debug text default port is 50001', formatter_class= argparse.RawTextHelpFormatter)
    parser.add_argument('-b', '--host', action = 'store', help = 'Bind / listen ip address, default all network device: 0.0.0.0', default = '0.0.0.0', type = str)
    parser.add_argument('-p', '--port', action = 'store', help = 'Bind / listen port number, default is 50001', default = 50001, type = int)
    parser.add_argument('-a', '--on-top', action = 'store_true', help = 'Always On Top')
    parser.add_argument('-C', '--center', action = 'store_true', help = 'Centering window')
    parser.add_argument('-c', '--cleanup', action = 'store', help = 'CleanUp File')
    parser.add_argument('-l', '--db-log', action = 'store_true', help = 'Get the print log from Database')
    parser.add_argument('-L', '--db-log-tag', action = 'store', help = 'Get the print log from Database with Tag')
    parser.add_argument('-v', '--version', action = 'store_true', help = 'Get version number')
    if len(sys.argv) == 1:
        print("\n")
        parser.print_help()
        try:
            args = parser.parse_args()
            serve(args.host, args.port, args.on_top, args.center)
        except KeyboardInterrupt:
            sys.exit()
    else:
        args = parser.parse_args()
        if args.cleanup:
            cleanup(args.cleanup)
        elif args.db_log:
            debugger.db_log()
        elif args.db_log_tag:
            debugger.db_log(args.db_log_tag)
        elif args.version:
            print("VERSION:", version())
        else:
            try:
                serve(args.host, args.port, args.on_top, args.center)
            except KeyboardInterrupt:
                sys.exit()

if __name__ == '__main__':
    if sys.platform == 'win32':
        kernel32 = ctypes.WinDLL('kernel32')
        handle2 = ctypes.windll.user32.GetForegroundWindow()
        HANDLE = handle2
    print("PID:", PID)
    if sys.platform == 'win32':
        print("HANDLE:", HANDLE)
    usage()
