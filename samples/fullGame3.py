# https://www.youtube.com/watch?v=EsTXhFKtER8

import clocktower

g = clocktower.game("trouble_brewing")

# define players

g.add_player('doug', 'virgin' )
g.add_player('ben', 'butler')
g.add_player('carley', 'empath')
g.add_player('theo', 'washerwoman')
g.add_player('marianna', 'recluse')
g.add_player('lachlan', 'slayer')
g.add_player('hayley', 'chef')
g.add_player('filip', 'monk')

# define claims and info (claims can happen at any time before getting solutions)

g.players['theo'].add_info(1, 'slayer','lachlan','ben')
g.players['carley'].add_info(0)
g.players['hayley'].add_info(1)

g.players['filip'].nominate('doug','trigger')

g.next_day()

g.players['lachlan'].was_killed_at_night()
g.players['carley'].add_info(0)

g.players['theo'].slay('carley',None)
g.players['doug'].nominate('hayley',None)
g.players['ben'].nominate('ben',None)
g.players['hayley'].nominate('theo',None)
g.players["ben"].executed_by_vote()

g.next_day()

g.players['marianna'].was_killed_at_night()
g.players['carley'].add_info(0)

g.next_day()

g.players['carley'].was_killed_at_night()


# get solutions

solutions = g.getAllSolutions(False, 2)
print("Found ",len(solutions), " solutions:")
for solution in solutions: print(solution)
print(g.get_analytics())

# analytics output
# 10 valid configurations:
# {'doug': 0.0, 'ben': 0.0, 'carley': 0.0, 'theo': 0.2, 'marianna': 0.0, 'lachlan': 0.0, 'hayley': 0.8, 'filip': 0.0}
# 7 valid configurations without lucky poisoners:
# {'doug': 0.0, 'ben': 0.0, 'carley': 0.0, 'theo': 0.0, 'marianna': 0.0, 'lachlan': 0.0, 'hayley': 1.0, 'filip': 0.0}