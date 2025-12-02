# https://www.youtube.com/watch?v=0aDt7n06dRM

import clocktower

g = clocktower.game("trouble_brewing")

# define players

g.add_player('athena', 'fortune_teller')
g.add_player('nene', 'chef')
g.add_player('important', 'librarian')
g.add_player('katherine', 'monk')
g.add_player('jackson', 'mayor')
g.add_player('graymason', 'empath')
g.add_player('krisey', 'soldier')
g.add_player('mike', 'undertaker')

# define claims and info (claims can happen at any time before getting solutions)

g.players['nene'].add_info(0)
g.players['important'].add_info(1,'drunk','jackson','mike')
g.players['athena'].add_info(0,'demon','mike','nene')
g.players['graymason'].add_info(1)
g.players['important'].nominate('graymason',None)
g.players['jackson'].nominate('important',None)
g.players['graymason'].nominate('mike',None)
g.players['important'].executed_by_vote()

g.next_day()

g.players['athena'].was_killed_at_night()
g.players['graymason'].add_info(1)
g.players['mike'].add_info(1,'librarian','important')
g.players['graymason'].nominate('krisey')
g.players['krisey'].nominate('jackson')
g.players['katherine'].nominate('mike')
g.players['krisey'].executed_by_vote()

g.next_day()

g.players['graymason'].add_info(2)
g.players['katherine'].was_killed_at_night()
g.players['mike'].add_info(1,'poisoner','krisey')

g.next_day()
g.players['nene'].was_killed_at_night()
g.players['graymason'].add_info(2)

# get solutions

solutions = g.getAllSolutions(False, 2)
print("Found ",len(solutions), " solutions:")
for solution in solutions: print(solution)
print(g.get_analytics())

# analytics output
