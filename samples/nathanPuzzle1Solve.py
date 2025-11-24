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
g.players["finn"].add_info(0,'demon','egan','denny')
g.players["gisele"].add_action("slay", "chris", None)
#g.players["denny"].add_info(1)

solutions = g.getAllSolutions()
#print("Found ",len(solutions), " solutions:")
#for solution in solutions: print(solution)
print(solutions)