import clocktower

c = clocktower.clocktower("trouble brewing")

# define players

c.add_player('you',     'empath')
c.add_player('abed',    'librarian')
c.add_player('beth',    'chef')
c.add_player('chris',   'saint')
c.add_player('denny',   'recluse')
c.add_player('egan',    'washerwoman')
c.add_player('finn',    'fortune teller')
c.add_player('gisele',  'slayer')

# define info and actions

c.players["you"].add_info(0)
c.players["abed"].add_info(1,'drunk','denny','chris')
c.players["beth"].add_info(2)
c.players["egan"].add_info(1,'librarian','abed','you')
c.players["finn"].add_info(0,'demon','egan','denny')
c.players["gisele"].add_action("slay", "chris", None)

solutions = c.getAllSolutions()
print("Found ",len(solutions), " solutions:")
for solution in solutions: print(solution)
