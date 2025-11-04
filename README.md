# clocktower
solver for the game Blood on the Clocktower

Usage:

import clocktower
c = clocktower.clocktower()

Methods:
c.add_player(name, claimed_character_name) 
# players are added sequentially in clockwise order. Assumes good characters are being truthful about their claimed character.
# added players can be referenced by name with the c.players[name] dictionary
# a player named 'you' is assumed to be good
# player names must be unique

player.add_info(number, info_character_name, other_player_name_1, other_player_name_2)
# info describes information the players claim to have received from the storyteller.
# number is required and other parameters are optional
# info should be added only after players have been added, if info references players

player.add_action(action_name, target_player_name, result)
# action describes an event which may trigger abilities during the day. The player whose action is being added is the one which may have an ability related to the action.
# action_name can be 'slay', 'wasnominated', or 'wasexecuted'
# target_player_name (optional) is the other player (if any) who interacted with the action player.
# result is None or 'trigger'

c.getAllSolutions()
Returns a list of character name lists describing the players, ordered by seat number. 
All returned lists have the potential to satisfy all the constraints, but solutions may be improbable or require poor decisions from the players or storyteller (but not breaking any game rules).

For all methods, specify parameters in lowercase.

Samples: 
see clocktower/samples for usage examples with 3 puzzles  
