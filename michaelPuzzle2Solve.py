import clocktower

g = clocktower.game("trouble_brewing")

# define players

g.add_player('you', 'saint')
g.add_player('abed',     'fortune_teller')
g.add_player('beth',    'soldier')
g.add_player('chris',    'librarian')
g.add_player('denny',   'virgin')
g.add_player('egan',   'empath')
g.add_player('finn',    'recluse')
g.add_player('gisele',    'butler')

# define info and actions

g.players["abed"].add_info(0,'imp','gisele','beth')
g.players["chris"].add_info(0)
g.players["egan"].add_info(1)
g.players["chris"].nominate('denny','trigger')

g.print_game_summary()
solutions = g.getAllSolutions()
print("Found ",len(solutions), " solutions:")
for solution in solutions: print(solution)
print(g.get_analytics())

