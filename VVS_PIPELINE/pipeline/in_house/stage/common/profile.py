from line_profiler import LineProfiler
from functools import wraps

def profile(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        lp = LineProfiler()
        lp.add_function(func)
        result = lp(func)(*args, **kwargs)
        print(f"\n[Profiler Output for '{func.__name__}']:")
        lp.print_stats(output_unit=1.0)
        return result
    return wrapper
