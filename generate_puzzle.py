# keeps generating single-days until it finds one with a unique imp solution

import clocktower

foundUniqueSolution = False
solvedCt = 0
while foundUniqueSolution == False:
    
    goodCombo = False
    g = None
    while goodCombo == False:
        g1 = clocktower.game("trouble_brewing")
        g1.set_random_players_and_claims(8, 'basic', 2, True) # for 8 players
        # params: player_count, evil_strategy, min_info_roles, includes_you 
        charNames = []
        for p in g1.circle: charNames.append(p.updatedCharacter.name)
        if 'scarlet_woman' not in charNames: 
            goodCombo = True
            g = g1
    g.run_random_night_and_day('basic',1)
    # params: evil_strategy, max_days
    # so far, only single-day generations have been tested :)

    if g.winner == None: 
        solutions = g.getAllSolutions(False,0, True)
        if len(solutions) > 0:
            a = g.get_analytics()
            solvedCt += 1
            if len(a.possible_imps) == 1: # desired number of imp solutions 
                foundUniqueSolution = True
                print(charNames)
                g.print_game_summary()
                print(solutions[0])
            elif a.certain_imp_player_name != None:
                foundUniqueSolution = True
                print('SPECIAL SOLUTION! ' + str(charNames))
                g.print_game_summary()
                for s in solutions: print(s)
            elif solvedCt % 100 == 99: print('solved ' + str(solvedCt) + ' with more possible imps: ' + str(len(a.possible_imps)))

 #Sample output:

# ***GAME SUMMARY:***
# abed (claims slayer)
# beth (claims undertaker)
# chris (claims virgin)
# denny (claims fortune_teller)
# egan (claims chef)
# finn (claims investigator)
# gisele (claims recluse)
# haoyu (claims saint)
#
# NIGHT 0:
# denny (claiming fortune_teller) saw that neither haoyu nor gisele is the imp.
# egan (claiming chef) saw 0 pairs of evil players.
# finn (claiming investigator) saw that haoyu or beth is the poisoner.
# DAY 0:
# abed shot haoyu and nothing happened.
# gisele nominated chris and gisele was executed.