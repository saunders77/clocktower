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
        g.set_random_players_and_claims(7, 'basic',2,False) # for 7 players
        charNames = []
        for p in g.circle:
            if p.updatedCharacter.name == 'drunk' and p.claimedCharacter.name in {'librarian'}: 
                goodCombo = True
                drunk = p
            elif p.updatedCharacter.name == 'imp': imp = p
    g.run_random_night_and_day('basic',None,1)

    if g.winner == None:
        totalDrunks += 1
        fakeRole = drunk.claimedCharacter.name 
        info = drunk.claimedInfos[0] 
        number = info.number 
        char = info.character 
        if char == None:
            datapoint = (fakeRole, number, None, None, None, None, None)
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
            if allowed != 'disallowed': onlyGood = None

            # did you ping the recluse?
            if player1char == 'recluse' or player2char == 'recluse': recluseIncluded = 'recluseIncluded'
            else: recluseIncluded = 'noRecluse'

            # is the imp included?
            if player1char == 'imp' or player2char == 'imp': impIncluded = 'impIncluded'
            else: impIncluded = 'noImp'
            
            datapoint = (fakeRole, number, allowed, accurate, onlyGood, None, None)
            print('librarian info is: ' + character + ' and actual registered roles are ' + player1char + '/' + player2char + '. Assessment is ' + allowed + '/' + accurate)
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

# OUTPUT for 8 players:

#DATA:

#3111;   avg imps: 5.3 +/- 0.1;  avg solutions: 46.1 +/- 1.9;    setup: ('librarian', 1, 'disallowed', 'inaccurate', 'notOnlyGood', None, None)
#2999;   avg imps: 5.2 +/- 0.1;  avg solutions: 47.6 +/- 2.0;    setup: ('librarian', 1, 'disallowed', 'inaccurate', 'onlyGood', None, None)
#960;    avg imps: 5.3 +/- 0.1;  avg solutions: 42.8 +/- 3.1;    setup: ('librarian', 0, None, None, None, None, None)
#493;    avg imps: 6.0 +/- 0.1;  avg solutions: 41.0 +/- 2.6;    setup: ('librarian', 1, 'allowed', 'accurate', None, None, None)
#337;    avg imps: 5.7 +/- 0.1;  avg solutions: 70.0 +/- 7.3;    setup: ('librarian', 1, 'allowed', 'inaccurate', None, None, None)