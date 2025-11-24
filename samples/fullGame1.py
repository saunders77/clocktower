# https://www.youtube.com/watch?v=AJLrY7N6VLo

import clocktower

g = clocktower.game("trouble_brewing")

# define players

g.add_player('george')
g.add_player('ellen')
g.add_player('raj')
g.add_player('lorinda')
g.add_player('jc')
g.add_player('alex')
g.add_player('daniel')
g.add_player('amy')
g.add_player('claire')

# define claims and info (claims can happen at any time before getting solutions)

g.players["amy"].claim('empath')
g.players["amy"].add_info(1)
g.players["ellen"].claim('chef')
g.players["ellen"].add_info(0)
g.players["raj"].claim('monk')
g.players["claire"].claim('slayer')
g.players["jc"].claim('mayor')
g.players["alex"].claim('butler')
g.players["raj"].claim('investigator')
g.players["george"].claim('recluse')

g.players["daniel"].add_action("was_executed")

g.next_day()

g.players["raj"].add_action("was_killed_at_night")
g.players["raj"].claim('undertaker')
g.players["amy"].add_info(1)
g.players["claire"].claim('ravenkeeper')
g.players["alex"].claim('butler')
g.players["daniel"].claim("washerwoman")
g.players["lorinda"].claim("slayer")

g.players[]



# get solutions

solutions = g.getAllSolutions()
print("Found ",len(solutions), " solutions:")
for solution in solutions: print(solution)