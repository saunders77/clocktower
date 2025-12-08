import random, math

class game:
    def __init__(self, script):
        self.circle = [] # ordered list of players by seat
        self.players = {} # dictionary to reference players by name
        self.day = 0
        
        self.dailyActions = [[]]
        self.meta_redHerringCanMoveRule = True
        self.meta_minInfoRolesCount = 0
        self.solutions = [] # "world" class objects

        # for solving: 
        self.queuedWorlds = []
        self.executedPlayers = [] # indexed by the day when the execution happened
        self.demonKilledPlayers = [None] # indexed by the day after kill
        self.poisonsBlockingInfo = []


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
            for role in self.scriptCharacters.keys():
                if self.scriptCharacters[role] == 'townsfolk': self.townsfolkNames.append(role)
                elif self.scriptCharacters[role] == 'outsider': self.outsiderNames.append(role)
                elif self.scriptCharacters[role] == 'minion': self.minionNames.append(role)

            self.scriptActions = {
                'slay',
                'was_nominated',
                'was_executed'
            }
        else: raise Exception("Script not supported. Currently supports: ['trouble_brewing'].")
    
    class player:
        def __init__(self, parent, name, claimedCharacterName=None):
            if type(name) is not str: raise Exception("Players must have a name.")
            self.name = name.lower()
            self.game = parent
            self.seat = 0
            self.isMe = (name.lower() == 'you')
            self.claimedCharacter = None
            if(claimedCharacterName): self.claimedCharacter = self.game.character(self.game, claimedCharacterName)
            
            self.claimedInfos = [None] # array of daytimes, one info per day following the info
            self.actions = [[]] # array of daytimes. Each daytime can have multiple actions
            self.alive = True # only changed by the solving functions
            self.actualCharacter = None # starting character, known to ST. Only specified by the solving functions
            self.updatedCharacter = None # only specified by the solving functions
            self.isFortuneTellerRedHerring = False
        
        def __eq__(self, other):
            if other == None: return False
            return self.name == other.name

        def claim(self, claimedCharacterName):
            self.claimedCharacter = self.game.character(self.game, claimedCharacterName)

        def add_info(self, number=None, characterName=None, name1=None, name2=None):
            self.claimedInfos[self.game.day] = self.info(self, number, characterName, name1, name2)
        
        def previous_info(self, nightNumber, number=None, characterName=None, name1=None, name2=None):
            # nightNumber starts with the 0th night and corresponds to the day after
            if (type(nightNumber) is not int) or nightNumber < 0 or nightNumber > self.game.day: 
                raise Exception("Provide a valid index for the night when the info was received.")
            self.claimedInfos[nightNumber] = self.info(self, number, characterName, name1, name2)

        def add_action(self, actionType=None, targetName=None, result=None):
            self.actions[self.game.day].append(self.action(self, actionType, targetName, result))

        def nominate(self, nominee, result=None):
            self.game.players[nominee].add_action('was_nominated', self.name, result)
        
        def slay(self, target, result):
            self.add_action('slay', target, result)

        def executed_by_vote(self):
            self.add_action('was_executed')
        was_executed_by_vote = executed_by_vote

        def was_killed_at_night(self):
            self.game.demonKilledPlayers.append(self)
        killed_at_night = was_killed_at_night

        def set_character(self, characterName): # to be used only during solving
            self.actualCharacter = self.game.character(self.game, characterName)
            self.updatedCharacter = self.game.character(self.game, characterName)
        
        def canRegisterAsChar(self, character):
            if character == self.updatedCharacter: return True
            if self.updatedCharacter.name == 'recluse' and character.alignment == 'evil': return True
            if self.updatedCharacter.name == 'spy' and character.alignment == 'good': return True
            if self.updatedCharacter.name == 'dead_imp' and character.name == 'imp': return True
            return False

        def canRegisterAsType(self, charType):
            if charType == self.updatedCharacter.type: return True
            if self.updatedCharacter.name == 'recluse' and charType in {'minion', 'demon'}: return True
            if self.updatedCharacter.name == 'spy' and charType in {'townsfolk', 'outsider'}: return True
            return False
        
        def mustRegisterAsType(self, charType):
            if self.updatedCharacter.name in {'recluse', 'spy'}: return False
            if charType == self.updatedCharacter.type: return True
            return False

        def canRegisterAsAlignment(self, alignment):
            if alignment == self.updatedCharacter.alignment: return True
            if self.updatedCharacter.name == 'recluse' and alignment == 'evil': return True
            if self.updatedCharacter.name == 'spy' and alignment == 'good': return True
            return False
        
        def mustRegisterAsAlignment(self, alignment):
            if self.updatedCharacter.name in {'recluse', 'spy'}: return False
            if alignment == self.updatedCharacter.alignment: return True
            return False
        
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
                    self.character = self.player.game.character(self.player.game, characterName.lower())
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
        def __init__(self, parent, startingCharacterNamesList, fortuneTellerRedHerringSeat, replacementMinionNamesQueue=[]):
            self.game = parent
            self.startingCharacterNamesList = startingCharacterNamesList
            self.fortuneTellerRedHerringSeat = fortuneTellerRedHerringSeat
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

            # gp means "great poisoner"

            self.gp_valid_configurations_count = self.game.gp_valid_configurations_count
            self.gp_imp_counts = self.game.gp_imp_counts
            self.gp_imp_fractions = self.game.gp_imp_fractions


        def __str__(self):
            r = 'imp probabilities across ' + str(self.valid_configurations_count) + ' valid configurations:\n' + str(self.imp_fractions) + '\n' 
            r += 'imp probabilities across ' + str(self.gp_valid_configurations_count) + ' valid configurations without lucky 1st-night poisoners:\n' + str(self.gp_imp_fractions)
            if self.certain_imp_player_name != None:
                r += '\n' + self.certain_imp_player_name + ' is the imp! '
                r += str(self.certain_targets_on_most_certain_targeted) + ' players are sure, which is enough!'
            else: 
                # r += '\n' + self.most_targeted + ' has the most players pointing to them. The players indicate imp probabilities for ' + self.most_targeted + ' of: ' + str(self.game.consensus_imp_certainties)
                if len(self.game.certain_accusations.keys()) > 0:
                    r += '\nThe following players can accuse with certainty: '
                    for accuser in self.game.certain_accusations.keys():
                        r += accuser + ' accuses ' + self.game.certain_accusations[accuser] + '. '
                else: r += '\nNo players can say they identified the imp with certainty.'
            return r

    def get_analytics(self):
        if self.solutions == []: raise Exception("No solutions for generating analytics.")
        self.valid_configurations_count = len(self.solutions)
        self.gp_valid_configurations_count = self.valid_configurations_count # gp means "great poisoner"

        # count how many times each player is the updated imp:
        self.imp_counts = {}
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
        return self(self,startingCharNames, fortuneTellerRedHerringSeat)


    def add_player(self, name, claimedCharacterName=None):
        self.circle.append(self.player(self, name, claimedCharacterName))
        self.circle[-1].seat = len(self.circle) - 1
        self.players[name] = self.circle[-1]
        return self.players[name]
    
    def add_players(self, names):
        for name in names:
            self.add_player(name)

    def set_random_players_and_claims(self, playerCount): # for constructing new games
        if (type(playerCount) is not int) or playerCount < 5 or playerCount > 15:
            raise Exception("Choose a player count between 5 and 15.")
        
        # assign seats
        for i in range(playerCount):
            self.add_player(str(i))

        chars = [] # index is seat

        # choose an imp
        chars.append('imp')

        # choose minions
        availableMinions = []
        modifiedOutsiderCount = self.characterCounts[playerCount][1]
        modifiedTownsfolkCount = self.characterCounts[playerCount][0]
        for minionName in self.minionNames: availableMinions.append(minionName)
        while len(self.minionNames) - len(availableMinions) < self.characterCounts[playerCount][2]:
            chars.append(availableMinions.pop(random.randint(0, len(availableMinions) - 1)))
            if chars[-1] == 'baron': 
                modifiedOutsiderCount += 2
                modifiedTownsfolkCount -= 2

        # choose outsiders
        availableOutsiders = []
        for outsiderName in self.outsiderNames: availableOutsiders.append(outsiderName)
        while len(self.outsiderNames) - len(availableOutsiders) < modifiedOutsiderCount:
            chars.append(availableOutsiders.pop(random.randint(0, len(availableOutsiders) - 1)))

        # choose townsfolk
        availableTownsfolk = []
        for townsfolkName in self.townsfolkNames: availableTownsfolk.append(townsfolkName)
        while len(self.townsfolkNames) - len(availableTownsfolk) < modifiedTownsfolkCount:
            chars.append(availableTownsfolk.pop(random.randint(0, len(availableTownsfolk) - 1)))
        
        redHerringIndex = random.randint(self.characterCounts[playerCount][2] + 1, playerCount - 1)
        # assumes fortune teller red herring can't start as the spy and can't move

        random.shuffle(chars)

        for c in range(playerCount): 
            self.circle[c].set_character(chars[c])
            if c == redHerringIndex: self.circle[c].isFortuneTellerRedHerring = True
            if self.circle[c].updatedCharacter.name == 'drunk': self.circle[c].claim(availableTownsfolk.pop(random.randint(0, len(availableTownsfolk)-1)))
            elif self.circle[c].alignment == 'good': self.circle[c].claim(chars[c])
            else: # evil player picks a random good character. might be in play
                goodNames = self.townsfolkNames + self.outsiderNames
                self.circle[c].claim(goodNames[random.randint(0,len(goodNames)-1)])      

    def findPlayerByUpdatedCharacter(self, characterName):
        for player in self.circle:
            if player.updatedCharacter == self.character(self, characterName): return player
        return None

    def pickNRandomPlayerNames(self, n, excludeNamesList):
        names = []
        picks = []
        for player in self.circle: 
            if player.name not in excludeNamesList: names.append(player.name)
        random.shuffle(names)
        while len(picks) < n: picks.append(names.pop())
        return picks
    
    def chefRange(self, player):
        playerCount = len(self.circle)
        minPairs = 0
        maxPairs = 0
        for seat in range(playerCount):
            if self.circle[seat].canRegisterAsAlignment('evil') and self.circle[(seat + 1) % playerCount].canRegisterAsAlignment('evil'):
                maxPairs += 1
            if self.circle[seat].mustRegisterAsAlignment('evil') and self.circle[(seat + 1) % playerCount].mustRegisterAsAlignment('evil'):
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

        if leftNeighbour.canRegisterAsAlignment('evil'): maxCount += 1
        if not leftNeighbour.canRegisterAsAlignment('good'): minCount += 1

        if rightNeighbour.canRegisterAsAlignment('evil'): maxCount += 1
        if not rightNeighbour.canRegisterAsAlignment('good'): minCount += 1
        
        return (minCount, maxCount)

    def run_random_night_and_day(self): # for constructing games
        playerCount = len(self.circle)
        poisonedPlayer = None
        monkedPlayer = None
        monkablePlayers = []
        livingMinions = []
        livingPlayers = []
        goodLivingPlayers = []
        charPlayers = {} # dict of character name to player object
        for player in self.circle:
            if player.alive and player.updatedCharacter.name != 'monk': monkablePlayers.append(player)
            if player.alive and player.updatedCharacter.alignment == 'good': goodLivingPlayers.append(player)
            if player.updatedCharacter.type == 'minion' and player.alive: livingMinions.append(player)
            charPlayers[player.updatedCharacter.name] = player

        if 'monk' in charPlayers.keys(): livingPlayers = monkablePlayers + [charPlayers['monk']]
        
        # poisoner
        if 'poisoner' in charPlayers.keys() and charPlayers['poisoner'].alive: 
            poisonedPlayer = (goodLivingPlayers + [charPlayers['poisoner'], charPlayers['imp']])[random.randint(0,len(livingPlayers)+1)] # allow the poisoner to poison itself to appear non-poisoning. Allow to poison imp to simulate soldier/monk
        # monk
        if self.day > 0 and charPlayers['monk'] != None and charPlayers['monk'].alive and poisonedPlayer != charPlayers['monk']: 
            monkedPlayer = monkablePlayers[random.randint(0,len(monkablePlayers)-1)]
        # imp
        def killPlayerAtNight(p):
            p.alive = False
            p.was_killed_at_night()
            liveIndex = None
            for live in livingPlayers:
                if live == p: liveIndex = live
            livingPlayers.pop(liveIndex)    

        if self.day > 0 and poisonedPlayer != charPlayers['imp']:
            if len(livingMinions) > 0: nightDeathPlayer = livingPlayers[random.randint(0,len(livingPlayers)-1)] # allow the imp to kill a minion or itself
            else: nightDeathPlayer = goodLivingPlayers[random.randint(0,len(goodLivingPlayers)-1)]
            if nightDeathPlayer == charPlayers['mayor']: nightDeathPlayer = livingPlayers[random.randint(0,len(livingPlayers)-1)] # warning: can end the game if kills imp

            if nightDeathPlayer != monkedPlayer and nightDeathPlayer != charPlayers['soldier']: # then proceed with the kill        
                if nightDeathPlayer == charPlayers['imp'] and len(livingMinions) > 0: 
                    replacement = livingMinions[random.randint(0,len(livingMinions)-1)]
                    if charPlayers['scarletWoman'] != None and charPlayers['scarletWoman'].alive and len(livingPlayers) >= 5:
                        replacement = charPlayers['scarletWoman']
                    replacement.updatedCharacter = self.character(self, 'imp')
                    charPlayers['imp'].updatedCharacter = self.character(self, 'dead_imp')
                    mIndex = None
                    for m in livingMinions: 
                        if m == replacement: mIndex = m
                    livingMinions.pop(mIndex)
                killPlayerAtNight(nightDeathPlayer)

        # info roles and fakers
        for player in self.circle:
            if player.alive:
                possiblyWrongInfo = player.updatedCharacter.alignment == 'evil' or player == poisonedPlayer or player == charPlayers['drunk']
                match player.claimedCharacter.name:
                    case 'washerwoman':
                        if possiblyWrongInfo:
                            picks = self.pickNRandomPlayerNames(2, [player.name])
                            player.add_info(1,self.townsfolkNames[random.randint(0,len(self.townsfolkNames)-1)],picks[0],picks[1])
                        else:
                            registeredName = None
                            registeredTownsfolk = None
                            while registeredName == None:
                                picks = self.pickNRandomPlayerNames(1, [player.name])
                                if self.players[picks[0]].canRegisterAsType('townsfolk'): 
                                    registeredName = picks[0]
                            otherName = self.pickNRandomPlayerNames(1,[player.name, registeredName])
                            if self.players[registeredName].updatedCharacter.name == 'spy':
                                registeredTownsfolk = self.townsfolkNames[random.randint(0,len(self.townsfolkNames)-1)]
                            else: registeredTownsfolk = self.players[registeredName].updatedCharacter.name
                            player.add_info(1,registeredTownsfolk,registeredName,otherName)
                    case 'librarian':
                        if possiblyWrongInfo:
                            if (self.characterCounts[playerCount][1] == 0 and random.randint(1,8) <= 5) or (self.characterCounts[playerCount][1] == 1 and random.randint(1,8) == 8):
                                player.add_info(0)
                            else:
                                picks = self.pickNRandomPlayerNames(2, [player.name])
                                player.add_info(1,self.outsiderNames[random.randint(0,len(self.outsiderNames)-1)],picks[0],picks[1])
                        else:
                            minOutsidersRegistered = self.characterCounts[playerCount][1]
                            maxOutsidersRegistered = self.characterCounts[playerCount][1]
                            if self.findPlayerByUpdatedCharacter('recluse') != None: minOutsidersRegistered -= 1
                            if self.findPlayerByUpdatedCharacter('spy') != None: maxOutsidersRegistered += 1
                            if maxOutsidersRegistered == 0: player.add_info(0)
                            elif minOutsidersRegistered == 0 and random.randint(0,maxOutsidersRegistered) == 0: player.add_info(0)
                            else:
                                registeredName = None
                                registeredOutsider = None
                                while registeredName == None:
                                    picks = self.pickNRandomPlayerNames(1, [player.name])
                                    if self.players[picks[0]].canRegisterAsType('outsider'): 
                                        registeredName = picks[0]
                                otherName = self.pickNRandomPlayerNames(1,[player.name, registeredName])
                                if self.players[registeredName].updatedCharacter.name == 'spy':
                                    registeredOutsider = self.outsiderNames[random.randint(0,len(self.outsiderNames)-1)]
                                else: registeredOutsider = self.players[registeredName].updatedCharacter.name
                                player.add_info(1,registeredOutsider, registeredName, otherName)
                    case 'investigator':
                        if possiblyWrongInfo:
                            picks = self.pickNRandomPlayerNames(2, [player.name])
                            player.add_info(1,self.minionNames[random.randint(0,len(self.minionNames)-1)],picks[0],picks[1])
                        else:
                            registeredName = None
                            registeredMinion = None
                            while registeredName == None:
                                picks = self.pickNRandomPlayerNames(1, [player.name])
                                if self.players[picks[0]].canRegisterAsType('minion'): 
                                    registeredName = picks[0]
                            otherName = self.pickNRandomPlayerNames(1,[player.name, registeredName])
                            if self.players[registeredName].updatedCharacter.name == 'recluse':
                                registeredMinion = self.minionNames[random.randint(0,len(self.minionNames)-1)]
                            else: registeredMinion = self.players[registeredName].updatedCharacter.name
                            player.add_info(1,registeredMinion,registeredName,otherName)
                    case 'chef':
                        if possiblyWrongInfo:
                            evilPairMax = self.scriptCharacters[playerCount][2] # assumes trouble brewing
                            if self.findPlayerByUpdatedCharacter('recluse') != None: evilPairMax += 1
                            player.add_info(int(round((random.randint(0,int(round(math.sqrt(evilPairMax) * 4))) ** 2) / 16))) # maxes lower numbers of pairs a bit likelier
                        else:
                            (minPairs, maxPairs) = self.chefRange(player)
                            player.add_info(random.randint(minPairs,maxPairs))
                    case 'empath':
                        if possiblyWrongInfo: player.add_info(random.randint(0,2))
                        else:
                            (minCount, maxCount) = self.empathRange(player)
                            player.add_info(random.randint(minCount,maxCount))
                    case 'fortune_teller':
                        picks = self.pickNRandomPlayerNames(2, [])
                        if possiblyWrongInfo:
                            player.add_info(random.randint(0,1),'imp',picks[0],picks[1])
                        else:
                            if self.players[picks[0]].mustRegisterAsType('demon') or self.players[picks[1]].mustRegisterAsType('demon') or self.players[picks[0]].isFortuneTellerRedHerring or self.players[picks[1]].isFortuneTellerRedHerring:
                                player.add_info(1,'imp',picks[0],picks[1])
                            elif self.players[picks[0]].canRegisterAsType('demon') or self.players[picks[1]].canRegisterAsType('demon'):
                                player.add_info(random.randint(0,1),'imp',picks[0],picks[1])
                            else:
                                player.add_info(0,'imp',picks[0],picks[1])
                    case 'undertaker':
                        if self.day > 0 and self.executedPlayers[self.day-1] != None: # someone was executed
                            normalUndertake = False
                            if possiblyWrongInfo:
                                allowedNames = self.townsfolkNames + self.minionNames + self.outsiderNames + ['imp']
                            elif self.executedPlayers[self.day-1].updatedCharacter.name == 'recluse':
                                allowedNames = self.minionNames + ['imp','recluse']
                            elif self.executedPlayers[self.day-1].updatedCharacter.name == 'spy':
                                allowedNames = self.townsfolkNames + self.outsiderNames + ['spy']
                            else: normalUndertake = True

                            if normalUndertake and self.executedPlayers[self.day-1].updatedCharacter.name == 'dead_imp':
                                player.add_info(1,'imp',self.executedPlayers[self.day-1].name)
                            elif normalUndertake:
                                player.add_info(1,self.executedPlayers[self.day-1].updatedCharacter.name, self.executedPlayers[self.day-1].name)
                            else: # abnormal undertake
                                player.add_info(1, allowedNames[random.randint(0, len(allowedNames)-1)], self.executedPlayers[self.day-1].name) # unlikely to work out as a lie, but possible
                    
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
        self.characterNames = set()
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
            if player.actualCharacter.name in self.characterNames: return False
            if player.actualCharacter.name in {'washerwoman','librarian','investigator','chef','empath','fortune_teller','undertaker'}:
                infoRolesCount += 1
            self.characterNames.add(player.actualCharacter.name)
            if player.isFortuneTellerRedHerring:
                self.fortuneTellerRedHerring = player
                if player.canRegisterAsAlignment('evil') and self.meta_redHerringCanMoveRule: self.redHerringCanMove = True # must be recluse or spy red herring
            if player.isMe and player.actualCharacter.name not in {'drunk', player.claimedCharacter.name}:
                return False
            elif player.actualCharacter.name == 'drunk':
                outsiderCount += 1
                if player.claimedCharacter.type != 'townsfolk': return False
                drunk = player
            elif player.actualCharacter.type == 'outsider': outsiderCount += 1
            elif player.actualCharacter.type == 'minion': self.livingMinions.append(player)
        
        if drunk != None and drunk.claimedCharacter.name in self.characterNames: return False # drunk can't think they're a character that's actually in play
        if infoRolesCount < self.meta_minInfoRolesCount: return False

        expectedOutsiders = self.characterCounts[playerCount][1]
        if 'baron' in self.characterNames: expectedOutsiders = expectedOutsiders + 2
        if expectedOutsiders != outsiderCount: return False

        def scarletBecomesImp(scarletPlayer):
            self.characterNames.remove('scarlet_woman')
            s = None
            for m in range(len(self.livingMinions)):
                if self.livingMinions[m] == scarletPlayer: s = m
            if s == None: raise Exception("Can't find scarlet woman among living minions. ")
            else: 
                self.livingMinions.pop(s)
            scarletPlayer.updatedCharacter = self.character(self, 'imp')

        def killedPlayer(player, nightDeath, queuedReplacementMinionNames):
            self.countLivingPlayers -= 1
            player.alive = False
            if nightDeath and player.updatedCharacter.name == 'imp':
                if len(self.livingMinions) < 1: return False # the imp can't kill itself if no minions remain
                
                scarletWoman = self.findPlayerByUpdatedCharacter('scarlet_woman')
                if scarletWoman != None and scarletWoman.alive and self.countLivingPlayers >= 4: # then we need to use the scarlet woman
                    scarletBecomesImp(scarletWoman)
                    player.updatedCharacter = self.character(self, 'dead_imp')
                elif len(queuedReplacementMinionNames) > 0: # check if there's a queue
                    # just use the first minion in the queue
                    replacedMinionName = queuedReplacementMinionNames.pop(0)
                    
                    self.replacedMinionNames.append(replacedMinionName)
                    self.characterNames.remove(replacedMinionName)
                    self.findPlayerByUpdatedCharacter(replacedMinionName).updatedCharacter = self.character(self, 'imp')
                    player.updatedCharacter = self.character(self, 'dead_imp')
                    r = None
                    for m in range(len(self.livingMinions)):
                        if self.livingMinions[m].updatedCharacter.type == 'demon': r = m
                    if r == None: raise Exception("Can't find replacement minions.")     
                    self.livingMinions.pop(r)
                else:
                    # select any minion 
                    replacedMinion = self.livingMinions.pop()
                    self.replacedMinionNames.append(replacedMinion.updatedCharacter.name)
                    self.characterNames.remove(replacedMinion.updatedCharacter.name)
                    replacedMinion.updatedCharacter = self.character(self, 'imp')
                    player.updatedCharacter = self.character(self, 'dead_imp')

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
                        minionNamesQueue.append(livingMinion.updatedCharacter.name)
                        self.queuedWorlds.append(self.world(self, characterNamesList, fortuneTellerRedHerringSeat, minionNamesQueue))
            elif player.updatedCharacter.name == 'imp': # imp was still killed during the day and game is still going. Replacement must be scarlet woman
                scarletWoman = self.findPlayerByUpdatedCharacter('scarlet_woman')
                if self.countLivingPlayers < 4 or scarletWoman == None or scarletWoman.alive == False: return False  # after imp killed during the day, scarlet woman needs 4+ players to still live
                else:
                    scarletBecomesImp(scarletWoman)
                player.updatedCharacter = self.character(self, 'dead_imp')
                self.executedPlayers.append(player)
            elif player.updatedCharacter.type == 'minion':
                self.characterNames.remove(player.updatedCharacter.name)
                mIndex = None
                for m in range(len(self.livingMinions)):
                    if self.livingMinions[m] == player: mIndex = m
                self.livingMinions.pop(mIndex)
                self.executedPlayers.append(player)
            else:
                self.characterNames.remove(player.updatedCharacter.name)
                self.executedPlayers.append(player)
            return True

        for testDay in range(self.day + 1):
            poisoners = 0
            poisonedNames = set()
            if 'poisoner' in self.characterNames: poisoners = 1
            
            # process night deaths
            deadPlayerToday = None
            if testDay < len(self.demonKilledPlayers):
                deadPlayerToday = self.demonKilledPlayers[testDay]
                if deadPlayerToday != None: 
                    if deadPlayerToday.updatedCharacter.name == 'soldier': poisonedNames.add(deadPlayerToday.name)
                    if killedPlayer(self.demonKilledPlayers[testDay], True, queuedReplacementMinionNames) == False: return False

            # process night info

            for player in self.circle: 
                info = player.claimedInfos[testDay]
                if info != None and player.updatedCharacter.alignment == 'good':
                    match player.updatedCharacter.name:
                        case "washerwoman":
                            if info.player1.canRegisterAsChar(info.character) == False and info.player2.canRegisterAsChar(info.character) == False:
                                poisonedNames.add(player.name)
                        case "librarian":
                            if info.number == 0: 
                                for player in self.circle:
                                    if player.updatedCharacter.name in {'butler', 'drunk', 'saint'}: # characters who must register as outsiders
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

                            if info.player1.updatedCharacter.type == 'demon' or info.player2.updatedCharacter.type == 'demon': # must register as demon
                                minCount = 1
                                maxCount = 1
                            elif info.player1.mustRegisterAsType('minion') and info.player2.mustRegisterAsType('minion'):
                                minCount = 0
                                maxCount = 0
                            elif self.redHerringCanMove:
                                minCount = 0
                                maxCount = 1
                            elif info.player1.isFortuneTellerRedHerring or info.player2.isFortuneTellerRedHerring: 
                                minCount = 1
                                maxCount = 1
                            elif info.player1.canRegisterAsType('demon') or info.player2.canRegisterAsType('demon'): # there's a recluse and a non-demon non-herring
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
                    if action.player.updatedCharacter.name == 'slayer':
                        if action.targetPlayer.updatedCharacter.type == 'demon': # recluse means anything can happen and player is consistent
                            if action.result == None: 
                                poisonedNames.add(action.player.name) # slayer could be poisoned
                            else:
                                if killedPlayer(action.targetPlayer, False, queuedReplacementMinionNames) == False: return False
                        elif not action.targetPlayer.canRegisterAsType('demon'):
                            if action.result != None: return False
                    elif action.result != None: return False # spy can't fake the slayer's ability
                    
                elif action.type in {'was_nominated', 'wasnominated'} and virginNeverNominated and action.player.alive:
                    if action.player.updatedCharacter.name == 'virgin':
                        virginNeverNominated = False
                        if action.result != None: 
                            if killedPlayer(action.targetPlayer, False, queuedReplacementMinionNames) == False: return False
                        if action.targetPlayer.updatedCharacter.type == 'townsfolk': # not spy: spy means anything can happen and player is consistent
                            if action.result == None: 
                                poisonedNames.add(action.player.name) # virgin could be poisoned
                        elif not action.targetPlayer.canRegisterAsType('townsfolk'):
                            if action.result != None: return False
                    elif action.result != None: return False # spy can't fake the virgin's ability
                
                elif action.type in {'was_executed','wasexecuted'}:
                    if player.updatedCharacter.name == 'saint': # the game didn't end because we're solving a puzzle
                        poisonedNames.add(action.player.name)
                    if killedPlayer(action.player, False, queuedReplacementMinionNames) == False: return False

                if len(poisonedNames) > poisoners: return False     

            if len(poisonedNames) == 1: self.poisonsBlockingInfo.append(True)
            elif poisoners == 1: self.poisonsBlockingInfo.append(False)  # the poisoner failed to block info or actions   
        return True

    def getAllSolutions(self, meta_movingRedHerringsAllowed=True, meta_minInfoRoles=0, drunksCount=None):
        if meta_movingRedHerringsAllowed == False: self.meta_redHerringCanMoveRule = False # technically the storyteller can start the red herring as the spy or recluse, and then move it to another player whenever desired. This setting bans/ignores that
        self.meta_minInfoRolesCount = meta_minInfoRoles
        initialWrongCharList = ['imp'] # wrongCharList will be a unique combination (not permutation) of possible wrongly-claimed characters 
        if drunksCount == 1: initialWrongCharList.append('drunk')
        elif drunksCount == None:
            return self.getAllSolutions(meta_movingRedHerringsAllowed, meta_minInfoRoles, 0) + self.getAllSolutions(meta_movingRedHerringsAllowed, meta_minInfoRoles, 1)

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
                    solutionDict[player.updatedCharacter.name] = player.name
                    if player.isFortuneTellerRedHerring == True:
                        redHerringSeat = player.seat
                    if not player.updatedCharacter == player.actualCharacter:
                        transformationsDict[player.name] = [player.actualCharacter.name, player.updatedCharacter.name]
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
        if drunksCount > outsidersCount: return consistentCircles

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
                            player.set_character(player.claimedCharacter.name)
                        for i in range(wrongCharPlayerCount):
                            self.circle[wrongCharPerm[i]].set_character(wrongCharList[i])
                        if herring.canRegisterAsAlignment('good'):
                            herring.isFortuneTellerRedHerring = True
                        if recordIfConsistent(): herringIndex = len(self.circle) # exit the loop. already found consistent one                     
                        else: herringIndex += 1
                else:
                    for player in self.circle:
                        player.isFortuneTellerRedHerring = False
                        player.set_character(player.claimedCharacter.name)
                    for i in range(wrongCharPlayerCount):
                        self.circle[wrongCharPerm[i]].set_character(wrongCharList[i])
                    recordIfConsistent()
                countCheckedConfigs += 1
                if countCheckedConfigs % 10000 == 0: print('... Checking configurations with ' + str(drunksCount) + ' drunks. Checked ' + str(countCheckedConfigs) + ' so far...')

        # check other queued worlds:
        while len(self.queuedWorlds) > 0:
            world = self.queuedWorlds.pop()
            for player in self.circle:
                player.set_character(world.startingCharacterNamesList[player.seat])
                player.isFortuneTellerRedHerring = False
                if player.seat == world.fortuneTellerRedHerringSeat: player.isFortuneTellerRedHerring = True
            recordIfConsistent(world.replacementMinionNamesQueue)

        print("... Checked ", countCheckedConfigs, " configurations with ", drunksCount, "drunks.")
        for sol in solutionWorlds:
            self.solutions.append(sol)
        return solutionWorlds

clocktower = game # back-compatPlayer