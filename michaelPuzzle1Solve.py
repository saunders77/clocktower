import clocktower

g = clocktower.game("trouble_brewing")

# define players

g.add_player('player0',     'slayer')
g.add_player('player1',    'undertaker')
g.add_player('player2',    'virgin')
g.add_player('player3',   'fortune_teller')
g.add_player('player4',   'chef')
g.add_player('player5',    'investigator')
g.add_player('player6',    'recluse')
g.add_player('player7',  'saint')

# define info and actions

g.players["player3"].add_info(0,'imp','player7','player6')
g.players["player4"].add_info(0)
g.players["player5"].add_info(1,'poisoner','player7','player1')
g.players["player0"].slay('player7', None)
g.players["player6"].nominate('player2', 'trigger')

g.print_game_summary()
solutions = g.getAllSolutions()
print("Found ",len(solutions), " solutions:")
for solution in solutions: print(solution)
print(g.get_analytics())