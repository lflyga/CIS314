"""
RNG comparison + sorting timing
- Tasks 1–5 from assignment image
"""

from collections import Counter
from time import perf_counter
import random
import secrets

# ---------- RNG helpers ----------
sysrand = random.SystemRandom()  # uses os.urandom under the hood

def draw_random(method: str, n: int, low: int, high: int) -> list[int]:
    """Return n integers in [low, high] using the chosen RNG backend."""
    if method == "random":
        return [random.randint(low, high) for _ in range(n)]
    elif method == "secrets":
        # secrets.randbelow is inclusive-low, exclusive-high; adjust to [low, high]
        span = high - low + 1
        return [low + secrets.randbelow(span) for _ in range(n)]
    elif method == "system":
        return [sysrand.randint(low, high) for _ in range(n)]
    else:
        raise ValueError("method must be 'random', 'secrets', or 'system'")

def summarize_counts(nums: list[int]) -> Counter:
    """Return Counter for frequency of unique values."""
    return Counter(nums)

def pretty_counts(cnt: Counter, low: int, high: int) -> str:
    """Format counts for all values in range (including missing)."""
    lines = []
    for v in range(low, high + 1):
        lines.append(f"{v:>5}: {cnt.get(v, 0)}")
    return "\n".join(lines)

# ---------- Simple sorting (insertion sort) ----------
def insertion_sort(a: list[int]) -> list[int]:
    """Stable O(n^2) insertion sort; returns a new sorted list."""
    arr = a[:]  # copy so we don't mutate caller's list
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr

def time_call(fn, *args, label: str = "", repeat: int = 1) -> float:
    """Time a function call; optionally average over 'repeat' identical runs."""
    total = 0.0
    for _ in range(repeat):
        t0 = perf_counter()
        fn(*args)
        total += perf_counter() - t0
    return total / repeat

def header(title: str):
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)

# =========================
# 1. Comparing small numbers (1..16, 100 draws)
# =========================
header("1) Comparing small numbers (range 1..16, n=100)")
rng_methods = ["random", "secrets", "system"]
small_runs = {}

for m in rng_methods:
    nums = draw_random(m, n=100, low=1, high=16)
    cnt = summarize_counts(nums)
    small_runs[m] = (nums, cnt)
    print(f"\n— {m.upper()} —")
    print("Counts per value (1..16):")
    print(pretty_counts(cnt, 1, 16))

print("\n1.4) Based on the counts above, do any methods *appear* better?")
print("Note: With only 100 draws and 16 buckets, all three should look roughly uniform.")
print("Small deviations (e.g., one value appearing 3–10 times) are normal sampling noise.")

# =========================
# 2. Repeat #1 with range 1..65535
# =========================
header("2) Re-run #1 with numbers 1..65535 (n=100)")
big_runs = {}

for m in rng_methods:
    nums = draw_random(m, n=100, low=1, high=65535)
    cnt = summarize_counts(nums)
    big_runs[m] = (nums, cnt)
    unique = len(cnt)
    repeats = 100 - unique
    print(f"\n— {m.upper()} —")
    print(f"Unique values: {unique}  |  Repeated values: {repeats}")
    print("Example sample (first 20):", nums[:20])

print("\n2.1/2.2) Are results different? Were numbers repeated?")
print("All three backends should behave similarly. With a 65,535 range and only 100 draws,")
print("it’s common to see *no* repeats—or just a couple—across methods.")

# =========================
# 3. Sort timing on 100-element list in 1..16
# =========================
header("3) Sorting 100 elements in 1..16")
data_100_small = draw_random("random", n=100, low=1, high=16)

t_ins = time_call(insertion_sort, data_100_small, label="insertion")
t_builtin = time_call(sorted, data_100_small, label="builtin")

print(f"Insertion sort time: {t_ins:.6f} s")
print(f"Built-in sort time:  {t_builtin:.6f} s")

# =========================
# 4. Sort timing on 100-element list in 1..65535
# =========================
header("4) Sorting 100 elements in 1..65535")
data_100_big = draw_random("random", n=100, low=1, high=65535)

t_ins_big = time_call(insertion_sort, data_100_big, label="insertion")
t_builtin_big = time_call(sorted, data_100_big, label="builtin")

print(f"Insertion sort time: {t_ins_big:.6f} s")
print(f"Built-in sort time:  {t_builtin_big:.6f} s")
print("Observation: Value magnitude doesn’t affect comparison operations, so timings")
print("are dominated by list length and algorithmic complexity, not by the numeric size.")

# =========================
# 5. Repeat #4 with 500 elements
# =========================
header("5) Sorting 500 elements in 1..65535")
data_500_big = draw_random("random", n=500, low=1, high=65535)

t_ins_500 = time_call(insertion_sort, data_500_big, label="insertion")
t_builtin_500 = time_call(sorted, data_500_big, label="builtin")

print(f"Insertion sort time: {t_ins_500:.6f} s")
print(f"Built-in sort time:  {t_builtin_500:.6f} s")
print("\nConclusion:")
print("- Insertion sort is O(n^2) and will 'flounder' as n grows (100 → 500 shows a big jump).")
print("- Python’s built-in Timsort is O(n log n) and remains far faster at larger sizes.")
print("- Across RNGs, distribution differences at these sizes are just normal randomness.")

