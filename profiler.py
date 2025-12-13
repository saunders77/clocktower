# keeps generating single-days until it finds one with a unique imp solution

import clocktower
import time
import cProfile, pstats

def now():
    return time.perf_counter()

def profile_call(label, fn, args=(), kwargs=None, print_limit=40, filter_re="clocktower"):
    if kwargs is None:
        kwargs = {}

    prof = cProfile.Profile()
    t0 = now()
    prof.enable()
    result = fn(*args, **kwargs)
    prof.disable()
    t1 = now()

    print("\n==== PROFILE: " + label + " ====")
    print("WALL: %.3f s" % (t1 - t0))
    stats = pstats.Stats(prof).strip_dirs().sort_stats("tottime")
    stats.print_stats(filter_re, print_limit)  # only show clocktower frames by default
    return result

g = clocktower.game("trouble_brewing")

# define players

g.add_player('you', 'investigator')
g.add_player('abed',     'investigator')
g.add_player('beth',    'librarian')
g.add_player('chris',    'fortune_teller')
g.add_player('denny',   'ravenkeeper')
g.add_player('egan',   'monk')
g.add_player('finn',    'recluse')
g.add_player('gisele',    'saint')

# define info and actions

g.players["you"].add_info(1,'scarlet_woman','chris','gisele')
g.players["abed"].add_info(1,'scarlet_woman','you','finn')
g.players["beth"].add_info(0)
g.players["chris"].add_info(0,'imp','beth','abed')

g.print_game_summary()
solutions = profile_call(
    "getAllSolutions",
    g.getAllSolutions,
    args=(False, 0, True),
    filter_re="clocktower"
)
print("Found ",len(solutions), " solutions:")
for solution in solutions: print(solution)
print(g.get_analytics())

