class game:
    def __init__(self, script):
        self.circle = [] # ordered list of players by seat
        self.players = {} # dictionary to reference players by name
        self.day = 0
        self.demonKilledPlayers = [None] # indexed by the day after kill
        self.dailyActions = [[]]

        # for solving: 
        self.queuedWorlds = []

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
            self.minionNames = ['poisoner','spy','scarlet_woman','baron']
            self.combinationsWith4Types = { # used to select minions
                1: [[0],[1],[2],[3]],
                2: [[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]],
                3: [[0,1,2],[0,1,3],[0,2,3],[1,2,3]]
            }
    
    class player:
        def __init__(self, parent, name, claimedCharacterName=None):
            self.name = name
            self.game = parent
            self.seat = 0
            self.isMe = (name == 'you')
            self.claimedCharacter = None
            if(claimedCharacterName): self.claimedCharacter = self.game.character(claimedCharacterName)
            
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
            self.claimedCharacter = self.game.character(claimedCharacterName)

        def add_info(self, number=None, characterName=None, name1=None, name2=None):
            self.claimedInfos[self.game.day] = self.info(self, number, characterName, name1, name2)
        
        def previous_info(self, nightNumber, number=None, characterName=None, name1=None, name2=None):
            # nightNumber starts with the 0th night and corresponds to the day after
            self.claimedInfos[nightNumber] = self.info(self, number, characterName, name1, name2)

        def add_action(self, actionType=None, targetName=None, result=None):
            self.actions[self.game.day].append(self.action(self, actionType, targetName, result))

        def nominate(self, nominee, result=None):
            self.game.players[nominee].add_action('was_nominated', self.name, result)
        
        def slay(self, target, result):
            self.add_action('slay', target, result)

        def executed_by_vote(self):
            self.add_action('was_executed')

        def was_killed_at_night(self):
            self.game.demonKilledPlayers.append(self)

        def set_character(self, characterName): # to be used only during solving
            self.actualCharacter = self.game.character(characterName)
            self.updatedCharacter = self.game.character(characterName)
        
        def canRegisterAsChar(self, character):
            if character == self.updatedCharacter: return True
            if self.updatedCharacter.name == 'recluse' and character.alignment == 'evil': return True
            if self.updatedCharacter.name == 'spy' and character.alignment == 'good': return True
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
                self.number = number
                self.character = None
                if(characterName): self.character = self.player.game.character(characterName)
                self.player1 = None
                if(name1): self.player1 = self.player.game.players[name1]
                self.player2 = None
                if(name2): self.player2 = self.player.game.players[name2]

        class action:
            def __init__(self, parent, actionType, targetName=None, result=None):
                self.player = parent
                self.type = actionType
                self.targetPlayer = None
                if(targetName): self.targetPlayer = self.player.game.players[targetName]
                self.result = result
                self.player.game.dailyActions[-1].append(self)
    
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
                case 'fortune_teller' | 'fortuneteller': return 'townsfolk'
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
                case 'scarlet_woman': return 'minion'
                case 'baron': return 'minion'
                case 'imp': return 'demon'
                case 'dead_imp': return 'demon'
                case _: return None

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

            s = 'IMP: ' + demons['imp']
            if demons['imp'] in self.transformationsDict.keys(): 
                s += ' (was ' + self.transformationsDict[demons['imp']][0] + ')'
            s += '\n\t'
            for deadDemonKey in deadDemons.keys():
                s += deadDemonKey + ': ' + deadDemons[deadDemonKey] + ', '
            s = s[:-2] + '\n\t'
            for minionKey in minions.keys():
                s += minionKey + ': ' + minions[minionKey] + ', '
            s = s[:-2] + '\n\t'
            for drunkKey in drunks.keys():
                s += drunkKey + ': ' + drunks[drunkKey] + ', '
            s = s[:-2] + '\n\t'
            for otherKey in others.keys():
                s += otherKey + ': ' + others[otherKey] + ', ' 

            return s[:-2]         

    def add_player(self, name, claimedCharacterName=None):
        self.circle.append(self.player(self, name, claimedCharacterName))
        self.circle[-1].seat = len(self.circle) - 1
        self.players[name] = self.circle[-1]
    
    def add_players(self, names):
        for name in names:
            self.add_player(name)

    def next_day(self):
        self.day += 1
        self.dailyActions.append([])
        if len(self.demonKilledPlayers) < self.day: self.demonKilledPlayers.append(None)
        for player in self.circle:
            player.actions.append([])
            player.claimedInfos.append(None)

    def findPlayerByUpdatedCharacter(self, characterName):
        for player in self.circle:
            if player.updatedCharacter == self.character(characterName): return player
        return None

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
        outsiderCount = 0
        self.characterNames = set()
        self.countLivingPlayers = playerCount
        self.livingMinions = []
        self.executedPlayers = []
        self.replacedMinionNames = []
        drunk = None
        virginNeverNominated = True
        
        for player in self.circle:
            player.alive = True
            if player.actualCharacter.name in self.characterNames: return False
            self.characterNames.add(player.actualCharacter.name)
            if player.isMe and player.actualCharacter.name not in {'drunk', player.claimedCharacter.name}:
                return False
            elif player.actualCharacter.name == 'drunk':
                outsiderCount += 1
                if player.claimedCharacter.type != 'townsfolk': return False
                drunk = player
            elif player.actualCharacter.type == 'outsider': outsiderCount += 1
            elif player.actualCharacter.type == 'minion': self.livingMinions.append(player)
        
        if drunk != None and drunk.claimedCharacter.name in self.characterNames: return False # drunk can't think they're a character that's actually in play

        expectedOutsiders = self.characterCounts[playerCount][1]
        if 'baron' in self.characterNames: expectedOutsiders = expectedOutsiders + 2
        if expectedOutsiders != outsiderCount: return False

        def killedPlayer(player, nightDeath, queuedReplacementMinionNames):
            
            self.countLivingPlayers -= 1
            player.alive = False
            if nightDeath and player.updatedCharacter.name == 'imp':
                # check if there's a queue
                if len(queuedReplacementMinionNames) > 0:
                    # just use the first minion in the queue
                    replacedMinionName = queuedReplacementMinionNames.pop(0)
                    self.characterNames.remove(replacedMinionName)
                    self.findPlayerByUpdatedCharacter(replacedMinionName).updatedCharacter = self.character('imp')
                    player.updatedCharacter = self.character('dead_imp')
                    for m in range(len(self.livingMinions)):
                        if self.livingMinions[m] == replacedMinion: self.livingMinions.pop(m)
                else:
                    # select any minion
                    
                    if len(self.livingMinions) < 1: return False # the imp can't kill itself if no minions remain
                    replacedMinion = self.livingMinions.pop()
                    self.replacedMinionNames.append(replacedMinion.updatedCharacter.name)
                    self.characterNames.remove(replacedMinion.updatedCharacter.name)
                    replacedMinion.updatedCharacter = self.character('imp')
                    player.updatedCharacter = self.character('dead_imp')

                    # enqueue each alternative choice
                    
                    if len(self.livingMinions) > 0:
                        characterNamesList = []
                        fortuneTellerRedHerringSeat = None
                        for p in self.circle:
                            characterNamesList.append(p.actualCharacter.name)
                            if p.isFortuneTellerRedHerring: fortuneTellerRedHerringSeat = p.seat
                    
                    while len(self.livingMinions) > 0:
                        # create a new world to queue, with a list of starting characters and a queue of replacements
                        minionNamesQueue = []
                        for name in self.replacedMinionNames:
                            minionNamesQueue.append(name)
                        minionNamesQueue.append(self.livingMinions.pop().updatedCharacter.name)
                        self.queuedWorlds.append(self.world(self, characterNamesList, fortuneTellerRedHerringSeat, minionNamesQueue))
            elif player.updatedCharacter.name == 'imp': # imp was still killed suring the day and game is still going. Replacement must be scarlet woman
                scarletWoman = self.findPlayerByUpdatedCharacter('scarlet_woman')
                if self.countLivingPlayers < 4 or scarletWoman == None or scarletWoman.alive == False: return False  # after imp killed during the day, scarlet woman needs 4+ players to still live
                else:
                    self.characterNames.remove('scarlet_woman')
                    for m in range(len(self.livingMinions)):
                        if self.livingMinions[m] == scarletWoman: self.livingMinions.pop(m)
                    scarletWoman.updatedCharacter = self.character('imp')
                player.updatedCharacter = self.character('dead_imp')
            elif player.updatedCharacter.type == 'minion':
                for m in range(len(self.livingMinions)):
                    if self.livingMinions[m] == player: self.livingMinions.pop(m)
            
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
                            minPairCount = 0
                            maxPairCount = 0
                            for i in range(playerCount):
                                if self.circle[i].canRegisterAsAlignment('evil') and self.circle[(i+1) % playerCount].canRegisterAsAlignment('evil'): 
                                    maxPairCount += 1
                                    minPairCount += 1
                                    if self.circle[i].canRegisterAsAlignment('good') or self.circle[(i+1) % playerCount].canRegisterAsAlignment('good'):
                                        minPairCount -= 1       
                            if info.number < minPairCount or info.number > maxPairCount: poisonedNames.add(player.name)
                        case "empath":
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
                            elif info.player1.isFortuneTellerRedHerring: 
                                maxCount = 1
                                if info.player1.mustRegisterAsAlignment('good'): minCount = 1
                            elif info.player2.isFortuneTellerRedHerring: 
                                maxCount = 1
                                if info.player2.mustRegisterAsAlignment('good'): minCount = 1
                            elif info.player1.canRegisterAsType('demon') or info.player2.canRegisterAsType('demon'): maxCount = 1
                            else: # this spy/recluse checking may leave in more solutions than what are stricly possile because it's difficult to keep track of moving red herrings. No solutions will be missed, however.
                                recluse = self.findPlayerByUpdatedCharacter('recluse')
                                if recluse != None and recluse .isFortuneTellerRedHerring: maxCount = 1
                                else:
                                    spy = self.findPlayerByUpdatedCharacter('spy')
                                    if spy != None and spy.isFortuneTellerRedHerring: maxCount = 1
                            if info.number < minCount or info.number > maxCount: poisonedNames.add(player.name)
                        case "undertaker":
                            if len(self.executedPlayers) == 0: return False # undertaker shouldn't be woken without execution
                            elif not self.executedPlayers[-1].canRegisterAsChar(info.character):
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

        return True

    def getAllSolutions(self, drunksCount=None):
        initialWrongCharList = ['imp'] # wrongCharList will be a unique combination (not permutation) of possible wrongly-claimed characters 
        if drunksCount == 1: initialWrongCharList.append('drunk')
        elif drunksCount == None:
            return self.getAllSolutions(0) + self.getAllSolutions(1)

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
                    player.set_character(player.claimedCharacter.name)
                    player.isFortuneTellerRedHerring = False
                    if player.claimedCharacter.name in {'fortune_teller','fortuneteller'}: fortuneTellerClaimed = True
                for i in range(wrongCharPlayerCount):
                    self.circle[wrongCharPerm[i]].set_character(wrongCharList[i])
                countCheckedConfigs += 1
                if fortuneTellerClaimed:
                    for player in self.circle:
                        if player.canRegisterAsAlignment('good'):
                            player.isFortuneTellerRedHerring = True
                            recordIfConsistent()
                else: recordIfConsistent()

        # check other queued worlds:
        while len(self.queuedWorlds) > 0:
            world = self.queuedWorlds.pop()
            for player in self.circle:
                player.set_character(world.startingCharacterNamesList[player.seat])
                player.isFortuneTellerRedHerring = False
                if player.seat == world.fortuneTellerRedHerringSeat: player.isFortuneTellerRedHerring = True
            recordIfConsistent(world.replacementMinionNamesQueue)

        print("Checked ", countCheckedConfigs, " configurations with ", drunksCount, "drunks.")
        
        return solutionWorlds

clocktower = game # back-compat