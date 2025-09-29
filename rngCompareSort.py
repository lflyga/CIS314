"""
Author: L. Flygare
Description: generate RNG/PRNG lists of numbers and perform different operations to compare and sort them 
                to better understand limits and efficiencies
"""

import random
import secrets
from collections import Counter
from time import perf_counter   #more accurate than time.time() and reliable even if comp clock changes time because it can only increase


"""started with this and realized I wanted something reusable with how many lists would be generated and compared"""
# #comparing small numbers (1-16)
# #list of 100 random numbers (1-16) using random
# n1 = 100    #number of random numbers
# randList = random.choices(range(1,17), k=n1)
# print(randList)
# #list of 100 random numbers (1-16) using secrets

#generating random lists using different methods of RNG
def draw_random(method: str, n: int, low: int, high: int) -> list[int]:
    """return n integers in range low-high using stated RNG method so it can be reused across different size lists"""
    if method == "random":
        return [random.randint(low, high) for g in range(n)]
    elif method == "secrets":
        #secrets.randbelow is inclusive low, exclusive high; adjust to [low, high] using span
        span = high - low + 1
        return [low + secrets.randbelow(span) for g in range(n)]
    else:
        raise ValueError("Method must be 'random' or 'secrets'")
    
#counting total of unique numbers
def summarize_counts(nums: list[int]) -> Counter:
    """return Counter for frequency of unique values"""
    return Counter(nums)

# #get counts of frequency of each unique value
# def individual_counts(cnt: Counter, low: int, high: int) -> str:
#     """format for a clean view of the frequency of each value in the given range even if the occurence is 0"""
#     lines = []
#     for v in range(low, high + 1):
#         #f string that formats to show the value of v and right align it using at least 5 character spaces to align neatly in a column
#         #cnt.get looks up the value of v in the Counter dict of freqs and if it is not present returns a 0 instead of an error
#         lines.append(f"{v:>5}: {cnt.get(v, 0)}")
#     return "\n".join(lines)

#get counts of frequency of each value but only show all if range is under a certain threshold, otherwise only show observed values
def flex_counts(cnt: Counter, low: int, high: int, threshold: int) -> str:
    """
    if range <= threshold then show all values in range with 0s for non-observed values
    if range > threshold then show only observed values with their counts
    """
    rng_size = high - low + 1
    lines = []
    if rng_size <= threshold:
        for v in range(low, high + 1):
            #f string that formats to show the value of v and right align it using at least 5 character spaces to align neatly in a column
            #cnt.get looks up the value of v in the Counter dict of freqs and if it is not present returns a 0 instead of an error
            lines.append(f"{v:>5}: {cnt.get(v, 0)}")
    else:
        #only keys that actually appear, sorted by value
        #allows for a large range to be used and not show every single value in the range to be listed in the frequency list
        for v in sorted(cnt.keys()):
            lines.append(f"{v:>5}: {cnt[v]}")
        #show how many values in provided range did not appear
        missing = rng_size - len(cnt)
        lines.append(f"...({missing} values in range did not appear)")
    return "\n".join(lines)

#creating an insertion sort - demonstrates sorting degradation over varying sized data sets
def insertion_sort(a: list[int]) -> list[int]:
    """ a stable O(n^2) insertion sort that returns a new sorted list"""
    arr = a[:]  #copy to leave original unmutated 
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr

#function that uses .sort()
def dot_sort(a: list[int]):
    """sorts list in place using .sort()"""
    arr = a[:]
    arr.sort()

#timing the sorts
def time_call(fn, *args, label: str = "") -> float:
    """
    timing a single function call and return the elapsed seconds
    fn = function to be timed, *args allows any number of args to be passed to that function
    """
    t0 = perf_counter()     #records the start time
    fn(*args)               #call function and arguments
    return perf_counter() - t0    #return elapsed time as a float

def compare_sorts(time_insertion: float, time_dot_sort: float) -> None:
    """ compare and print which method of sorting is faster"""
    if time_insertion < time_dot_sort:
        faster, slower, t_fast, t_slow = "Insertion Sort", ".sort()", time_insertion, time_dot_sort
    else:
        faster, slower, t_fast, t_slow = ".sort()", "Insertion Sort", time_dot_sort, time_insertion

    diff = t_slow - t_fast  #absolute difference in seconds
    ratio = (t_slow / t_fast) if t_fast > 0 else float("inf")   #calsulates how much faster, if fast time is 0 return infinity to avoid division by 0
    percent = (diff / t_slow) * 100.0 if t_slow > 0 else 0.0    # how much less time as a percentage, again avoids division by 0

    print(f"{faster} was faster than {slower}")
    print(f"Difference: {diff:.6f} seconds  |  Speedup: {ratio:.2f}x  |  {percent:.1f}% less time")

#create function to format a header for each section for easy delineation in output
def header(title: str):
    print("\n" + "=" * 90)
    print(title)
    print("=" * 90)

#========================
# 1. comparing small numbers, range 1-16, n=100
#========================
header("1. Comparing small numbers, range 1-16, n=100")
rng_methods = ["random", "secrets"]
small_runs = {}

