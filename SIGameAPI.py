import requests
import base64
import random
from string import ascii_lowercase
from signalrcore.hub_connection_builder import HubConnectionBuilder
from signalrcore.protocol.messagepack_protocol import MessagePackHubProtocol
import time
import Types
import threading

#API_ENTRY_POINT = 'https://vladimirkhil.com/api/si'

#SERVER_ADRESS = 'https://sionline.ru/siserver/1'


APPLICATIONS_DBs = {}

def _register_application():
    counter = 0
    res = APPLICATIONS_DBs.get(str(counter),False)
    while res != False:
        counter += 1
        res = APPLICATIONS_DBs.get(str(counter),False)

    APPLICATIONS_DBs[str(counter)] = Types.Application_DB()
    return counter

def _unregister_application(id:int):
    to_return = APPLICATIONS_DBs[str(id)].copy()
    del APPLICATIONS_DBs[id]
    return to_return


LOGIN_URL = '/api/Account/LogOn'
SONLINE_URL = '/sionline?token='

USERAGENT = '{User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36}'

def message_printer(message):
    print(message[0],message[1])

def got_slice(message,id:int,lock):
    APPLICATIONS_DBs[str(id)].append_slice(message.result)
    lock.release()

def got_slice_without_save(message,lock):
    to_return = Types.Slice(message.result)
    lock.release()
    
    

class WEB_API:
    def __init__(self,url='https://vladimirkhil.com/api/si'):
        self.server = url

    def get_servers(self):
        ret = requests.get(self.server+'/GetGameServersUrisNew',headers = {'User-Agent':USERAGENT})
        return ret.json()

    def get_all_packages(self):
        ret = requests.get(self.server+'/Packages')
        return ret.json()

    def get_categories(self):
        ret = requests.get(self.server+'/Categories')
        return ret.json()

    def get_packages_by_category_and_restriction(self,categoryid:int,restriction:str):
        ret = requests.get(self.server+f'/Packages?categoryID={categoryid}&restriction={restriction}')
        return ret.json()

    def get_package_by_id(self,packageid:int):
        ret = requests.get(self.server+f'/Packages?packageID={packageid}')
        return ret.json()

    def get_package_by_guid(self,packageguid:str):
        ret = requests.get(self.server+f'/PackageByGuid?packageGuid={packageguid}')
        return ret.json()

    def get_packages_by_tag(self,tagID:int):
        ret = requests.get(self.server+f'/PackagesByTag?tagId={tagID}')
        return ret.json()

    def get_tags(self):
        ret = requests.get(self.server+'/Tags')
        return ret.json()





class API:
    def __init__(self,username,password=''):
        self.DB_ID = _register_application()
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.token = str()
        
        self.web = WEB_API()
        self.SERVER_ADDRESS = self.web.get_servers()[0]['uri']
        self.hub_connection = None
        self.lock = threading.Lock()

    def get_token(self):
        ret = self.session.post(self.SERVER_ADDRESS+LOGIN_URL,data={'login':self.username,'password':self.password},headers={'User-Agent':USERAGENT})
        if ret.status_code != 200:
            raise Exception('Login Failed')
        self.token = ret.content.decode('utf-8')
        return self.token

    def token_factory(self):
        return base64.b64encode(bytes(self.username,'utf-8')).decode('utf-8')


    def online(self,message_handler=message_printer):
        #handler = logging.StreamHandler()
        #handler.setLevel(logging.DEBUG)
        self.hub_connection = HubConnectionBuilder()\
            .with_url(self.SERVER_ADDRESS+SONLINE_URL+self.token,options={
                                                                    "access_token_factory":self.token_factory
                                                                        })\
            .with_automatic_reconnect({
                "type": "raw",
                "keep_alive_interval": 10,
                "reconnect_interval": 5,
                "max_attempts": 5
                })
            
            

        self.hub_connection.build()
        #self.get_token.on_message(print)
        #message = ''
        #self.hub_connection.hub.on_message(message)
        self.hub_connection.on("Say",message_handler)
        self.hub_connection.on("Leaved",print)
        self.hub_connection.on("Joined",print)
        self.hub_connection.on("GameChanged",print)
        self.hub_connection.on("GameDeleted",print)
        self.hub_connection.on("GameCreated",print)
        #self.hub_connection.on("GetGamesSlice",lambda m: got_slice(m,self.DB_ID,self.lock))
        #self.hub_connection.on_message(print)
        self.hub_connection.start()
        
        #print(1)

    def send_message(self,message):
        self.hub_connection.send("Say",[message])


    def get_games_slice(self,FromId:int):  
        self.lock.acquire()
        #if save:
        self.hub_connection.send('GetGamesSlice',[FromId],lambda m: got_slice(m,self.DB_ID,self.lock))
        
        self.lock.acquire()
        self.lock.release()
        return APPLICATIONS_DBs[str(self.DB_ID)].slices[-1]
        
        









if __name__ == '__main__':
    api = API('CumDump')
    api.get_token()
    api.online()
    #api.send_message('12')
    #data = api.get_games_slice(0)
    #print(data)
    while True:
        time.sleep(1)
        data = api.get_games_slice(0)
        print(data)
        