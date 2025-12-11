import clocktower

# what % of games are solvable at 3-players with no information-sharing until final-three?

# what is the best lie to tell in a given situation?

found = False
checked = 0
uniqueImp = 0
while found == False:
    g = clocktower.game("trouble_brewing")
    g.set_random_players_and_claims(6,None,'basic','basic')
    r=g.run_random_night_and_day('basic','basic')
    if r == False: solutions = []
    else: solutions = g.getAllSolutions(False, 0, True)
    if len(solutions) >= 1:
        checked += 1
        if checked % 100 == 99: print('checked game #' + str(checked) + '. ' + str(uniqueImp) + ' have immediately found the imp.')
        if checked > 2000: found = True 
        a = g.get_analytics()
        if a.certain_imp_player_name != None:

# OUTPUT:

# checked game #1999. 34 have immediately found the imp.