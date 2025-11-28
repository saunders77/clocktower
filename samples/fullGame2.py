# https://www.youtube.com/watch?v=0aDt7n06dRM

import clocktower

g = clocktower.game("trouble_brewing")

# define players

g.add_player('ekin', 'chef' )
g.add_player('fran', 'empath')
g.add_player('kota', 'washerwoman')
g.add_player('dem', 'slayer')
g.add_player('reznora', 'soldier')
g.add_player('ryback', 'mayor')
g.add_player('tapir', 'recluse')
g.add_player('bruce', 'undertaker')
g.add_player('art', 'fortune_teller')
g.add_player('josh', 'monk' )
g.add_player('malashaan', 'investigator')
g.add_player('drinks', 'mayor')


# define claims and info (claims can happen at any time before getting solutions)

g.players['ekin'].add_info(1)
g.players['malashaan'].add_info(1, 'poisoner','drinks','fran')
g.players['fran'].add_info(1)
g.players['kota'].add_info(1, 'monk','tapir','josh')

g.players['malashaan'].nominate('fran',None)
g.players['kota'].nominate('kota',None)
g.players['reznora'].nominate('malashaan',None)

g.players['malashaan'].executed_by_vote()

g.next_day()

g.players['josh'].was_killed_at_night()
g.players['josh'].add_info(1,None,'art')
g.players['fran'].add_info(1)
g.players['bruce'].add_info(1,'investigator')
g.players['bruce'].nominate('drinks',None)
g.players['kota'].nominate('fran',None)

g.players['drinks'].executed_by_vote()

g.next_day()
g.players['ekin'].was_killed_at_night()
g.players['fran'].add_info(1)
g.players['bruce'].add_info(1,'poisoner')


# get solutions

solutions = g.getAllSolutions()
print("Found ",len(solutions), " solutions:")
for solution in solutions: print(solution)
