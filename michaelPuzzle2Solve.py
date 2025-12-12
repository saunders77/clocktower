import clocktower

g = clocktower.game("trouble_brewing")

# define players

g.add_player('you', 'investigator')
g.add_player('abed',     'investigator')
g.add_player('beth',    'librarian')
g.add_player('chris',    'fortune_teller')
g.add_player('denny',   'ravenkeeper')
g.add_player('egan',   'monk')
g.add_player('finn',    'recluse')
g.add_player('gisele',    'saint')

# define info and actions

g.players["you"].add_info(1,'scarlet_woman','chris','gisele')
g.players["abed"].add_info(1,'scarlet_woman','you','finn')
g.players["beth"].add_info(0)
g.players["chris"].add_info(0,'imp','beth','abed')

g.print_game_summary()
solutions = g.getAllSolutions()
print("Found ",len(solutions), " solutions:")
for solution in solutions: print(solution)
print(g.get_analytics())

