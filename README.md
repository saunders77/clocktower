# Clocktower
solver for the game Blood on the Clocktower

V 2.0 - added support for multi-turn games
Breaking changes:
-'clocktower' object replaced by 'game' object
-'getAllSolutions returns an array of possible world dictionaries (see the world object below)

## Usage:

import clocktower

g = clocktower.game('trouble_brewing')

## Methods:

For all methods, specify arguments in lowercase.

### game.add_player(name, [claimed_character_name]) 

Players are added sequentially in clockwise order. Assumes good characters are being truthful about their claimed character.

Added players can be referenced by name with the game.players[name] dictionary.

A player named 'you' is assumed to be good

Player names must be unique

Player claims can be added (or replaced) later with player.claim()

### game.add_players(names)

Players can also be added with this method in a single name list

### player.add_info(number, info_character_name, other_player_name_1, other_player_name_2)

info describes information the players claim to have received from the storyteller.

number is required and other parameters are optional. For roles without a specified number in their info, use the number 0 or 1, depending on whether a player is specified. Some info is a combination of information from the storyteller and the player - for example, a Monk's info is given as 1 and the player being protected. A fortune teller gets a 1 if a demon is detected.

info should be added only after players have been added, if info references players

add_info can called once, at most, per player per day

if players change their info claims, previous claims can be overwritten with player.previous_info (see below)

### player.previous_info(night_number, number, info_character_name, other_player_name_1, other_player_name_2)

adds or changes info, if a player provided info for a morning before this morning or if a player says they lied about previous information

arguments are the same as add_info, except for the initial night_number parameter. The number corresponds to the night when the info was made, either 0 for the initial night, or 1, 2, 3, ... for subsequent nights.

### player.slay(target_player_name, result)

call when a player publicly attempts to slay. result is None if the target doesn't die. Result should be 'trigger' or True if the target dies.

### player.nominate(nominee_name, result)

Nominations must be recorded in actions the first time each player is nominated, even if they do not trigger an execution (otherwise some Virgin solutions can't be excluded).

result is None if the player nominating survives. If the player nominating dies, result is 'trigger' or True if the nominating player dies (would be from nominating the virgin)

### player.executed_by_vote()

call when the player is executed via vote

### player.was_killed_at_night()

call when you discover the demon (night) kill

### player.claim(claimed_character_name)

creates or overwrites the player's claimed character. Can be called multiple times if a player changes their claim

### game.next_day()

call right before each night phase after the first

### game.getAllSolutions(fortune_teller_red_herring_can_move_rule = True, min_info_roles_count = 0)

Returns a dictionary of world solutions describing the players, ordered by seat number. See the world object (below)

All returned lists have the potential to satisfy all the constraints, but solutions may be improbable or require poor decisions from the players or storyteller (but not breaking any game rules).

There are several meta assumptions which can be changed to further restrict possible worlds:

-fortune_teller_red_herring_can_move_rule can be set False to assume the storyteller won't pick the recluse/spy as the fortune teller's red herring, and then being able to choose a new red herring on a subsequent turn at will.

-min_info_roles_count assumes the storyteller will pick at least a certain number of true townsfolk roles that are guaranteed to get information

### game.world

Describes a solution, returned in a list via game.getAllSolutions() (above)

Properties include:
-world.finalCharactersDict, a dictionary with all characters, with the keys as final character names and the values as the player names
-world.transformationsDict, a dictionary with all players who changed character. The keys are the player name and the values are 2-element lists with the [0] element as the starting character and the [1] element as the ending character
-world.fortuneTellerRedHerringSeat, an 0-based index corresponding to the seat position of the player who was the fortune teller's red herring (if any), based on the order in which the players were added to the game. Otherwise, None
-world.poisonsBlockingInfo, an array of turns where the poisoner blocked info (True) or did not (False) 

str(world) yields a user-readable solution (same for print(world))

### game.get_analytics()

Call after game.getAllSolutions(). Returns an analytics object. Call print() or str() with it to see a summary of solutions data

## Samples: 

See clocktower/samples for usage examples with 3 puzzles  
