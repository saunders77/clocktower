import clocktower

g = clocktower.game("trouble_brewing")

# define players

g.add_player('you', 'chef')
g.add_player('abed',     'slayer')
g.add_player('beth',    'empath')
g.add_player('chris',    'virgin')
g.add_player('denny',   'butler')
g.add_player('egan',   'recluse')
g.add_player('finn',    'chef')
g.add_player('gisele',    'librarian')

# define info and actions

g.players["you"].add_info(1)
g.players["beth"].add_info(0)
g.players["finn"].add_info(1)
g.players["gisele"].add_info(1,'recluse','egan','finn')
g.players["abed"].slay('denny',None)
g.players["finn"].nominate('chris','trigger')

g.print_game_summary()
solutions = g.getAllSolutions()
print("Found ",len(solutions), " solutions:")
for solution in solutions: print(solution)
print(g.get_analytics())

['empath', 'monk', 'drunk', 'imp', 'washerwoman', 'investigator', 'librarian', 'poisoner']
***GAME SUMMARY:***
you (claims empath)
abed (claims monk)
beth (claims virgin)
chris (claims recluse)
denny (claims washerwoman)
egan (claims investigator)
finn (claims librarian)
gisele (claims chef)

NIGHT 0:
you (claiming empath) saw 2 evil neighbours.
denny (claiming washerwoman) saw that finn or chris is the librarian.
egan (claiming investigator) saw that gisele or you is the poisoner.
finn (claiming librarian) saw that beth or gisele is the drunk.
gisele (claiming chef) saw 1 pairs of evil players.
DAY 0:
denny nominated beth.