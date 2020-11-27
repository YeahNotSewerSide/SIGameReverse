

class Player:
    def __init__(self,input:dict):
        self.name = input['name']
        self.role = input['role']
        self.is_online = input['isOnline']

class Game:
    def __init__(self,input:dict):
        self.game_id = input['gameID']
        self.game_name = input['gameName']
        self.owner = input['owner']
        self.package_name = input['packageName']
        self.start_time = input['startTime']
        self.real_start_time = input['realStartTime']
        self.stage = input['stage']
        self.stage_name = input['stageName']
        self.rules = input['rules']
        self.started = input['started']
        self.mode = input['mode']
        self.language = input['language']
        self.password_required = input['passwordRequired']
        self.players = []
        for person in input['persons']:
            self.players.append(Player(person))







class Slice:
    def __init__(self,input:dict):
        self._is_last = input['isLastSlice']
        self.games = []
        for game_raw in input['data']:
            self.games.append(Game(game_raw))

    def is_last(self):
        return self._is_last



class Application_DB:
    def __init__(self):
        self.slices = []
        self.chat = []
        #self.append_slice(input)


    def append_slice(self,input):
        self.slices.append(Slice(input))



