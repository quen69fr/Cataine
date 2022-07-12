""" this function probably belongs somewhere else, but you can cut/paste it
    easy
"""

def get_probability_to_roll(n):
    assert 2 <= n <= 12, "can't roll that number"
    return {
        2:  1,
        3:  2,
        4:  3,
        5:  4,
        6:  5,
        7:  6,
        8:  5,
        9:  4,
        10: 3,
        11: 2,
        12: 1
    }[n] / 36

def get_probability_of_intersection(ns):
    return sum(get_probability_of_intersection(n) for n in ns)
    
