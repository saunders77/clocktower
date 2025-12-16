# What's the best info give to the drunk washerwoman/librarian/investigator/fortune teller?

import clocktower, statistics
totalDrunks = 0
results = {}
gameWon = 0
noSolutions = 0
while totalDrunks < 20000:
    goodCombo = False
    g = None
    drunk = None
    imp = None
    minion = None
    while goodCombo == False:
        g = clocktower.game("trouble_brewing")
        g.set_random_players_and_claims(8, 'basic', 2,False) # for 8 players
        charNames = []
        for p in g.circle:
            if p.updatedCharacter.name == 'drunk' and p.claimedCharacter.name in {'fortune_teller'}: 
                goodCombo = True
                drunk = p
            elif p.updatedCharacter.name == 'imp': imp = p
    g.run_random_night_and_day('basic',None,1)

    if g.winner == None:
        totalDrunks += 1
        fakeRole = drunk.claimedCharacter.name 
        info = drunk.claimedInfos[0] 
        #number = info.number 
        #char = info.character 
        char = None
        if char == None:
            datapoint = None
            phrase = None
            #raise Exception('no char shown for investigator')
        else:
            character = char.name # will be measured   
            player1char = info.player1.updatedCharacter.name # will be measured
            player2char = info.player2.updatedCharacter.name # will be measured

            # did you get allowed-by-rules information?
            if info.player1.canRegisterAsChar(character) or info.player2.canRegisterAsChar(character): allowed = 'allowed'
            else: allowed = 'disallowed'

            # did you get accurate literal information about the actual characters?
            if character not in {player1char, player2char}: accurate = 'inaccurate'
            else: accurate = 'accurate'

            # did you ping only good?
            if info.player1.updatedCharacter.alignment == 'good' and info.player2.updatedCharacter.alignment == 'good': onlyGood = 'onlyGood'
            else: onlyGood = 'notOnlyGood'

            # did you ping the recluse?
            if player1char == 'recluse' or player2char == 'recluse': recluseIncluded = 'recluseIncluded'
            else: recluseIncluded = 'noRecluse'

            if info.player1.updatedCharacter.type == 'minion' or info.player2.updatedCharacter.type == 'minion':
                showMinion = True
            else: showMinion = False

            # is the imp included?
            if player1char == 'imp' or player2char == 'imp': impIncluded = 'impIncluded'
            else: impIncluded = 'noImp'

            phrase = None
            if number == 1:
                if impIncluded == 'impIncluded':
                    phrase = 'register the demon correctly'
                else:
                    if accurate == 'inaccurate' and allowed =='allowed':
                        phrase = 'register the recluse as a demon'
                    else:
                        phrase = 'register a demon among 2 NON-demons (not recluse)'
            else:
                if impIncluded == 'impIncluded':
                    phrase = 'register the demon as NOT the demon'
                else:
                    phrase = 'register NO demon among 2 NON-demons'


    
            
            datapoint = phrase
        # pretend the imp is good, then measure the number of possible imps and the number of possible solutions
        g.findPlayerByUpdatedCharacter('imp').isMe = True
        solutions = g.getAllSolutions(False,0, True)
        if len(solutions) > 0:
            a = g.get_analytics()
            impsCount = len(a.possible_imps)
            solutionsCount = len(solutions)
        else:
            impsCount = 0
            solutionsCount = 0
        if datapoint not in results: results[datapoint] = [[],[]]
        results[datapoint][0].append(impsCount)
        results[datapoint][1].append(solutionsCount) 
        
        if totalDrunks % 50 == 0: 
            print('\nDATA:\n')
            for r in results.keys():
                if len(results[r][0]) >= 2:
                    oline = ''
                    oline += str(len(results[r][0])) + ';\t'
                    oline += 'avg imps: ' + str(round(statistics.mean(results[r][0]),1)) + ' +/- ' + str(round(statistics.stdev(results[r][0])*1.96/(len(results[r][0])**0.5),1)) + ';\t'
                    oline += 'avg solutions: ' + str(round(statistics.mean(results[r][1]),1)) + ' +/- ' + str(round(statistics.stdev(results[r][1])*1.96/(len(results[r][1])**0.5),1)) + ';\t'
                    oline += 'setup: ' + str(r)
                    print(oline)

# OUTPUT:

# DATA:

# 2258;   avg imps: 5.8 +/- 0.1;  avg solutions: 59.1 +/- 2.5;    setup: register NO demon among 2 NON-demons
# 726;    avg imps: 5.9 +/- 0.1;  avg solutions: 66.5 +/- 5.5;    setup: register the demon as NOT the demon
# 1898;   avg imps: 6.1 +/- 0.1;  avg solutions: 74.6 +/- 3.5;    setup: register a demon among 2 NON-demons
# 730;    avg imps: 6.1 +/- 0.1;  avg solutions: 79.6 +/- 6.0;    setup: register the demon correctly
# 188;    avg imps: 6.2 +/- 0.2;  avg solutions: 43.2 +/- 4.8;    setup: register the recluse as a demon