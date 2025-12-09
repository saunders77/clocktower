import clocktower

# what % of games are solvable at 3-players with no information-sharing until final-three?

# what is the best lie to tell in a given situation?

# what's a problem that must be considered separately from each player's perspective to solve?

g = clocktower.game("trouble_brewing")
g.set_random_players_and_claims(8)
g.run_random_night_and_day()