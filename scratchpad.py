import clocktower

# what % of games are solvable at 3-players with no information-sharing until final-three?

# what is the best lie to tell in a given situation?

g = clocktower.game("trouble_brewing")
g.set_random_players_and_claims(8,'basic',2, True)
r=g.run_random_night_and_day('basic',1)
charNames = []
for p in g.circle: charNames.append(p.updatedCharacter.name)
print(charNames)
g.print_game_summary()
if g.winner == None: 
    solutions = g.getAllSolutions(False,0, True)
    #for s in solutions: print(s)
    print(solutions[0])

