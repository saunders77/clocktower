# https://www.youtube.com/watch?v=AJLrY7N6VLo

import clocktower

g = clocktower.game("trouble_brewing")

# define players

g.add_players(['george', 'ellen', 'raj', 'lorinda', 'jc', 'alex', 'daniel', 'amy', 'claire'])

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

g.players["claire"].nominate('george', None)
g.players["george"].nominate('claire', None)
g.players["daniel"].nominate('jc', None)
g.players["amy"].nominate('daniel', None)
g.players["daniel"].executed_by_vote()

g.next_day()

g.players["raj"].was_killed_at_night()

g.players["raj"].claim('undertaker')
g.players["amy"].add_info(1)
g.players["claire"].claim('ravenkeeper')
g.players["alex"].claim('butler')
g.players["daniel"].claim("washerwoman")
g.players["daniel"].previous_info(0, 1,'chef','alex','ellen')
g.players["lorinda"].claim("slayer")
g.players["ellen"].claim('chef')
g.players["ellen"].previous_info(0,0)


g.players["claire"].nominate('amy', None)
g.players["amy"].nominate('claire', None)
g.players["claire"].executed_by_vote()

g.next_day()

g.players["lorinda"].was_killed_at_night()
g.players["amy"].add_info(1)
g.players["amy"].nominate('amy', None)
g.players["george"].nominate('jc', None)
g.players["jc"].nominate('george', None)
g.players["jc"].executed_by_vote()

g.next_day()
g.players["ellen"].was_killed_at_night()

# get solutions

solutions = g.getAllSolutions()
print("Found ",len(solutions), " solutions:")
for solution in solutions: print(solution)
