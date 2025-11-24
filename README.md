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

if players change their info claims, previous claims can be overwritten with player.change_info (seel below)

### player.change_info(night_number, number, info_character_name, other_player_name_1, other_player_name_2)

changes info, if a player says they lied about previous information

arguments are the same as add_info, except for the night_number parameter. The number corresponds to the night when the info was made, either 0 for the initial night, or 1, 2, 3, ... for subsequent nights.

### player.add_action(action_name, target_player_name, result)

action describes an event which may trigger abilities during the day. The player whose action is being added is the one which may have an ability related to the action.

action_name can be 'slay', 'wasnominated', or 'wasexecuted'.

target_player_name (optional) is the other player (if any) who interacted with the action player.

Nominations must be recorded in actions, even if they do not trigger an execution (otherwise some Virgin solutions can't be excluded).

result is None or 'trigger'.

### player.claim(claimed_character_name)

creates or overwrites the player's claimed character. Can be called multiple times if a player changes their claim

### game.getAllSolutions()

Returns a dictionary of world solutions describing the players, ordered by seat number. See the world object (below)

All returned lists have the potential to satisfy all the constraints, but solutions may be improbable or require poor decisions from the players or storyteller (but not breaking any game rules).

### g.world

Describes a solution, returned in a list via game.getAllSolutions() (above)

Properties include:
-world.finalCharactersDict, a dictionary with all characters, with the keys as final character names and the values as the player names
-world.transformationsDict, a dictionary with all players who changed character. The keys are the player name and the values are 2-element lists with the [0] element as the starting character and the [1] element as the ending character
-world.fortuneTellerRedHerringSeat, an 0-based index corresponding to the seat position of the player who was the fortune teller's red herring (if any), based on the order in which the players were added to the game. Otherwise, None 

str(world) yields a user-readable solution (same for print(world))

## Samples: 

See clocktower/samples for usage examples with 3 puzzles  
