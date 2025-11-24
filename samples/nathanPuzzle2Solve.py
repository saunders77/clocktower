import clocktower

g = clocktower.game("trouble_brewing")

# define players

g.add_player('you',     'empath')
g.add_player('abed',    'librarian')
g.add_player('beth',    'saint')
g.add_player('chris',   'slayer')
g.add_player('denny',   'investigator')
g.add_player('egan',    'washerwoman')
g.add_player('finn',    'virgin')
g.add_player('gisele',  'chef')

# define info and actions

g.players["you"].add_info(2)
g.players["abed"].add_info(1,'drunk','you','gisele')
g.players["chris"].add_action('slay', 'abed', None)
g.players["denny"].add_info(1, 'poisoner', 'chris', 'gisele')
g.players["egan"].add_info(1,'librarian','abed','finn')
g.players["finn"].add_action('was_nominated','abed', None)
g.players["gisele"].add_info(1)


solutions = g.getAllSolutions()
print("Found ",len(solutions), " solutions:")
for solution in solutions: print(solution)

### output ###
#
# Checked  224  configurations with  0 drunks.
# Checked  1344  configurations with  1 drunks.
# Found  2  solutions:
# IMP: beth
#         poisoner: chris
#         drunk: you
#         librarian: abed, investigator: denny, washerwoman: egan, virgin: finn, chef: gisele
# IMP: beth
#         poisoner: gisele
#         drunk: you
#         librarian: abed, slayer: chris, investigator: denny, washerwoman: egan, virgin: finn