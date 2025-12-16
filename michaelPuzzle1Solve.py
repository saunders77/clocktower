import clocktower

g = clocktower.game("trouble_brewing")

# define players

g.add_player('abed',     'slayer')
g.add_player('beth',    'undertaker')
g.add_player('chris',    'virgin')
g.add_player('denny',   'fortune_teller')
g.add_player('egan',   'chef')
g.add_player('finn',    'investigator')
g.add_player('gisele',    'recluse')
g.add_player('haoyu',  'saint')

# define info and actions

g.players["denny"].add_info(0,'imp','haoyu','gisele')
g.players["egan"].add_info(0)
g.players["finn"].add_info(1,'poisoner','haoyu','beth')
g.players["abed"].slay('haoyu', None)
g.players["gisele"].nominate('chris', 'trigger')

g.print_game_summary()
#solutions = g.getAllSolutions()
#print("Found ",len(solutions), " solutions:")
#for solution in solutions: print(solution)
#print(g.get_analytics())

