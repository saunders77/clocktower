# keeps generating single-days until it finds one with a unique imp solution

import clocktower

foundUniqueSolution = False

while foundUniqueSolution == False:
    g = clocktower.game("trouble_brewing")
    g.set_random_players_and_claims(8, 'basic', 2) # for 8 players
    gameActive = True
    while g.active:
        g.run_random_night_and_day('basic',1)
        if g.active: g.next_day()
    if g.winner == None: 
        solutions = g.getAllSolutions(False, 0, True)
        if len(solutions) > 0:
            a = g.get_analytics()
            if len(a.possible_imps) == 1: # desired number of imp solutions 
                foundUniqueSolution = True
                g.print_game_summary()

#Sample output:

#***GAME SUMMARY:***
#player0 (claims slayer)
#player1 (claims undertaker)
#player2 (claims virgin)
#player3 (claims fortune_teller)
#player4 (claims chef)
#player5 (claims investigator)
#player6 (claims recluse)
#player7 (claims saint)
#
#NIGHT 0:
#player3 (claiming fortune_teller) saw that neither player7 nor player6 is the imp.
#player4 (claiming chef) saw 0 pairs of evil players.
#player5 (claiming investigator) saw that player7 or player1 is the poisoner.
#DAY 0:
#player0 shot player7 and nothing happened.
#player6 nominated player2 and player6 was executed.