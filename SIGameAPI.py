import requests
import base64
import random
from string import ascii_lowercase
from signalrcore.hub_connection_builder import HubConnectionBuilder
from signalrcore.protocol.messagepack_protocol import MessagePackHubProtocol
import time

#API_ENTRY_POINT = 'https://vladimirkhil.com/api/si'

#SERVER_ADRESS = 'https://sionline.ru/siserver/1'




LOGIN_URL = '/api/Account/LogOn'
SONLINE_URL = '/sionline?token='

USERAGENT = '{User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36}'

def message_printer(message):
    print(message[0],message[1])

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
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.token = str()
        
        self.web = WEB_API()
        self.SERVER_ADDRESS = self.web.get_servers()[0]['uri']
        self.hub_connection = None

    def get_token(self):
        ret = self.session.post(self.SERVER_ADDRESS+LOGIN_URL,data={'login':self.username,'password':self.password},headers={'User-Agent':USERAGENT})
        if ret.status_code != 200:
            raise Exception('Login Failed')
        self.token = ret.content.decode('utf-8')
        return self.token

    def token_factory(self):
        return base64.b64encode(bytes(self.username,'utf-8')).decode('utf-8')


    def online(self,message_handler=message_printer):
        self.hub_connection = HubConnectionBuilder()\
            .with_url(self.SERVER_ADDRESS+SONLINE_URL+self.token,options={
                                                                    "access_token_factory":self.token_factory
                                                                        })\
            .with_automatic_reconnect({
                "type": "raw",
                "keep_alive_interval": 10,
                "reconnect_interval": 5,
                "max_attempts": 5
                })\
            .with_hub_protocol(MessagePackHubProtocol())

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
        self.hub_connection.start()
        
        #print(1)

    def send_message(self,message):
        self.hub_connection.send("Say",[message])










if __name__ == '__main__':
    api = API('CumDump')
    api.get_token()
    api.online()
    #api.send_message('12')
    while True:
        time.sleep(1)
        #api.send_message('12')