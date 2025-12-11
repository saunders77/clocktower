import clocktower

g = clocktower.game("trouble_brewing")

# define players

g.add_player('you',     'chef')
g.add_player('abed',    'empath')
g.add_player('beth',    'librarian')
g.add_player('chris',   'recluse')
g.add_player('denny',   'slayer')
g.add_player('egan',    'saint')
g.add_player('finn',    'virgin')
g.add_player('gisele',  'investigator')

# define info and actions

g.players["you"].add_info(1)
g.players["abed"].add_info(2)
g.players["beth"].add_info(0)
g.players["denny"].slay('chris', 'trigger')
g.players["denny"].nominate('finn', None)
g.players["gisele"].add_info(1, 'poisoner', 'beth', 'finn')

g.print_game_summary()
solutions = g.getAllSolutions()
print("Found ",len(solutions), " solutions:")
for solution in solutions: print(solution)
print(g.get_analytics())


### output ###
#
# Checked  224  configurations with  0 drunks.
# Checked  1344  configurations with  1 drunks.
# Found  1  solutions:
# IMP: egan
#         poisoner: finn
#         chef: you, empath: abed, librarian: beth, recluse: chris, slayer: denny, investigator: gisele