for m in rng_methods:
    nums = draw_random(m, n=100, low=1, high=16)
    cnt = summarize_counts(nums)
    small_runs[m] = (nums, cnt)
    unique = len(cnt)
    repeats = 100 - unique
    print(f"\n- {m.upper()} -") #prints the RNG method in UPPERCASE
    print(f"Unique values: {unique}  |  Repeated values: {repeats}")
    print("Counts per value (1-16): ")
    # print(individual_counts(cnt, 1, 16))
    print(flex_counts(cnt, 1, 16, 25))

#========================
# 2. repeat step 1 with new range, range 1-65535, n=100
#========================
header("2. Repeat step 1 with new range, range 1-65535, n=100")
big_runs = {}

for m in rng_methods:
    nums = draw_random(m, n=100, low=1, high=65535)
    cnt = summarize_counts(nums)
    big_runs[m] = (nums, cnt)
    unique = len(cnt)
    repeats = 100 - unique
    print(f"\n- {m.upper()} -")
    print(f"Unique values: {unique}  |  Repeated values: {repeats}")
    print("Counts per value (1-65535): ")
    # print(individual_counts(cnt, 1, 65535))
    print(flex_counts(cnt, 1, 65535, 25))

"""
tl;dr - random/secret bahave roughly the same, small ranges have duplicates, larger ranges repeats go away
        neither is better in this application

for a small range with 100 elements, both RNGs worked roughly the same and because of the limited range had repeated 
values as expected while using all values within the range. over multiple runs, there was variance 
in frequecies within the expected range as is to be expected with random generation

for a large range with 100 elements, again, both RNGs performed about the same. with a wider range but still 100 
elements, there were no repeat values and 100 unique elements. I did at first wonder about the distribution of 
1, 2, 3, 4, and 5 digit numbers but then realized it was in keeping with the probability distribution  and that
with a larger 'n' 1 and 2 digit values would begin to be seen and there would be more 3 digit values along with 
repeats starting to be seen (for funsies changed 'n' to 10000 for one run and saw some values repeated)
"""

#========================
# 3. timing sorting of 100 elements, range 1-16
#========================
header("3. Sorting 100 elements, range 1-16")
data_100_small_num = draw_random("random", n=100, low=1, high=16)

t_insertion_small = time_call(insertion_sort, data_100_small_num, label="insertion")
t_inplace_small = time_call(dot_sort, data_100_small_num, label=".sort()")

print(f"insertion sort time: {t_insertion_small:.6f} seconds")
print(f".sort() sort time: {t_inplace_small:.6f} seconds")
compare_sorts(t_insertion_small, t_inplace_small)


#========================
# 4. timing sorting of 100 elements, range 1-65535
#========================
header("4. Sorting 100 elements, range 1-65535")
data_100_big_num = draw_random("random", n=100, low=1, high=65535)

t_insertion_big = time_call(insertion_sort, data_100_big_num, label="insertion")
t_inplace_big = time_call(dot_sort, data_100_big_num, label=".sort()")

print(f"insertion sort time: {t_insertion_big:.6f} seconds")
print(f".sort() sort time: {t_inplace_big:.6f} seconds")
compare_sorts(t_insertion_big, t_inplace_big)

#========================
# 5. timing sorting of 500 elements, range 1-65535
#========================
header("5. Sorting 500 elements, range 1-65535")
data_500 = draw_random("random", n=500, low=1, high=65535)

t_insertion_500 = time_call(insertion_sort, data_500, label="insertion")
t_inplace_500 = time_call(dot_sort, data_500, label=".sort()")

print(f"insertion sort time: {t_insertion_500:.6f} seconds")
print(f".sort() sort time: {t_inplace_500:.6f} seconds")
compare_sorts(t_insertion_500, t_inplace_500)

"""
tl;dr - insertion sort is good for tiny data sets but quickly flounders as size grows
        .sort() is significantly faster and works well on a large scale
        number of elements impacts sort time, range of values does not

sorting 100 elements with a small range, insertion sort was fast, but
.sort() was still significantly faster and saved way more time

sorting 100 elements with a wider range, the run times were almost identical 
because comparison based sorting does not care about the range but the length
of the list being sorted and both were 100 elements, .sort() still outperformed
insertion sort

sorting 500 elements, range irrelevant as previously established, insertion 
sort began to seriosluy flounder compared to .sort() which still outperformed 
it by leaps and bounds. the quadratic growth of the list makes insertion sort, 
an O(n^2) algorithm impratical for larger data sets
"""

"""
I absolutely referenced chatGPT. I started completely on my own but quickly 
realized I wanted to do it differently. it forced me to use things like 
f-strings that I tend to avoid and I was constantly asking for in-depth 
explanations of steps I asked about to better understand the methodology to be 
able to better implement it on my own in the future. I did make tweaks to what 
was provided to still make it my own and show things how I wished for them to 
appear. I made notes about things I didn't previously know and learned in the 
process but that are also informative about the code
"""