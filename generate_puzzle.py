# keeps generating single-days until it finds one with a unique imp solution

import clocktower

foundUniqueSolution = False

while foundUniqueSolution == False:
    g = clocktower.game("trouble_brewing")
    g.set_random_players_and_claims(8, 'basic', 2, False) # for 8 players
    # params: player_count, evil_strategy, min_info_roles, includes_you 
    gameActive = True
    while g.active:
        g.run_random_night_and_day('basic',1)
        # params: evil_strategy, max_days
        if g.active: g.next_day()
    if g.winner == None: 
        solutions = g.getAllSolutions(False, 0, True)
        if len(solutions) > 0:
            a = g.get_analytics()
            if len(a.possible_imps) == 1: # desired number of imp solutions 
                foundUniqueSolution = True
                g.print_game_summary()

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
# gisele nominated beth and gisele was executed.