import random, math

class game:
    def __init__(self, script):
        self.circle = [] # ordered list of players by seat
        self.players = {} # dictionary to reference players by name
        self.day = 0
        self.active = True
        self.winner = None
        
        self.dailyActions = [[]]
        self.meta_redHerringCanMoveRule = True
        self.meta_minInfoRolesCount = 0
        self.solutions = [] # "world" class objects

        # for solving: 
        self.queuedWorlds = []
        self.executedPlayers = [] # indexed by the day when the execution happened
        self.demonKilledPlayers = [None] # indexed by the day after kill
        self.poisonsBlockingInfo = []
        self.impBluffCharNames = []


        if script in {'trouble_brewing','troublebrewing'}:
            self.characterCounts = { # (townsfolk, outsiders, minions, demons)
                5: (3,0,1,1),
                6: (3,1,1,1),
                7: (5,0,1,1),
                8: (5,1,1,1),
                9: (5,2,1,1),
                10: (7,0,2,1),
                11: (7,1,2,1),
                12: (7,2,2,1),
                13: (9,0,3,1),
                14: (9,1,3,1),
                15: (9,2,3,1)
            }
            self.combinationsWith4Types = { # used to select minions
                1: [[0],[1],[2],[3]],
                2: [[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]],
                3: [[0,1,2],[0,1,3],[0,2,3],[1,2,3]]
            }
            self.scriptCharacters = {
                'washerwoman': 'townsfolk',
                'librarian': 'townsfolk',
                'investigator': 'townsfolk',
                'chef': 'townsfolk',
                'empath': 'townsfolk',
                'fortune_teller': 'townsfolk',
                'undertaker': 'townsfolk',
                'monk': 'townsfolk',
                'ravenkeeper': 'townsfolk',
                'virgin': 'townsfolk',
                'slayer': 'townsfolk',
                'soldier': 'townsfolk',
                'mayor': 'townsfolk',
                'butler': 'outsider',
                'drunk': 'outsider',
                'recluse': 'outsider',
                'saint': 'outsider',
                'poisoner': 'minion',
                'spy': 'minion',
                'scarlet_woman': 'minion',
                'baron': 'minion',
                'imp': 'demon',
                'dead_imp': 'demon'
            }
            self.townsfolkNames = []
            self.outsiderNames = []
            self.minionNames = []
            self.infoRoles = {'washerwoman','librarian','investigator','chef','empath','fortune_teller','undertaker'}
            for role in self.scriptCharacters.keys():
                if self.scriptCharacters[role] == 'townsfolk': self.townsfolkNames.append(role)
                elif self.scriptCharacters[role] == 'outsider': self.outsiderNames.append(role)
                elif self.scriptCharacters[role] == 'minion': self.minionNames.append(role)

            self.scriptActions = {
                'slay',
                'was_nominated',
                'was_executed'
            }

            # --- FAST CHARACTER TABLES (ids + properties) ---
            # Give every character a stable small int id.
            self.char_names = list(self.scriptCharacters.keys())
            self.char_id = {}
            for i in range(len(self.char_names)):
                self.char_id[self.char_names[i]] = i

            # id -> type/alignment (store as small ints for speed)
            # types: 0=townsfolk,1=outsider,2=minion,3=demon
            self.type_id = {'townsfolk':0, 'outsider':1, 'minion':2, 'demon':3}
            self.id_type = [0] * len(self.char_names)
            self.id_align = [0] * len(self.char_names)  # 0=good,1=evil

            for name in self.char_names:
                cid = self.char_id[name]
                tname = self.scriptCharacters[name]
                tid = self.type_id[tname]
                self.id_type[cid] = tid
                # outsiders + townsfolk are good; minion + demon are evil
                if tid >= 2: self.id_align[cid] = 1

            # Precompute some id lists used a lot
            self.townsfolkIds = []
            self.outsiderIds = []
            self.minionIds = []
            self.demonIds = []

            for name in self.townsfolkNames: self.townsfolkIds.append(self.char_id[name])
            for name in self.outsiderNames: self.outsiderIds.append(self.char_id[name])
            for name in self.minionNames: self.minionIds.append(self.char_id[name])
            self.demonIds.append(self.char_id['imp'])
            self.demonIds.append(self.char_id['dead_imp'])

            # Handy ids
            self.ID_RECLUSE = self.char_id.get('recluse', -1)
            self.ID_SPY = self.char_id.get('spy', -1)
            self.ID_IMP = self.char_id.get('imp', -1)
            self.ID_DEAD_IMP = self.char_id.get('dead_imp', -1)

            # --- CHARACTER OBJECT CACHE ---
            # Build once; solver will reuse these instead of constructing 100k+ character objects.
            self.char_obj = {}
            for nm in self.char_names:
                self.char_obj[nm] = self.character(self, nm)


        else: raise Exception("Script not supported. Currently supports: ['trouble_brewing'].")
    
    class player:
        def __init__(self, parent, name, claimedCharacterName=None):
            if type(name) is not str: raise Exception("Players must have a name.")
            self.name = name.lower()
            self.game = parent
            self.seat = 0
            self.isMe = (name.lower() == 'you')
            self.claimedCharacter = None
            if claimedCharacterName:
                self.claimedCharacter = self.game.char_obj[claimedCharacterName.lower()]
            self.claimedInfos = [None] # array of daytimes, one info per day following the info
            self.actions = [[]] # array of daytimes. Each daytime can have multiple actions
            self.alive = True # only changed by the solving functions
            self.poisoned = False
            self.actualCharacter = None # starting character, known to ST. Only specified by the solving functions
            self.updatedCharacter = None # only specified by the solving functions
            self.actualCharacterId = None
            self.updatedCharacterId = None
            self.isFortuneTellerRedHerring = False
        
        def __eq__(self, other):
            if other == None: return False
            return self.name == other.name

        def claim(self, claimedCharacterName):
            self.claimedCharacter = self.game.char_obj[claimedCharacterName.lower()]

        def add_info(self, number=None, characterName=None, name1=None, name2=None):
            self.claimedInfos[self.game.day] = self.info(self, number, characterName, name1, name2)
        
        def previous_info(self, nightNumber, number=None, characterName=None, name1=None, name2=None):
            # nightNumber starts with the 0th night and corresponds to the day after
            if (type(nightNumber) is not int) or nightNumber < 0 or nightNumber > self.game.day: 
                raise Exception("Provide a valid index for the night when the info was received.")
            self.claimedInfos[nightNumber] = self.info(self, number, characterName, name1, name2)

        def add_action(self, actionType=None, targetName=None, result=None):
            self.actions[self.game.day].append(self.action(self, actionType, targetName, result))
            if actionType in {'was_nominated','was_executed'} and result == 'trigger':
                self.game.executedPlayers.append(self)
                self.alive = False

        def nominate(self, nominee, result=None):
            self.game.players[nominee].add_action('was_nominated', self.name, result)
        
        def slay(self, target, result):
            self.add_action('slay', target, result)

        def executed_by_vote(self):
            self.add_action('was_executed')
        was_executed_by_vote = executed_by_vote

        def was_killed_at_night(self):
            self.game.demonKilledPlayers.append(self)
            self.alive = False
        killed_at_night = was_killed_at_night

        def set_character(self, characterName):  # compat wrapper (slower)
            cid = self.game.char_id[characterName.lower()]
            self.set_character_id(cid)

        def set_character_id(self, cid):  # fast: takes int id
            self.actualCharacterId = cid
            self.updatedCharacterId = cid

            # reuse cached objects; avoid name lookups
            obj = self.game.char_obj[self.game.char_names[cid]]
            self.actualCharacter = obj
            self.updatedCharacter = obj

        def reset_to_claimed(self):  # fastest common case in solver loop
            # assumes claimedCharacter is always set
            cid = self.game.char_id[self.claimedCharacter.name]
            self.set_character_id(cid)

        
        def canRegisterAsChar(self, character):
            # character can be either a character object OR a name OR an id.
            # For speed, prefer passing an int id in solver code.
            if type(character) is int:
                targetId = character
            elif type(character) is str:
                targetId = self.game.char_id[character.lower()]
            else:
                # assume character object with .name
                targetId = self.game.char_id[character.name]

            myId = self.updatedCharacterId

            if targetId == myId: 
                return True

            if self.poisoned == False:
                if myId == self.game.ID_RECLUSE:
                    # recluse may register as any evil character
                    return self.game.id_align[targetId] == 1
                if myId == self.game.ID_SPY:
                    # spy may register as any good character
                    return self.game.id_align[targetId] == 0

            # dead imp registers as imp (for undertaker / FT logic etc.)
            if myId == self.game.ID_DEAD_IMP and targetId == self.game.ID_IMP:
                return True

            return False

        def canRegisterAsType(self, charType):
            # charType can be your existing strings ('townsfolk', etc.) or int type ids.
            if type(charType) is int:
                targetType = charType
            else:
                targetType = self.game.type_id[charType]

            myId = self.updatedCharacterId
            myType = self.game.id_type[myId]

            if targetType == myType:
                return True

            if self.poisoned == False:
                if myId == self.game.ID_RECLUSE and (targetType == 2 or targetType == 3):
                    return True
                if myId == self.game.ID_SPY and (targetType == 0 or targetType == 1):
                    return True

            return False
        
        def mustRegisterAsType(self, charType):
            # charType can be string ('townsfolk') or int (0..3)
            if type(charType) is int:
                targetType = charType
            else:
                targetType = self.game.type_id[charType]

            myId = self.updatedCharacterId

            # recluse/spy are not forced to register as their true type (unless poisoned)
            if (myId == self.game.ID_RECLUSE or myId == self.game.ID_SPY) and (self.poisoned == False):
                return False

            return targetType == self.game.id_type[myId]

        def canRegisterAsAlignment(self, alignment):
            # alignment can be 'good'/'evil' or 0/1
            if type(alignment) is int:
                targetAlign = alignment
            else:
                targetAlign = 0 if alignment == 'good' else 1

            myId = self.updatedCharacterId

            if targetAlign == self.game.id_align[myId]:
                return True

            if self.poisoned == False:
                if myId == self.game.ID_RECLUSE and targetAlign == 1:
                    return True
                if myId == self.game.ID_SPY and targetAlign == 0:
                    return True

            return False
        
        def mustRegisterAsAlignment(self, alignment):
            if type(alignment) is int:
                targetAlign = alignment
            else:
                targetAlign = 0 if alignment == 'good' else 1

            myId = self.updatedCharacterId

            if (myId == self.game.ID_RECLUSE or myId == self.game.ID_SPY) and (self.poisoned == False):
                return False

            return targetAlign == self.game.id_align[myId]
        
        def listPossibleCharRegisters(self):
            myId = self.updatedCharacterId
            if self.game.id_type[myId] == 3:  # demon
                return 'imp'
            if myId == self.game.ID_RECLUSE and self.poisoned == False:
                return self.game.minionNames + ['recluse', 'imp']
            if myId == self.game.ID_SPY and self.poisoned == False:
                return self.game.townsfolkNames + self.game.outsiderNames + ['spy']
            return self.game.char_names[myId]
        
        class info:
            def __init__(self, parent, number=None, characterName=None, name1=None, name2=None):
                self.player = parent
                if number != None and ((type(number) is not int) or number < 0): 
                    raise Exception("Provide a valid number for the character's info.")
                self.number = number
                self.character = None
                if(characterName): 
                    if characterName.lower() not in self.player.game.scriptCharacters.keys():
                        raise Exception("Character '" + str(characterName.lower()) + "' is not in the selected script.")
                    self.character = self.player.game.char_obj[characterName.lower()]
                self.player1 = None
                if(name1): 
                    if name1.lower() not in self.player.game.players.keys():
                        raise Exception("There is no player with this name.")
                    self.player1 = self.player.game.players[name1.lower()]
                self.player2 = None
                if(name2): 
                    if name2.lower() not in self.player.game.players.keys():
                        raise Exception("There is no player with this name.")
                    self.player2 = self.player.game.players[name2.lower()]

        class action:
            def __init__(self, parent, actionType, targetName=None, result=None):
                self.player = parent
                if actionType.lower() not in self.player.game.scriptActions: 
                    raise Exception("Action not supported in the selected script.")
                self.type = actionType.lower()
                self.targetPlayer = None
                if targetName != None and targetName.lower() not in self.player.game.players.keys():
                    raise Exception("There is no player with this name.")
                if(targetName): self.targetPlayer = self.player.game.players[targetName.lower()]
                if result != None and result.lower() in {'none','failed'}: 
                    raise Exception("Use the None object instead of a string to report no action result.")
                if result == None: self.result = None
                else: self.result = result.lower()
                self.player.game.dailyActions[-1].append(self)
    
    class character:
        def __init__(self, parent, name):
            self.game = parent
            if name.lower() not in self.game.scriptCharacters.keys():
                raise Exception('Character is not in the selected script.')
            self.name = name.lower()
            self.type = self.get_type()
            self.alignment = self.get_alignment()

        def __eq__(self, other):
            return self.name == other.name
        
        def get_type(self):
            if self.name in self.game.scriptCharacters.keys():
                return self.game.scriptCharacters[self.name]
            return None

        def get_alignment(self):
            match self.type:
                case 'townsfolk': return 'good'
                case 'outsider': return 'good'
                case 'minion': return 'evil'
                case 'demon': return 'evil'
                case _: return None
    
    class world:
        def __init__(self, parent, startingCharacterNamesList, fortuneTellerRedHerringSeat, replacementMinionNamesQueue=None):
            self.game = parent
            self.startingCharacterNamesList = startingCharacterNamesList
            self.fortuneTellerRedHerringSeat = fortuneTellerRedHerringSeat
            if replacementMinionNamesQueue is None:
                replacementMinionNamesQueue = []
            self.replacementMinionNamesQueue = replacementMinionNamesQueue
            self.finalCharactersDict = {}
            self.transformationsDict = {}
            self.startingCharacterDict = {}
            self.poisonsBlockingInfo = []
            self.blockingPoisonsCount = 0
            for turnPoison in self.game.poisonsBlockingInfo: 
                self.poisonsBlockingInfo.append(turnPoison)
                if turnPoison: self.blockingPoisonsCount += 1

        def startersString(self):
            for c in range(len(self.startingCharacterNamesList)):
                self.startingCharacterDict[self.startingCharacterNamesList[c]] = self.game.circle[c].name
            return str(self.startingCharacterDict)
        
        def hasGreatPoisoner(self):
            if self.blockingPoisonsCount > 0 and self.poisonsBlockingInfo[0]: 
                return True
            return False
        
        def __str__(self):
            demons = {}
            deadDemons = {}
            minions = {}
            drunks = {}
            others = {}          
            
            for startingChar in self.startingCharacterNamesList:
                if startingChar in self.transformationsDict.keys():
                    self.transformationsDict[startingChar]

            for charName in self.finalCharactersDict.keys():
                if charName in {'imp'}: demons[charName] = self.finalCharactersDict[charName]
                elif charName in {'dead_imp'}: deadDemons[charName] = self.finalCharactersDict[charName]
                elif charName in self.game.minionNames: minions[charName] = self.finalCharactersDict[charName]
                elif charName in {'drunk'}: drunks[charName] = self.finalCharactersDict[charName]
                else: others[charName] = self.finalCharactersDict[charName]

            s = 'IMP: '
            if 'imp' in demons.keys(): s += demons['imp']
            if demons['imp'] in self.transformationsDict.keys(): 
                s += ' (was ' + self.transformationsDict[demons['imp']][0] + ')'
            s += '\n\t'
            if len(deadDemons.keys()) > 0:
                for deadDemonKey in deadDemons.keys():
                    s += deadDemonKey + ': ' + deadDemons[deadDemonKey]
                    if deadDemons[deadDemonKey] in self.transformationsDict.keys():
                        s += ' (was ' + self.transformationsDict[deadDemons[deadDemonKey]][0] + ')'
                s += '\n\t'
            for minionKey in minions.keys():
                s += minionKey + ': ' + minions[minionKey] + ', '
            s = s[:-2] + '\n\t'
            for drunkKey in drunks.keys():
                s += drunkKey + ': ' + drunks[drunkKey] + ', '
            s = s[:-2] + '\n\t'
            for otherKey in others.keys():
                s += otherKey + ': ' + others[otherKey] + ', ' 
            s = s[:-2]  
            if len(self.poisonsBlockingInfo) > 0:
                s += '\n\t' + str(self.blockingPoisonsCount) + '/' + str(len(self.poisonsBlockingInfo)) + ' info-blocking or action-blocking poisonings'
                if self.blockingPoisonsCount > 0 and self.poisonsBlockingInfo[0]: s += ', including the first night'
            return s     

    class analytics:
        def __init__(self, parent):
            self.game = parent
            self.valid_configurations_count = self.game.valid_configurations_count
            self.imp_counts = self.game.imp_counts
            self.imp_fractions = self.game.imp_fractions
            self.certain_targets_on_most_certain_targeted = self.game.certain_targets_on_most_certain_targeted
            self.certain_imp_player_name = self.game.certain_imp_player_name
            self.most_targeted = self.game.most_targeted
            self.certain_accusations = self.game.certain_accusations
            self.possible_imps = self.game.possible_imps
            

            # gp means "great poisoner"

            self.gp_valid_configurations_count = self.game.gp_valid_configurations_count
            self.gp_imp_counts = self.game.gp_imp_counts
            self.gp_imp_fractions = self.game.gp_imp_fractions


        def __str__(self):
            r = 'possible imps: ' + str(self.possible_imps) + '\n'
            r += 'imp probabilities across ' + str(self.valid_configurations_count) + ' valid configurations:\n' + str(self.imp_fractions) + '\n' 
            r += 'imp probabilities across ' + str(self.gp_valid_configurations_count) + ' valid configurations without lucky 1st-night poisoners:\n' + str(self.gp_imp_fractions)
            if self.certain_imp_player_name != None:
                r += '\n' + self.certain_imp_player_name + ' is the imp! '
                #r += str(self.certain_targets_on_most_certain_targeted) + ' players are sure, which is enough!'
            else: 
                # r += '\n' + self.most_targeted + ' has the most players pointing to them. The players indicate imp probabilities for ' + self.most_targeted + ' of: ' + str(self.game.consensus_imp_certainties)
                if len(self.game.certain_accusations.keys()) > 0:
                    r += '\nThe following players can accuse with certainty: '
                    for accuser in self.certain_accusations.keys():
                        r += accuser + ' accuses ' + self.certain_accusations[accuser] + '. '
                else: r += '\nNo players can say they identified the imp with certainty.'
            return r

    def get_analytics(self):
        if self.solutions == []: raise Exception("No solutions for generating analytics.")
        self.valid_configurations_count = len(self.solutions)
        self.gp_valid_configurations_count = self.valid_configurations_count # gp means "great poisoner"

        # count how many times each player is the updated imp:
        self.imp_counts = {}
        self.possible_imps = set()
        self.gp_imp_counts = {} 
        self.perspective_imp_counts = [] # count imp possibilities from each player's perspective
        self.perspective_valid_configurations_counts = [] # list of dicts of names to the number of solutions where they're the imp. Indexed by the seat of the player who considers these solutions
        self.perspective_imp_fractions = [] # list of dicts of names to the fraction of solutions where they're the imp. Indexed by the seat of the player who considers these solutions
        self.perspective_imp_player_names = [] # list of names of top imp candidate players, indexed by which player seat thinks they're most likely the imp
        self.perspective_imp_certainties = [] # how certain each player is that their top imp candidate is the imp
        for player in self.circle: 
            self.imp_counts[player.name] = 0
            self.gp_imp_counts[player.name] = 0
            self.perspective_imp_counts.append({})
            self.perspective_valid_configurations_counts.append(0)
            self.perspective_imp_fractions.append({})
            for player2 in self.circle:
                self.perspective_imp_counts[-1][player2.name] = 0
        for solution in self.solutions:
            self.imp_counts[solution.finalCharactersDict['imp']] += 1
            self.possible_imps.add(solution.finalCharactersDict['imp'])
            for player in self.circle:
                if self.character(self, solution.startingCharacterNamesList[player.seat]).alignment == 'good': # assumes alignment doesn't change in the script
                    self.perspective_imp_counts[player.seat][solution.finalCharactersDict['imp']] += 1
                    self.perspective_valid_configurations_counts[player.seat] += 1
            if solution.hasGreatPoisoner() == False: self.gp_imp_counts[solution.finalCharactersDict['imp']] += 1
            else: self.gp_valid_configurations_count -= 1

        self.imp_fractions = {}
        self.gp_imp_fractions = {}
        self.perspective_target_frequencies = {} # dict of player names to how many players think they're the most likely imp 
        self.perspective_certain_target_frequencies = {} # dict of player names to how many players know for certain they're the imp
        for name in self.imp_counts.keys():
            self.imp_fractions[name] = round(self.imp_counts[name] / self.valid_configurations_count, 3)
            if self.gp_valid_configurations_count > 0:
                self.gp_imp_fractions[name] = round(self.gp_imp_counts[name] / self.gp_valid_configurations_count, 3)
            self.perspective_target_frequencies[name] = 0
            self.perspective_certain_target_frequencies[name] = 0
            for player in self.circle:
                if self.perspective_valid_configurations_counts[player.seat] > 0:
                    self.perspective_imp_fractions[player.seat][name] = round(self.perspective_imp_counts[player.seat][name] / self.perspective_valid_configurations_counts[player.seat], 3)
                else: self.perspective_imp_fractions[player.seat][name] = 0

        for player in self.circle: # find each player's top-predicted imp and certainty
            top_certainty = 0
            top_candidate = None
            for candidate in self.circle:
                fraction = self.perspective_imp_fractions[player.seat][candidate.name]
                if fraction >= top_certainty: 
                    top_certainty = fraction
                    top_candidate = candidate
            self.perspective_imp_certainties.append(top_certainty)
            self.perspective_imp_player_names.append(top_candidate.name)
        
        # do more players agree with certainty about the imp's identity than there are evil players? If so, that player must be the imp.
        self.consensus_imp_player_name = None
        self.certain_imp_player_name = None
        self.most_targeted = None
        self.targets_on_most_targeted = 0
        self.most_certain_targeted = None
        self.certain_targets_on_most_certain_targeted = 0
        self.certain_accusations = {}
        for p in range(len(self.circle)):
            self.perspective_target_frequencies[self.perspective_imp_player_names[p]] += 1
            if self.perspective_target_frequencies[self.perspective_imp_player_names[p]] >= self.targets_on_most_targeted:
                self.most_targeted = self.perspective_imp_player_names[p]
                self.targets_on_most_targeted = self.perspective_target_frequencies[self.perspective_imp_player_names[p]]
            if self.perspective_imp_certainties[p] == 1: # player should be saying they're sure
                self.certain_accusations[self.circle[p].name] = self.perspective_imp_player_names[p]
                self.perspective_certain_target_frequencies[self.perspective_imp_player_names[p]] += 1
                if self.perspective_certain_target_frequencies[self.perspective_imp_player_names[p]] >= self.certain_targets_on_most_certain_targeted:
                    self.most_certain_targeted = self.perspective_imp_player_names[p]
                    self.certain_targets_on_most_certain_targeted = self.perspective_certain_target_frequencies[self.perspective_imp_player_names[p]]
        
        if self.certain_targets_on_most_certain_targeted > self.characterCounts[len(self.circle)][2] + self.characterCounts[len(self.circle)][3]:
            # then most_certain_targeted must be the imp because there's at least one good player who's sure
            self.certain_imp_player_name = self.most_certain_targeted
        else:
            # create a list of each player's certainties that consensus_imp is the imp, then sort
            self.consensus_imp_certainties = []
            for player in self.circle:
                self.consensus_imp_certainties.append(self.perspective_imp_fractions[player.seat][self.most_targeted])
            self.consensus_imp_certainties.sort(reverse=True)

        return self.analytics(self)

    def createWorld(self): # useful for debugging
        startingCharNames = []
        fortuneTellerRedHerringSeat = None
        for player in self.circle:
            startingCharNames.append(player.actualCharacter.name)
            if player.isFortuneTellerRedHerring: fortuneTellerRedHerringSeat = player.seat     
        return self.world(self, startingCharNames, fortuneTellerRedHerringSeat)


    def add_player(self, name, claimedCharacterName=None):
        self.circle.append(self.player(self, name, claimedCharacterName))
        self.circle[-1].seat = len(self.circle) - 1
        key = name.lower()
        self.players[key] = self.circle[-1]
        return self.players[key]

    def add_players(self, names):
        for name in names:
            self.add_player(name)

    def set_random_players_and_claims(self, playerCount, evilStrategy=None, stRolesMinInfo=0, youExist=False): # for constructing new games
        names = ['you','abed','beth','chris','denny','egan','finn','gisele','haoyu','igor','julie','kaito','layla','mwangi','neha','omar']
        if youExist: namesIndex = 0
        else: namesIndex = 1

        if (type(playerCount) is not int) or playerCount < 5 or playerCount > 15:
            raise Exception("Choose a player count between 5 and 15.")
        
        # assign seats
        for i in range(playerCount):
            self.add_player(names[i + namesIndex])

        chars = [] # index is seat

        availableMinions = []
        for minionName in self.minionNames: 
            if minionName != 'baron' or self.characterCounts[playerCount][0] > 3: # prevent 1-townsfolk games
                availableMinions.append(minionName)
        availableOutsiders = []
        for outsiderName in self.outsiderNames: availableOutsiders.append(outsiderName)
        availableTownsfolk = []
        for townsfolkName in self.townsfolkNames: availableTownsfolk.append(townsfolkName)
        
        # choose an imp
        chars.append('imp')
        
        # choose minions
        modifiedOutsiderCount = self.characterCounts[playerCount][1]
        modifiedTownsfolkCount = self.characterCounts[playerCount][0]
        
        while len(self.minionNames) - len(availableMinions) < self.characterCounts[playerCount][2]:
            chars.append(availableMinions.pop(random.randint(0, len(availableMinions) - 1)))
            if chars[-1] == 'baron': 
                modifiedOutsiderCount += 2
                modifiedTownsfolkCount -= 2

        # choose outsiders
        drunkHallucination = None
        drunkTokensChosen = 0
        while len(self.outsiderNames) - len(availableOutsiders) < modifiedOutsiderCount:
            chars.append(availableOutsiders.pop(random.randint(0, len(availableOutsiders) - 1)))
            if chars[-1] == 'drunk': 
                drunkHallucination = availableTownsfolk.pop(random.randint(0, len(availableTownsfolk) - 1))
                drunkTokensChosen += 1

        # choose townsfolk
        townsfolkChars = []
        unusedTownsfolk = []
        infoRoleCount = 0
        while len(self.townsfolkNames) - (len(availableTownsfolk) + drunkTokensChosen) < modifiedTownsfolkCount:
            townsfolkChars.append(availableTownsfolk.pop(random.randint(0, len(availableTownsfolk) - 1)))
            if townsfolkChars[-1] in self.infoRoles: infoRoleCount += 1
        t = 0
        while infoRoleCount < stRolesMinInfo and t < len(townsfolkChars): # swap out non-info townsfolk roles until you meet the strategy-defined minimum
            if chars[t] not in self.infoRoles:
                unusedTownsfolk.append(townsfolkChars.pop(t))
                townsfolkChars.append(availableTownsfolk.pop(random.randint(0, len(availableTownsfolk) - 1)))
                if townsfolkChars[-1] in self.infoRoles: 
                    infoRoleCount += 1
                    t += 1
            else: t += 1

        chars = chars + townsfolkChars
        
        redHerringIndex = random.randint(self.characterCounts[playerCount][2] + 1, playerCount - 1)
        # assumes fortune teller red herring can't start as the spy and can't move

        random.shuffle(chars)
        while youExist and chars[0] not in self.townsfolkNames + self.outsiderNames: # 'you' must be good
            random.shuffle(chars)
        
        availableGood = availableOutsiders + availableTownsfolk + unusedTownsfolk
        drunkIndex = None
        for i in range(len(availableGood)):
            if availableGood[i] == 'drunk': drunkIndex = i
        if drunkIndex != None: availableGood.pop(drunkIndex)
        random.shuffle(availableGood)
        self.impBluffCharNames = availableGood[0:3]

        for c in range(playerCount): 
            self.circle[c].set_character(chars[c])
            if c == redHerringIndex: self.circle[c].isFortuneTellerRedHerring = True
            if self.circle[c].updatedCharacterId == self.char_id['drunk']:
                self.circle[c].claim(drunkHallucination)
            elif self.id_align[self.circle[c].updatedCharacterId] == 0:  # good
                self.circle[c].claim(chars[c])
            else:
                # evil player picks a good character to claim, depending on strategy
                if evilStrategy == None or self.id_type[self.circle[c].updatedCharacterId] == 2:  # minion 
                    goodNames = self.townsfolkNames + self.outsiderNames # random picks for imp and minions
                    drunkIndex = None
                    for i in range(len(goodNames)):
                        if goodNames[i] == 'drunk': drunkIndex = i
                    if drunkIndex != None: goodNames.pop(drunkIndex)
                    self.circle[c].claim(goodNames[random.randint(0,len(goodNames)-1)])    
                else: self.circle[c].claim(self.impBluffCharNames[0]) # bluff pick for imp if there's a basic strategy
                
    def findPlayerByUpdatedCharacter(self, characterName):
        cid = self.char_id[characterName.lower()]
        for player in self.circle:
            if player.updatedCharacterId == cid:
                return player
        return None

    def pickNRandomPlayerNames(self, n, excludeNamesList, canRegisterAsType=None):
        names = []
        picks = []
        for player in self.circle: 
            if player.name not in excludeNamesList: 
                if canRegisterAsType == None or player.canRegisterAsType(canRegisterAsType):
                    names.append(player.name)
        if len(names) < n: return False
        if len(names) == 1: return names
        random.shuffle(names)
        while len(picks) < n: picks.append(names.pop())
        return picks
    
    def chefRange(self, player):
        playerCount = len(self.circle)
        minPairs = 0
        maxPairs = 0
        for seat in range(playerCount):
            if self.circle[seat].canRegisterAsAlignment(1) and self.circle[(seat + 1) % playerCount].canRegisterAsAlignment(1):
                maxPairs += 1
            if self.circle[seat].mustRegisterAsAlignment(1) and self.circle[(seat + 1) % playerCount].mustRegisterAsAlignment(1):
                minPairs += 1
        return (minPairs, maxPairs)
    
    def empathRange(self, player):
        playerCount = len(self.circle)
        minCount = 0
        maxCount = 0

        # find neighbours
        leftNeighbour = self.circle[(player.seat + 1) % playerCount]
        while leftNeighbour.alive == False:
            leftNeighbour = self.circle[(leftNeighbour.seat + 1) % playerCount]
        rightNeighbour = self.circle[(player.seat - 1) % playerCount]
        while rightNeighbour.alive == False:
            rightNeighbour = self.circle[(rightNeighbour.seat - 1) % playerCount]

        if leftNeighbour.canRegisterAsAlignment(1): maxCount += 1
        if not leftNeighbour.canRegisterAsAlignment(0): minCount += 1

        if rightNeighbour.canRegisterAsAlignment(1): maxCount += 1
        if not rightNeighbour.canRegisterAsAlignment(0): minCount += 1
        
        return (minCount, maxCount)

    def run_random_night_and_day(self, evilStrategy=None, maxDays=None): # for constructing games
        playerCount = len(self.circle)
        monkedPlayer = None
        monkablePlayers = []
        livingMinions = []
        livingPlayers = []
        goodLivingPlayers = []
        townsfolkClaimers = []
        charPlayers = {} # dict of ID to player object
        for player in self.circle:
            player.poisoned = False
            if player.alive and player.updatedCharacterId != self.char_id['monk']: monkablePlayers.append(player)
            if player.alive and self.id_align[player.updatedCharacterId] == 0: goodLivingPlayers.append(player)
            if self.id_type[player.updatedCharacterId] == 2 and player.alive: livingMinions.append(player)
            if self.day == 0 and player.claimedCharacter.type == 'townsfolk': townsfolkClaimers.append(player)
            charPlayers[player.updatedCharacterId] = player

        monkId = self.char_id['monk']
        if monkId in charPlayers:
            livingPlayers = monkablePlayers + [charPlayers[monkId]]
        else:
            livingPlayers = monkablePlayers
        
        # poisoner
        poisonerId = self.char_id['poisoner']
        impId = self.ID_IMP
        monkId = self.char_id['monk']
        mayorId = self.char_id['mayor']
        soldierId = self.char_id['soldier']
        scarletWomanId = self.char_id['scarlet_woman']

        if poisonerId in charPlayers and charPlayers[poisonerId].alive:
            if evilStrategy == None:
                (goodLivingPlayers + [charPlayers[poisonerId], charPlayers[impId]])[random.randint(0, len(goodLivingPlayers) + 1)].poisoned = True
            else:
                picks = self.pickNRandomPlayerNames(1, [charPlayers[poisonerId].name, charPlayers[impId].name])
                if picks == False: return False
                self.players[picks[0]].poisoned = True
        # monk
        if self.day > 0 and monkId in charPlayers and charPlayers[monkId].alive and (charPlayers[monkId].poisoned == False):
            monkedPlayer = monkablePlayers[random.randint(0, len(monkablePlayers) - 1)]
        
        def killPlayer(p, atNight):
            if atNight: p.was_killed_at_night()
            if p.updatedCharacterId == self.ID_IMP:
                if atNight and len(livingMinions) == 0: 
                    self.active = False
                    self.winner = 'good'
                elif atNight:
                    replacement = livingMinions[random.randint(0, len(livingMinions) - 1)]

                    # If Scarlet Woman is alive and there are 5+ living players, she becomes the imp.
                    if (scarletWomanId in charPlayers) and charPlayers[scarletWomanId].alive and (len(livingPlayers) >= 5):
                        replacement = charPlayers[scarletWomanId]

                    # Remove old ids from lookup dict (we will re-add with new ids)
                    if replacement.updatedCharacterId in charPlayers:
                        charPlayers.pop(replacement.updatedCharacterId)
                    if impId in charPlayers:
                        charPlayers.pop(impId)

                    # Apply transformation on BOTH id and object
                    replacement.updatedCharacterId = impId
                    replacement.updatedCharacter = self.char_obj['imp']

                    p.updatedCharacterId = self.ID_DEAD_IMP
                    p.updatedCharacter = self.char_obj['dead_imp']

                    # Re-add to lookup dict with new ids
                    charPlayers[replacement.updatedCharacterId] = replacement
                    charPlayers[p.updatedCharacterId] = p

                    # If replacement was a minion, remove them from livingMinions (they're now demon)
                    mIndex = None
                    for m in range(len(livingMinions)):
                        if livingMinions[m] == replacement:
                            mIndex = m
                            break
                    if mIndex != None:
                        livingMinions.pop(mIndex)

                else: # imp killed during the day
                    if scarletWomanId in charPlayers and charPlayers[scarletWomanId].alive and len(livingPlayers) >= 5:
                        replacement = charPlayers.pop(scarletWomanId)
                    else: 
                        self.active = False
                        self.winner = 'good'
            liveIndex = None
            for live in range(len(livingPlayers)):
                if livingPlayers[live] == p: liveIndex = live
            livingPlayers.pop(liveIndex)
            if self.id_type[p.updatedCharacterId] == 2: # minion
                mIndex = None
                for m in range(len(livingMinions)): 
                    if livingMinions[m] == p: mIndex = m
                livingMinions.pop(mIndex)
            elif self.id_align[p.updatedCharacterId] == 0:
                gIndex = None
                for g in range(len(goodLivingPlayers)): 
                    if goodLivingPlayers[g] == p: gIndex = g
                goodLivingPlayers.pop(gIndex)
            if p in townsfolkClaimers:
                tIndex = None
                for t in range(len(townsfolkClaimers)):
                    if townsfolkClaimers[t] == p: tIndex = t
                townsfolkClaimers.pop(tIndex)

        def getInfoCharNameForPlayer(p, possiblyWrong):
            deterministic = False
            if possiblyWrong: allowedNames = self.townsfolkNames + self.minionNames + self.outsiderNames + ['imp']
            elif p.updatedCharacterId == self.ID_RECLUSE: allowedNames = self.minionNames + ['imp','recluse']
            elif p.updatedCharacterId == self.ID_SPY: allowedNames = self.townsfolkNames + self.outsiderNames + ['spy'] 
            else: deterministic = True

            if deterministic and p.updatedCharacterId == self.ID_DEAD_IMP:
                return 'imp'
            elif deterministic:
                return self.char_names[p.updatedCharacterId]
            return allowedNames[random.randint(0, len(allowedNames) - 1)]        
        
        # imp
        if self.day > 0 and (impId in charPlayers) and (charPlayers[impId].poisoned == False):
            if (evilStrategy == None or self.id_type[charPlayers[impId].actualCharacterId] == 2) and len(livingMinions) > 0:
                nightDeathPlayer = livingPlayers[random.randint(0, len(livingPlayers) - 1)]
                # allow the imp to kill a minion or itself. Minion is #2
            else: nightDeathPlayer = goodLivingPlayers[random.randint(0,len(goodLivingPlayers)-1)] # for basic evil strategy, don't kill yourself or minions as the imp
            if (mayorId in charPlayers) and (nightDeathPlayer == charPlayers[mayorId]):
                nightDeathPlayer = livingPlayers[random.randint(0, len(livingPlayers) - 1)]

            if (nightDeathPlayer != monkedPlayer) and ((soldierId not in charPlayers) or (nightDeathPlayer != charPlayers[soldierId])):
                killPlayer(nightDeathPlayer, True)
        
        # info roles and fakers
        for player in self.circle:
            possiblyWrongInfo = (self.id_align[player.updatedCharacterId] == 1) or player.poisoned or (player.updatedCharacterId == self.char_id['drunk'])
            match player.claimedCharacter.name:
                case 'washerwoman':
                    if player.alive and possiblyWrongInfo:
                        picks = self.pickNRandomPlayerNames(2, [player.name])
                        if picks == False: return False
                        if evilStrategy != None: # strategic imps should avoid using a bluff here. evils should avoid their own claimed character
                            possibleFakeTownsfolkChars = []
                            for char in self.townsfolkNames: 
                                if player.actualCharacter.name == 'imp' and char not in self.impBluffCharNames and char != 'washerwoman': possibleFakeTownsfolkChars.append(char)
                                elif char != 'washerwoman': possibleFakeTownsfolkChars.append(char)
                        else: possibleFakeTownsfolkChars = self.townsfolkNames
                        player.add_info(1,possibleFakeTownsfolkChars[random.randint(0,len(possibleFakeTownsfolkChars)-1)],picks[0],picks[1])
                    elif player.alive:
                        picks = self.pickNRandomPlayerNames(1, [player.name],'townsfolk')
                        if picks == False: return False
                        registeredName = picks[0]
                        otherNames = self.pickNRandomPlayerNames(1,[player.name, registeredName])
                        if otherNames == False: return False
                        if self.players[registeredName].updatedCharacterId == self.ID_SPY:
                            registeredTownsfolk = self.townsfolkNames[random.randint(0,len(self.townsfolkNames)-1)]
                        else: registeredTownsfolk = self.char_names[self.players[registeredName].updatedCharacterId]
                        player.add_info(1,registeredTownsfolk,registeredName,otherNames[0])
                case 'librarian':
                    if player.alive and possiblyWrongInfo:
                        if (self.characterCounts[playerCount][1] == 0 and random.randint(1,8) <= 5) or (self.characterCounts[playerCount][1] == 1 and random.randint(1,8) == 8):
                            player.add_info(0)
                        else:
                            picks = self.pickNRandomPlayerNames(2, [player.name])
                            if picks == False: return False
                            if evilStrategy != None: # pick any non-bluff outsider or the drunk
                                possibleFakeOutsiderChars = []
                                for char in self.outsiderNames:
                                    if player.actualCharacterId == self.ID_IMP and char not in self.impBluffCharNames: possibleFakeOutsiderChars.append(char)
                                possibleFakeOutsiderChars.append('drunk')
                                player.add_info(1,possibleFakeOutsiderChars[random.randint(0,len(possibleFakeOutsiderChars)-1)],picks[0],picks[1])
                            else:
                                player.add_info(1,self.outsiderNames[random.randint(0,len(self.outsiderNames)-1)],picks[0],picks[1])
                    elif player.alive:
                        minOutsidersRegistered = self.characterCounts[playerCount][1]
                        maxOutsidersRegistered = self.characterCounts[playerCount][1]
                        recluseId = self.ID_RECLUSE
                        spyId = self.ID_SPY
                        if (recluseId in charPlayers) and (charPlayers[recluseId].poisoned == False): minOutsidersRegistered -= 1
                        if (spyId in charPlayers) and (charPlayers[spyId].poisoned == False): maxOutsidersRegistered += 1

                        if maxOutsidersRegistered == 0: player.add_info(0)
                        elif minOutsidersRegistered == 0 and random.randint(0,maxOutsidersRegistered) == 0: player.add_info(0)
                        else:
                            registeredName = None
                            registeredOutsider = None
                            picks = self.pickNRandomPlayerNames(1, [player.name],'outsider')
                            if picks == False: return False
                            registeredName = picks[0]
                            otherNames = self.pickNRandomPlayerNames(1,[player.name, registeredName])
                            if otherNames == False: return False
                            if self.players[registeredName].updatedCharacterId == self.ID_SPY:
                                registeredOutsider = self.outsiderNames[random.randint(0,len(self.outsiderNames)-1)]
                            else: registeredOutsider = self.char_names[self.players[registeredName].updatedCharacterId]
                            player.add_info(1,registeredOutsider, registeredName, otherNames[0])
                case 'investigator':
                    if player.alive and possiblyWrongInfo:
                        picks = self.pickNRandomPlayerNames(2, [player.name])
                        if picks == False: return False
                        player.add_info(1,self.minionNames[random.randint(0,len(self.minionNames)-1)],picks[0],picks[1])
                    elif player.alive:
                        registeredName = None
                        registeredMinion = None
                        picks = self.pickNRandomPlayerNames(1, [player.name],'minion')
                        if picks == False: return False
                        registeredName = picks[0]     
                        otherNames = self.pickNRandomPlayerNames(1,[player.name, registeredName])
                        if otherNames == False: return False
                        if self.players[registeredName].updatedCharacterId == self.ID_RECLUSE:
                            registeredMinion = self.minionNames[random.randint(0,len(self.minionNames)-1)]
                        else: registeredMinion = self.char_names[self.players[registeredName].updatedCharacterId]
                        player.add_info(1,registeredMinion,registeredName,otherNames[0])
                case 'chef':
                    if player.alive and possiblyWrongInfo:
                        evilPairMax = self.characterCounts[playerCount][2] # assumes trouble brewing. minion count, plus the imp, minus 1
                        recluseId = self.ID_RECLUSE
                        if (recluseId in charPlayers) and (charPlayers[recluseId].poisoned == False):
                            evilPairMax += 1
                        player.add_info(int(round((random.randint(0,int(round(math.sqrt(evilPairMax) * 4))) ** 2) / 16))) # maxes lower numbers of pairs a bit likelier
                    elif player.alive:
                        (minPairs, maxPairs) = self.chefRange(player)
                        player.add_info(random.randint(minPairs,maxPairs))
                case 'empath':
                    if player.alive and possiblyWrongInfo: player.add_info(random.randint(0,2))
                    elif player.alive:
                        (minCount, maxCount) = self.empathRange(player)
                        player.add_info(random.randint(minCount,maxCount))
                case 'fortune_teller':
                    picks = self.pickNRandomPlayerNames(2, [])
                    if picks == False: return False
                    if player.alive and possiblyWrongInfo:
                        player.add_info(random.randint(0,1),'imp',picks[0],picks[1])
                    elif player.alive:
                        if self.players[picks[0]].mustRegisterAsType(3) or self.players[picks[1]].mustRegisterAsType('demon') or self.players[picks[0]].isFortuneTellerRedHerring or self.players[picks[1]].isFortuneTellerRedHerring:
                            player.add_info(1,'imp',picks[0],picks[1])
                        elif self.players[picks[0]].canRegisterAsType(3) or self.players[picks[1]].canRegisterAsType('demon'):
                            player.add_info(random.randint(0,1),'imp',picks[0],picks[1])
                        else:
                            player.add_info(0,'imp',picks[0],picks[1])
                case 'undertaker':
                    if player.alive and self.day > 0 and self.executedPlayers[self.day-1] != None: # someone was executed
                        player.add_info(1, getInfoCharNameForPlayer(self.executedPlayers[self.day-1], possiblyWrongInfo), self.executedPlayers[self.day-1].name)
                case 'ravenkeeper':
                    if self.demonKilledPlayers[self.day] == player: # player is dead
                        targetPlayer = self.circle[random.randint(0,playerCount-1)] # anyone, dead or alive
                        player.add_info(1, getInfoCharNameForPlayer(targetPlayer, possiblyWrongInfo), targetPlayer.name)

        # create all possible consequential actions
        noOneExecutedTodayYet = True
        for player in livingPlayers:
            match player.claimedCharacter.name:
                case 'virgin': # be nominated by a random living player
                    if self.day == 0:
                        nominator = townsfolkClaimers[random.randint(0,len(townsfolkClaimers)-1)]
                        result = None
                        if player.updatedCharacterId == self.char_id['virgin'] and player.poisoned == False: 
                            if nominator.canRegisterAsType(0): #townsfolk
                                if nominator.mustRegisterAsType(0) or random.randint(0,1) == 1: # spies can register 50%
                                    result = 'trigger'
                                    killPlayer(nominator, False)
                                    noOneExecutedTodayYet = False
                        nominator.nominate(player.name, result)
                case 'slayer': # shoot at a random living player
                    if self.day == 0:
                        target = livingPlayers[random.randint(0,len(livingPlayers)-1)]
                        result = None
                        if player.updatedCharacterId == self.char_id['slayer'] and player.poisoned == False:
                            if target.canRegisterAsType(3):
                                if target.mustRegisterAsType(3) or random.randint(0,1) == 1: # recluses can register 50%
                                    result = 'trigger'
                                    killPlayer(target, False)
                        player.slay(target.name, result)
        
        # random player executed
        if noOneExecutedTodayYet and self.day < maxDays - 1 and len(livingPlayers) != 4 and random.randint(0,len(livingPlayers)) == 0: # allow for a chance of non-execution
            executee = livingPlayers[random.randint(0,len(livingPlayers)-1)]
            executee.executed_by_vote()
            if executee.updatedCharacterId == self.char_id['saint'] and executee.poisoned == False: 
                self.active = False
                self.winner = 'evil'
            killPlayer(executee, False)
        elif self.day >= maxDays - 1: self.active = False # stop the game early to analyze
        
    def print_game_summary(self):
        s = '***GAME SUMMARY:***\n'
        for player in self.circle:
            s += player.name + ' (claims ' + player.claimedCharacter.name + ')\n'
        
        for d in range(self.day + 1):
            s += '\nNIGHT ' + str(d) + ':\n'    
            if d > 0:
                if self.demonKilledPlayers[d] == None: s += 'No one killed at night.\n'
                else: s += self.demonKilledPlayers[d].name + ' killed at night.\n'
            for player in self.circle:
                info = player.claimedInfos[d]
                if info != None: 
                    s += player.name + ' (claiming ' + player.claimedCharacter.name + ') '
                    match player.claimedCharacter.name:
                        case 'washerwoman' | 'librarian' | 'investigator' | 'fortune_teller':
                            if info.number == 1: s += 'saw that ' + info.player1.name + ' or ' + info.player2.name + ' is the ' + info.character.name + '.\n'
                            elif player.claimedCharacter.name == 'librarian': s += 'saw 0 outsiders in play.\n'
                            elif player.claimedCharacter.name == 'fortune_teller': s += 'saw that neither ' + info.player1.name + ' nor ' + info.player2.name + ' is the imp.\n'
                        case 'chef': s += 'saw ' + str(info.number) + ' pairs of evil players.\n'
                        case 'empath': s += 'saw ' + str(info.number) + ' evil neighbours.\n'
                        case 'undertaker': s += 'saw ' + info.character.name + ' was executed yesterday.\n'
                        case 'monk': s += 'protected ' + info.player1.name + '.\n'
                        case 'ravenkeeper': s += 'saw ' + info.player1.name + ' is the ' + info.character.name + '.\n'
            s += 'DAY ' + str(d) + ':\n'  
            for action in self.dailyActions[d]:
                if action.type == 'was_executed': s += action.player.name + ' was executed by vote.\n'
                elif action.type == 'slay': 
                    s += action.player.name + ' shot ' + action.targetPlayer.name + ' and '
                    if action.result == 'trigger': s += action.targetPlayer.name + ' died.\n'
                    else: s += 'nothing happened.\n'
                elif action.type == 'was_nominated':
                    s += action.targetPlayer.name + ' nominated ' + action.player.name
                    if action.result == 'trigger': s += ' and ' + action.targetPlayer.name + ' was executed.\n'
                    else: s += '.\n'
        
        if self.winner != None: s += '*** GAME OVER: ' + self.winner + ' wins! ***'

        print(s)
    
    def next_day(self):
        self.day += 1
        self.dailyActions.append([])
        if len(self.demonKilledPlayers) < self.day: self.demonKilledPlayers.append(None)
        if len(self.executedPlayers) < self.day: self.executedPlayers.append(None)
        for player in self.circle:
            player.actions.append([])
            player.claimedInfos.append(None)

    def everyPermutationWithNItems(self, n, itemCount): # used to select wrong characters
        permutations = []
        if n == 1:
            for i in range(itemCount): permutations.append([i])
        else:
            smallerPermutations = self.everyPermutationWithNItems(n - 1, itemCount)
            for smallerPermutation in smallerPermutations:
                for i in range(itemCount):
                    if i not in smallerPermutation: 
                        longerPermutation = [element for element in smallerPermutation]
                        longerPermutation.append(i)
                        permutations.append(longerPermutation)
        return permutations

    def isConsistent(self, queuedReplacementMinionNames):
        playerCount = len(self.circle)
        infoRolesCount = 0
        outsiderCount = 0
        self.characterIds = set()
        self.countLivingPlayers = playerCount
        self.livingMinions = []
        self.executedPlayers = []
        self.replacedMinionNames = []
        self.poisonsBlockingInfo = []
        self.fortuneTellerRedHerring = None
        self.redHerringCanMove = False
        drunk = None
        virginNeverNominated = True
        
        for player in self.circle:
            player.alive = True
            player.poisoned = False # never gets set True while solving so we only need to set it here
            cid = player.actualCharacterId
            if cid in self.characterIds: return False
            if player.actualCharacter.name in self.infoRoles:
                infoRolesCount += 1
            self.characterIds.add(cid)
            if player.isFortuneTellerRedHerring:
                self.fortuneTellerRedHerring = player
                if player.canRegisterAsAlignment(1) and self.meta_redHerringCanMoveRule: self.redHerringCanMove = True # must be recluse or spy red herring
            if player.isMe and player.actualCharacter.name not in {'drunk', player.claimedCharacter.name}:
                return False
            elif player.actualCharacterId == self.char_id['drunk']:
                outsiderCount += 1
                if player.claimedCharacter.type != 'townsfolk': return False
                drunk = player
            elif self.id_type[player.actualCharacterId] == 1:  # outsider
                outsiderCount += 1
            elif self.id_type[player.actualCharacterId] == 2:  # minion
                self.livingMinions.append(player)

        
        if drunk != None and self.char_id[drunk.claimedCharacter.name] in self.characterIds:  return False # drunk can't think they're a character that's actually in play
        if infoRolesCount < self.meta_minInfoRolesCount: return False

        expectedOutsiders = self.characterCounts[playerCount][1]
        if self.char_id['baron'] in self.characterIds: expectedOutsiders += 2
        if expectedOutsiders != outsiderCount: return False

        def scarletBecomesImp(scarletPlayer):
            self.characterIds.discard(self.char_id['scarlet_woman'])
            s = None
            for m in range(len(self.livingMinions)):
                if self.livingMinions[m] == scarletPlayer: s = m
            if s == None: raise Exception("Can't find scarlet woman among living minions. ")
            else: 
                self.livingMinions.pop(s)
            scarletPlayer.updatedCharacterId = self.ID_IMP
            scarletPlayer.updatedCharacter = self.char_obj['imp']


        def killedPlayer(player, nightDeath, queuedReplacementMinionNames):
            self.countLivingPlayers -= 1
            player.alive = False
            if nightDeath and player.updatedCharacterId == self.ID_IMP:
                if len(self.livingMinions) < 1: return False # the imp can't kill itself if no minions remain
                
                scarletWoman = self.findPlayerByUpdatedCharacter('scarlet_woman')
                if scarletWoman != None and scarletWoman.alive and self.countLivingPlayers >= 4: # then we need to use the scarlet woman
                    scarletBecomesImp(scarletWoman)
                    player.updatedCharacterId = self.ID_DEAD_IMP
                elif len(queuedReplacementMinionNames) > 0: # check if there's a queue
                    # just use the first minion in the queue
                    replacedMinionName = queuedReplacementMinionNames.pop(0)
                    
                    self.replacedMinionNames.append(replacedMinionName)
                    self.characterIds.discard(self.char_id[replacedMinionName])
                    rep = self.findPlayerByUpdatedCharacter(replacedMinionName)
                    rep.updatedCharacterId = self.ID_IMP
                    player.updatedCharacterId = self.ID_DEAD_IMP
                    r = None
                    for m in range(len(self.livingMinions)):
                        if self.id_type[self.livingMinions[m].updatedCharacterId] == 3: r = m  # demon
                    if r == None: raise Exception("Can't find replacement minions.")     
                    self.livingMinions.pop(r)
                else:
                    # select any minion 
                    replacedMinion = self.livingMinions.pop()
                    self.replacedMinionNames.append(self.char_names[replacedMinion.updatedCharacterId])
                    self.characterIds.remove(replacedMinion.updatedCharacterId)
                    replacedMinion.updatedCharacterId = self.ID_IMP  
                    player.updatedCharacterId = self.ID_DEAD_IMP

                    # enqueue each alternative choice
                    
                    if len(self.livingMinions) > 0:
                        characterNamesList = []
                        fortuneTellerRedHerringSeat = None
                        for p in self.circle:
                            characterNamesList.append(p.actualCharacter.name)
                            if p.isFortuneTellerRedHerring: fortuneTellerRedHerringSeat = p.seat
                    
                    for livingMinion in self.livingMinions:
                        # create a new world to queue, with a list of starting characters and a queue of replacements
                        minionNamesQueue = []
                        i = 0
                        while i < len(self.replacedMinionNames) - 1: # don't use the last element in the list because it was just added. should queue another choice instead
                            minionNamesQueue.append(self.replacedMinionNames[i])
                            i += 1
                        minionNamesQueue.append(self.char_names[livingMinion.updatedCharacterId])
                        self.queuedWorlds.append(self.world(self, characterNamesList, fortuneTellerRedHerringSeat, minionNamesQueue))
            elif player.updatedCharacterId == self.ID_IMP: # imp was still killed during the day and game is still going. Replacement must be scarlet woman
                scarletWoman = self.findPlayerByUpdatedCharacter('scarlet_woman')
                if self.countLivingPlayers < 4 or scarletWoman == None or scarletWoman.alive == False: return False  # after imp killed during the day, scarlet woman needs 4+ players to still live
                else:
                    scarletBecomesImp(scarletWoman)
                player.updatedCharacterId = self.ID_DEAD_IMP
                self.executedPlayers.append(player)
            elif self.id_type[player.updatedCharacterId] == 2: # minion
                self.characterIds.discard(player.updatedCharacterId)
                mIndex = None
                for m in range(len(self.livingMinions)):
                    if self.livingMinions[m] == player: mIndex = m
                self.livingMinions.pop(mIndex)
                self.executedPlayers.append(player)
            else:
                self.characterIds.discard(player.updatedCharacterId)
                self.executedPlayers.append(player)
            return True

        for testDay in range(self.day + 1):
            poisoners = 0
            poisonedNames = set()
            if self.char_id['poisoner'] in self.characterIds: poisoners = 1
            
            # process night deaths
            deadPlayerToday = None
            if testDay < len(self.demonKilledPlayers):
                deadPlayerToday = self.demonKilledPlayers[testDay]
                if deadPlayerToday != None: 
                    if deadPlayerToday.updatedCharacterId == self.char_id['soldier']: poisonedNames.add(deadPlayerToday.name)
                    if killedPlayer(self.demonKilledPlayers[testDay], True, queuedReplacementMinionNames) == False: return False

            # process night info

            for player in self.circle: 
                info = player.claimedInfos[testDay]
                if info != None and self.id_align[player.updatedCharacterId] == 0:
                    match self.char_names[player.updatedCharacterId]:
                        case "washerwoman":
                            if info.player1.canRegisterAsChar(info.character) == False and info.player2.canRegisterAsChar(info.character) == False:
                                poisonedNames.add(player.name)
                        case "librarian":
                            if info.number == 0: 
                                butlerId = self.char_id['butler']
                                drunkId = self.char_id['drunk']
                                saintId = self.char_id['saint']
                                for p2 in self.circle:
                                    if p2.updatedCharacterId == butlerId or p2.updatedCharacterId == drunkId or p2.updatedCharacterId == saintId:
                                        poisonedNames.add(player.name)
                            elif info.player1.canRegisterAsChar(info.character) == False and info.player2.canRegisterAsChar(info.character) == False:
                                poisonedNames.add(player.name)
                        case "investigator":
                            if info.player1.canRegisterAsChar(info.character) == False and info.player2.canRegisterAsChar(info.character) == False:
                                poisonedNames.add(player.name)
                        case "chef":
                            (minPairCount, maxPairCount) = self.chefRange(player)
                            if info.number < minPairCount or info.number > maxPairCount: poisonedNames.add(player.name)
                        case "empath":
                            (minCount, maxCount) = self.empathRange(player)
                            if info.number < minCount or info.number > maxCount: poisonedNames.add(player.name)
                        case "fortune_teller" | "fortuneteller":
                            minCount = 0
                            maxCount = 0

                            if self.id_type[info.player1.updatedCharacterId] == 3 or self.id_type[info.player2.updatedCharacterId] == 3: # must register as demon, #3
                                minCount = 1
                                maxCount = 1
                            elif info.player1.mustRegisterAsType(2) and info.player2.mustRegisterAsType(2):
                                minCount = 0
                                maxCount = 0
                            elif self.redHerringCanMove:
                                minCount = 0
                                maxCount = 1
                            elif info.player1.isFortuneTellerRedHerring or info.player2.isFortuneTellerRedHerring: 
                                minCount = 1
                                maxCount = 1
                            elif info.player1.canRegisterAsType(3) or info.player2.canRegisterAsType(3): # there's a recluse and a non-demon non-herring
                                minCount = 0
                                maxCount = 1 
                            if info.number < minCount or info.number > maxCount: poisonedNames.add(player.name)
                        case "undertaker":
                            if testDay > 0 and self.executedPlayers[testDay-1] == None: return False # undertaker shouldn't be woken without execution
                            elif testDay > 0 and (not self.executedPlayers[testDay-1].canRegisterAsChar(info.character)):
                                poisonedNames.add(player.name)
                        case "monk": # considered "info" instead of an action because it's secretly chosen
                            if deadPlayerToday == info.player1:
                                poisonedNames.add(player.name)
                        case "ravenkeeper":
                            if not info.player1.canRegisterAsChar(info.character): poisonedNames.add(player.name)
                
                if len(poisonedNames) > poisoners: return False

            # check action consistency

            for action in self.dailyActions[testDay]:
                if action.type == 'slay' and action.targetPlayer.alive and action.player.alive:
                    if action.player.updatedCharacterId == self.char_id['slayer']:
                        if self.id_type[action.targetPlayer.updatedCharacterId] == 3: # recluse means anything can happen and player is consistent. #3 is demon
                            if action.result == None: 
                                poisonedNames.add(action.player.name) # slayer could be poisoned
                            else:
                                if killedPlayer(action.targetPlayer, False, queuedReplacementMinionNames) == False: return False
                        elif not action.targetPlayer.canRegisterAsType(3):
                            if action.result != None: return False
                    elif action.result != None: return False # spy can't fake the slayer's ability
                    
                elif action.type in {'was_nominated', 'wasnominated'} and virginNeverNominated and action.player.alive:
                    if action.player.updatedCharacterId == self.char_id['virgin']:
                        virginNeverNominated = False
                        if action.result != None: 
                            if killedPlayer(action.targetPlayer, False, queuedReplacementMinionNames) == False: return False
                        if self.id_type[action.targetPlayer.updatedCharacterId] == 0: # not spy: spy means anything can happen and player is consistent. # 0 is townsfolk
                            if action.result == None: 
                                poisonedNames.add(action.player.name) # virgin could be poisoned
                        elif not action.targetPlayer.canRegisterAsType(0):
                            if action.result != None: return False
                    elif action.result != None: return False # spy can't fake the virgin's ability
                
                elif action.type in {'was_executed','wasexecuted'}:
                    if action.player.updatedCharacterId == self.char_id['saint']: # the game didn't end because we're solving a puzzle
                        poisonedNames.add(action.player.name)
                    if killedPlayer(action.player, False, queuedReplacementMinionNames) == False: return False

                if len(poisonedNames) > poisoners: return False     

            if len(poisonedNames) == 1: self.poisonsBlockingInfo.append(True)
            elif poisoners == 1: self.poisonsBlockingInfo.append(False)  # the poisoner failed to block info or actions   
        return True

    def getAllSolutions(self, meta_movingRedHerringsAllowed=True, meta_minInfoRoles=0, suppress_printing=False, drunksCount=None):
        if meta_movingRedHerringsAllowed == False: self.meta_redHerringCanMoveRule = False # technically the storyteller can start the red herring as the spy or recluse, and then move it to another player whenever desired. This setting bans/ignores that
        self.meta_minInfoRolesCount = meta_minInfoRoles
        initialWrongCharList = ['imp'] # wrongCharList will be a unique combination (not permutation) of possible wrongly-claimed characters 
        if drunksCount == 1: initialWrongCharList.append('drunk')
        elif drunksCount == None:
            x = self.getAllSolutions(meta_movingRedHerringsAllowed, meta_minInfoRoles, suppress_printing, 0)
            y = self.getAllSolutions(meta_movingRedHerringsAllowed, meta_minInfoRoles, suppress_printing, 1)
            return x + y
        
        countCheckedConfigs = 0
        consistentCircles = set()
        solutionWorlds = []
        def recordIfConsistent(replacementMinionNamesQueue=[]):
            if self.isConsistent(replacementMinionNamesQueue):
                consistentCircle = []
                solutionDict = {}
                transformationsDict = {}
                redHerringSeat = None
                for player in self.circle:
                    consistentCircle.append(player.actualCharacter.name)
                    solutionDict[self.char_names[player.updatedCharacterId]] = player.name
                    if player.isFortuneTellerRedHerring == True:
                        redHerringSeat = player.seat
                    if not player.updatedCharacter == player.actualCharacter:
                        transformationsDict[player.name] = [player.actualCharacter.name, self.char_names[player.updatedCharacterId]]
                circleTuple = tuple(consistentCircle)
                if circleTuple not in consistentCircles:
                    consistentCircles.add(circleTuple)
                    solutionWorld = self.world(self, consistentCircle, redHerringSeat)
                    solutionWorld.finalCharactersDict = solutionDict
                    solutionWorld.transformationsDict = transformationsDict
                    solutionWorlds.append(solutionWorld)
                return True
            return False       

        (townsfolkCount, outsidersCount, minionsCount, demonsCount) = self.characterCounts[len(self.circle)]
        
        wrongCharPlayerCount = drunksCount + minionsCount + demonsCount 
        wrongCharPerms = self.everyPermutationWithNItems(wrongCharPlayerCount,len(self.circle))
        minionCombos = self.combinationsWith4Types[minionsCount]
        
        for wrongCharPerm in wrongCharPerms:
            for minionCombo in minionCombos:
                wrongCharList = [e for e in initialWrongCharList]
                for element in minionCombo:
                    wrongCharList.append(self.minionNames[element])
                fortuneTellerClaimed = False
                for player in self.circle:
                    if player.claimedCharacter.name in {'fortune_teller','fortuneteller'}: fortuneTellerClaimed = True
                if fortuneTellerClaimed:
                    herringIndex = 0
                    while herringIndex < len(self.circle):
                        herring = self.circle[herringIndex]
                        for player in self.circle:
                            player.isFortuneTellerRedHerring = False
                            player.reset_to_claimed()
                        wrongCharIds = []
                        for nm in wrongCharList:
                            wrongCharIds.append(self.char_id[nm])
                        for i in range(wrongCharPlayerCount):
                            self.circle[wrongCharPerm[i]].set_character_id(wrongCharIds[i])
                        if herring.canRegisterAsAlignment(0):
                            herring.isFortuneTellerRedHerring = True
                        if recordIfConsistent(): herringIndex = len(self.circle) # exit the loop. already found consistent one                     
                        else: herringIndex += 1
                else:
                    for player in self.circle:
                        player.isFortuneTellerRedHerring = False
                        player.reset_to_claimed()
                    wrongCharIds = []
                    for nm in wrongCharList:
                        wrongCharIds.append(self.char_id[nm])
                    for i in range(wrongCharPlayerCount):
                        self.circle[wrongCharPerm[i]].set_character_id(wrongCharIds[i])
                    recordIfConsistent()
                countCheckedConfigs += 1
                if suppress_printing == False and countCheckedConfigs % 10000 == 0: print('... Checking configurations with ' + str(drunksCount) + ' drunks. Checked ' + str(countCheckedConfigs) + ' so far...')

        # check other queued worlds:
        while len(self.queuedWorlds) > 0:
            world = self.queuedWorlds.pop()
            for player in self.circle:
                player.set_character(world.startingCharacterNamesList[player.seat])
                player.isFortuneTellerRedHerring = False
                if player.seat == world.fortuneTellerRedHerringSeat: player.isFortuneTellerRedHerring = True
            recordIfConsistent(world.replacementMinionNamesQueue)

        if suppress_printing == False: print("... Checked ", countCheckedConfigs, " configurations with ", drunksCount, "drunks.")
        for sol in solutionWorlds:
            self.solutions.append(sol)
        return solutionWorlds

clocktower = game # back-compatPlayer