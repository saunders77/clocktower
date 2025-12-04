import clocktower

g = clocktower.game("trouble_brewing")

# define players

g.add_player('you',     'empath')
g.add_player('abed',    'librarian')
g.add_player('beth',    'chef')
g.add_player('chris',   'saint')
g.add_player('denny',   'recluse')
g.add_player('egan',    'washerwoman')
g.add_player('finn',    'fortune_teller')
g.add_player('gisele',  'slayer')

# define info and actions

g.players["you"].add_info(0)
g.players["abed"].add_info(1,'drunk','denny','chris')
g.players["beth"].add_info(2)
g.players["egan"].add_info(1,'librarian','abed','you')
g.players["finn"].add_info(0,'imp','egan','denny')
g.players["gisele"].slay("chris", None)
g.players["denny"].add_info(1)

solutions = g.getAllSolutions()
print("Found ",len(solutions), " solutions:")
for solution in solutions: print(solution)
print(g.get_analytics())

### output ###
# 
# Checked  224  configurations with  0 drunks.
# Checked  1344  configurations with  1 drunks.
# Found  7  solutions:
# IMP: beth
#         poisoner: chris
#         empath: you, librarian: abed, recluse: denny, washerwoman: egan, fortune_teller: finn, slayer: gisele
# IMP: beth
#         spy: chris
#         empath: you, librarian: abed, recluse: denny, washerwoman: egan, fortune_teller: finn, slayer: gisele
# IMP: beth
#         poisoner: denny
#         empath: you, librarian: abed, saint: chris, washerwoman: egan, fortune_teller: finn, slayer: gisele
# IMP: beth
#         spy: denny
#         empath: you, librarian: abed, saint: chris, washerwoman: egan, fortune_teller: finn, slayer: gisele
# IMP: beth
#         baron: egan
#         drunk: abed
#         empath: you, saint: chris, recluse: denny, fortune_teller: finn, slayer: gisele
# IMP: egan
#         baron: finn
#         drunk: abed
#         empath: you, chef: beth, saint: chris, recluse: denny, slayer: gisele
# IMP: finn
#         baron: egan
#         drunk: abed
#         empath: you, chef: beth, saint: chris, recluse: denny, slayer: gisele