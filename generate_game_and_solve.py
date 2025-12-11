# generates a single day-long game and solves

import clocktower

g = clocktower.game("trouble_brewing")
g.set_random_players_and_claims(8, 'basic', 2)
gameActive = True
while g.active:
    g.run_random_night_and_day('basic',1)
    if g.active: g.next_day()

g.print_game_summary()
if g.winner == None: solutions = g.getAllSolutions(False, 2, True)
for solution in solutions: print(solution)
if len(solutions) >= 1:
    a = g.get_analytics()
    print(a)

# Sample output:

#***GAME SUMMARY:***
#player0 (claims virgin)
#player1 (claims soldier)
#player2 (claims recluse)
#player3 (claims undertaker)
#player4 (claims investigator)
#player5 (claims empath)
#player6 (claims butler)
#player7 (claims ravenkeeper)

#NIGHT 0:
#player4 (claiming investigator) saw that player2 or player0 is the spy.
#player5 (claiming empath) saw 2 evil neighbours.
#DAY 0:
#player2 nominated player0 and player2 was executed.

#IMP: player5
#        spy: player2
#        virgin: player0, soldier: player1, undertaker: player3, investigator: player4, butler: player6, ravenkeeper: player7
#IMP: player6
#        spy: player2
#        drunk: player5
#        virgin: player0, soldier: player1, undertaker: player3, investigator: player4, ravenkeeper: player7
#imp probabilities across 2 valid configurations:
#{'player0': 0.0, 'player1': 0.0, 'player2': 0.0, 'player3': 0.0, 'player4': 0.0, 'player5': 0.5, 'player6': 0.5, 'player7': 0.0}
#imp probabilities across 2 valid configurations without lucky 1st-night poisoners:
#{'player0': 0.0, 'player1': 0.0, 'player2': 0.0, 'player3': 0.0, 'player4': 0.0, 'player5': 0.5, 'player6': 0.5, 'player7': 0.0}
#The following players can accuse with certainty: player5 accuses player6. player6 accuses player5.