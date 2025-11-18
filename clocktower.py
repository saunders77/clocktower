class clocktower:
    def __init__(self, script):
        self.circle = [] # ordered list of players by seat
        self.players = {} # dictionary to reference players by name
        self.day = 0
        self.executedPlayers = [] # indexed by the day of execution
        self.demonKilledPlayers = [None] # indexed by the day after kill
        if script == 'trouble brewing':
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
            self.minionNames = ['poisoner','spy','scarlet woman','baron']
            self.combinationsWith4Types = { # used to select minions
                1: [[0],[1],[2],[3]],
                2: [[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]],
                3: [[0,1,2],[0,1,3],[0,2,3],[1,2,3]]
            }
    
    class player:
        def __init__(self, parent, name, claimedCharacterName=None):
            self.name = name
            self.clocktower = parent
            self.seat = 0
            self.isMe = (name == 'you')
            self.claimedCharacter = None
            if(claimedCharacterName): self.claimedCharacter = clocktower.character(claimedCharacterName)
            self.alive = [True] # array of daytimes. Living status is for the end of the previous night
            self.claimedInfos = [None] # array of daytimes
            self.actions = [[]] # array of daytimes. Each daytime can have multiple actions
            self.actualCharacter = None
        
        def __eq__(self, other):
            return self.name == other.name

        def add_info(self, number=None, characterName=None, name1=None, name2=None):
            self.claimedInfos[self.clocktower.day] = self.info(self, number, characterName, name1, name2)

        def add_action(self, actionType=None, targetName=None, result=None):
            self.actions[self.clocktower.day].append(self.action(self, actionType, targetName, result))
            
            if actionType == 'was_killed_at_night': 
                self.alive[self.clocktower.day] = False
                self.clocktower.demonKilledPlayers.append(self)
            else:
                if self.clocktower.day > 0 and len(self.clocktower.demonKilledPlayers) < self.clocktower.day + 1:
                    self.clocktower.demonKilledPlayers.append(None)
                if actionType == 'was_executed': 
                    self.alive.append(False)
                    self.clocktower.executedPlayers.append(self)
                elif actionType in {'slay','was_nominated'} and result == 'trigger':
                    self.clocktower.players[targetName].alive.append(False)

        def canRegisterAs(self, character):
            if character == self.actualCharacter: return True
            if self.actualCharacter.name == 'recluse' and character.alignment == 'evil': return True
            if self.actualCharacter.name == 'spy' and character.alignment == 'good': return True
            return False

        def canRegisterCharTypeAs(self, charType):
            if charType == self.actualCharacter.type: return True
            if self.actualCharacter.name == 'recluse' and charType in {'minion', 'demon'}: return True
            if self.actualCharacter.name == 'spy' and charType in {'townsfolk', 'outsider'}: return True
            return False

        def canRegisterAsAlignment(self, alignment):
            if alignment == self.actualCharacter.alignment: return True
            if self.actualCharacter.name == 'recluse' and alignment == 'evil': return True
            if self.actualCharacter.name == 'spy' and alignment == 'good': return True
            return False
        
        class info:
            def __init__(self, parent, number=None, characterName=None, name1=None, name2=None):
                self.player = parent
                self.number = number
                self.character = None
                if(characterName): self.character = self.player.clocktower.character(characterName)
                self.player1 = None
                if(name1): self.player1 = self.player.clocktower.players[name1]
                self.player2 = None
                if(name2): self.player2 = self.player.clocktower.players[name2]

        class action:
            def __init__(self, parent, actionType, targetName=None, result=None):
                self.player = parent
                self.type = actionType
                self.targetPlayer = None
                if(targetName): self.targetPlayer = self.player.clocktower.players[targetName]
                self.result = result
    
    class character:
        def __init__(self, name):
            self.name = name
            self.type = self.get_type()
            self.alignment = self.get_alignment()

        def __eq__(self, other):
            return self.name == other.name
        
        def get_type(self):
            match self.name:
                case 'washerwoman': return 'townsfolk'
                case 'librarian': return 'townsfolk'
                case 'investigator': return 'townsfolk'
                case 'chef': return 'townsfolk'
                case 'empath': return 'townsfolk'
                case 'fortune teller': return 'townsfolk'
                case 'undertaker': return 'townsfolk'
                case 'monk': return 'townsfolk'
                case 'ravenkeeper': return 'townsfolk'
                case 'virgin': return 'townsfolk'
                case 'slayer': return 'townsfolk'
                case 'soldier': return 'townsfolk'
                case 'mayor': return 'townsfolk'
                case 'butler': return 'outsider'
                case 'drunk': return 'outsider'
                case 'recluse': return 'outsider'
                case 'saint': return 'outsider'
                case 'poisoner': return 'minion'
                case 'spy': return 'minion'
                case 'scarlet woman': return 'minion'
                case 'baron': return 'minion'
                case 'imp': return 'demon'
                case _: return None

        def get_alignment(self):
            match self.type:
                case 'townsfolk': return 'good'
                case 'outsider': return 'good'
                case 'minion': return 'evil'
                case 'demon': return 'evil'
                case _: return None

    def add_player(self, name, claimedCharacterName=None):
        self.circle.append(self.player(self, name, claimedCharacterName))
        self.circle[-1].seat = len(self.circle) - 1
        self.players[name] = self.circle[-1]

    def next_day(self):
        self.day += 1
        if len(self.executedPlayers) < self.day: self.executedPlayers.append(None)
        for player in self.circle:
            if len(player.alive) == self.day:
                player.alive.append(player.alive[self.day - 1])
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

    def isConsistentDay(self, testDay):
        playerCount = len(self.circle)
        remainingPoisons = 0
        outsiderCount = 0
        baronExists = False
        for player in self.circle:
            playerConsistent = True

            if player.isMe and player.actualCharacter.name not in {'drunk', player.claimedCharacter.name}:
                return False
            elif player.actualCharacter.name == 'baron': baronExists = True
            elif player.actualCharacter.type == 'outsider': outsiderCount += 1

            if player.actualCharacter.name == 'drunk' and player.claimedCharacter.type != 'townsfolk': return False
            
            for action in player.actions[testDay]:
                if action.type == 'slay':
                    if player.actualCharacter.name == 'slayer':
                        if action.targetPlayer.actualCharacter.type == 'demon': # recluse means anything can happen and player is consistent
                            if action.result != 'trigger': 
                                playerConsistent = False # slayer could be poisoned
                                
                        elif not action.targetPlayer.canRegisterCharTypeAs('demon'):
                            if action.result == 'trigger': return False
                    elif action.result == 'trigger': return False # spy can't fake the slayer's ability
                    
                elif action.type == 'was_nominated':
                    if player.actualCharacter.name == 'virgin':
                        if action.targetPlayer.actualCharacter.type == 'townsfolk': # spy means anything can happen and player is consistent
                            if action.result != 'trigger': 
                                playerConsistent = False # virgin could be poisoned
                        elif not action.targetPlayer.canRegisterCharTypeAs('townsfolk'):
                            if action.result == 'trigger': return False
                    elif action.result == 'trigger': return False # spy can't fake the virgin's ability
                
                elif action.type == 'was_executed':
                    if player.actualCharacter.name == 'saint': # the game didn't end because we're solving a puzzle
                        playerConsistent = False
                
                elif action.type == 'was_killed_at_night':
                    if player.actualCharacter.name == 'soldier': playerConsistent = False

                else: raise Exception("Action doesn't make sense.")     
            
            info = player.claimedInfos[testDay]
            if info != None:
                match player.actualCharacter.name:
                    case "washerwoman":
                        if info.player1.canRegisterAs(info.character) == False and info.player2.canRegisterAs(info.character) == False:
                            playerConsistent = False
                    case "librarian":
                        if info.number == 0: 
                            for player in self.circle:
                                if player.actualCharacter.name in {'butler', 'drunk', 'saint'}: # characters who must register as outsiders
                                    playerConsistent = False
                        elif info.player1.canRegisterAs(info.character) == False and info.player2.canRegisterAs(info.character) == False:
                            playerConsistent = False
                    case "investigator":
                        if info.player1.canRegisterAs(info.character) == False and info.player2.canRegisterAs(info.character) == False:
                            playerConsistent = False
                    case "chef":
                        minPairCount = 0
                        maxPairCount = 0
                        for i in range(playerCount):
                            if self.circle[i].canRegisterAsAlignment('evil') and self.circle[(i+1) % playerCount].canRegisterAsAlignment('evil'): 
                                maxPairCount += 1
                                minPairCount += 1
                                if self.circle[i].canRegisterAsAlignment('good') or self.circle[(i+1) % playerCount].canRegisterAsAlignment('good'):
                                    minPairCount -= 1
                        
                        playerConsistent = info.number >= minPairCount and info.number <= maxPairCount
                    case "empath":
                        minCount = 0
                        maxCount = 0

                        # find neighbours
                        leftNeighbour = self.circle[(player.seat + 1) % playerCount]
                        while leftNeighbour.alive[testDay] == False:
                            leftNeighbour = self.circle[(leftNeighbour.seat + 1) % playerCount]
                        rightNeighbour = self.circle[(player.seat - 1) % playerCount]
                        while rightNeighbour.alive[testDay] == False:
                            rightNeighbour = self.circle[(rightNeighbour.seat - 1) % playerCount]

                        if leftNeighbour.canRegisterAsAlignment('evil'): maxCount += 1
                        if not leftNeighbour.canRegisterAsAlignment('good'): minCount += 1

                        if rightNeighbour.canRegisterAsAlignment('evil'): maxCount += 1
                        if not rightNeighbour.canRegisterAsAlignment('good'): minCount += 1
                        
                        playerConsistent = info.number >= minCount and info.number <= maxCount
                    case "fortune teller":
                        if info.player1.actualCharacter.type == 'demon' or info.player2.actualCharacter.type == 'demon': # must register as demon
                            if info.number < 1: playerConsistent = False 
                    case "undertaker":
                        if self.executedPlayers[testDay - 1] == None: playerConsistent = False # undertaker shouldn't be woken without execution
                        elif not self.executedPlayers[testDay - 1].canRegisterAs(info.character):
                            playerConsistent = False
                    case "monk": # considered "info" instead of an action because it's secretly chosen
                        if self.demonKilledPlayers[testDay] == info.player1:
                            playerConsistent = False
                    case "ravenkeeper":
                        if not info.player1.canRegisterAs(info.character): playerConsistent = False

            if player.actualCharacter.name == 'poisoner': remainingPoisons += 1
            if playerConsistent == False: remainingPoisons -= 1
            
        expectedOutsiders = self.characterCounts[playerCount][1]
        if baronExists: expectedOutsiders = expectedOutsiders + 2
        return remainingPoisons >= 0 and expectedOutsiders == outsiderCount

    def getAllSolutions(self, drunksCount=None):
        initialWrongCharList = ['imp'] # wrongCharList will be a unique combination (not permutation) of possible wrongly-claimed characters 
        if drunksCount == 1: initialWrongCharList.append('drunk')
        elif drunksCount == None: 
            return self.getAllSolutions(0) + self.getAllSolutions(1)

        countCheckedConfigs = 0
        consistentCircles = []    
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
                for player in self.circle:
                    player.actualCharacter = self.character(player.claimedCharacter.name)
                for i in range(wrongCharPlayerCount):
                    self.circle[wrongCharPerm[i]].actualCharacter = self.character(wrongCharList[i])
                countCheckedConfigs += 1
                for testDay in range(self.day + 1):
                    allDaysConsistent = True
                    if self.isConsistentDay(testDay) == False: allDaysConsistent = False
                if allDaysConsistent:
                    consistentCircle = []
                    for player in self.circle:
                        consistentCircle.append(player.actualCharacter.name)
                    consistentCircles.append(consistentCircle)
        print("Checked ", countCheckedConfigs, " configurations with ", drunksCount, "drunks.")
        return consistentCircles       



