import io
import pstats


def show_profile(profile):
    s = io.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(profile, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())
