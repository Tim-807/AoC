import re
import sys
import math
import time
import copy
import pickle
import socket
import string
import requests
import itertools
import statistics
import numpy as np
from os import path
from functools import lru_cache
from collections import defaultdict

# Advent of Code
# Never did spend the time to work out how to get oAuth to work so this code expects you to
# manually copy over your session cookie value.
# Using a web browser inspect the cookies when logged into the Advent of Code website.
# Copy the value from the "session" cookie into a text file called "session.txt"

# Constants
_code_path = r'c:\AoC'
_offline = False
_year = 2022


def _check_internet(host="8.8.8.8", port=53, timeout=2):
    """
    Attempt to check for the firewall by connecting to Google's DNS.
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        # print(ex)
        return False


def _pull_puzzle_input(day, seperator, cast):
    """
    Pull the puzzle data from the AOC website.

    :param day: (int,str) the AoC day puzzle input to fetch or an example puzzle string
    :param seperator: (str) A string separator to pass into str.split when consuming the puzzle data.
    :param cast: (None,type) A Python function often a type cast (int, str, lambda) to be run against each data element.

    :return: tuple of the data.
    """
    global _work, _offline, _code_path

    if _offline:
        with open(_code_path + r"\{}\day{}.txt".format(_year, day)) as file_handler:
            data_list = file_handler.read().split(seperator)
    elif type(day) is str:  # An example string
        data_list = day.split(seperator)
    else:
        if not path.exists(_code_path + "/session.txt"):
            raise Exception("Using the web browser get the session cookie value\nand put it as a string in {}".format(_code_path + "\session.txt"))  # noqa: W605
        with open(_code_path + "/session.txt", 'r') as session_file:
            session = session_file.read()
        # Check to see if behind the firewall.
        if _check_internet():
            proxy_dict = {}
        else:
            proxy_dict = {'http': 'proxy-dmz.intel.com:911',
                          'https': 'proxy-dmz.intel.com:912'}
        header = {'Cookie': 'session={:s}'.format(session.rstrip('\n'))}
        with requests.Session() as session:
            resp = session.get('https://adventofcode.com/{}/day/{}/input'.format(_year, day), headers = header, proxies = proxy_dict)  # noqa: E251
            text = resp.text.strip("\n")
            if resp.ok:
                data_list = resp.text.split(seperator)
            else:
                print("Warning website error")
                return ()

    if data_list[-1] == "":
        data_list.pop(-1)
    if cast is not None:
        data_list = [cast(x) for x in data_list]
    return tuple(data_list)


# Cache the data in a pickle file.
def get_input(day, seperator, cast, override=False):
    """
    Helper function for the daily puzzle information.
    If the puzzle data does not exist it attempts to pull it from the website.
    Caches the puzzle data into a pickle file so that re-runs don't have the performance
    penalty of fetching from the Advent Of Code website.
    :param day: (int, str) the AoC day puzzle input to fetch or a string of the puzzle example.
    :param seperator: (str) A string separator to pass into str.split when consuming the puzzle data.
    :param cast: (None,type) A Python function often a type cast (int, str, lambda) to be run against each data element.
                             None - do not apply a function/cast to the data.
    :param override: (bool) True = Fetch the data again instead of using the cached copy.

    :return: tuple containing the puzzle data
    """
    global _code_path
    if path.exists(_code_path + r'\{}\input.p'.format(_year)):
        puzzle_dict = pickle.load(open(_code_path + r'\{}\input.p'.format(_year), 'rb'))
    else:  # No pickle file, will need to make a new one.
        puzzle_dict = {}

    puzzle_input = puzzle_dict.get(day, None)

    if puzzle_input is None or override is True:
        puzzle_input = _pull_puzzle_input(day, seperator, cast)
        if type(day) is int:  # only save the full puzzle data to the pickle file.
            puzzle_dict[day] = puzzle_input
            pickle.dump(puzzle_dict, open(_code_path + r'\{}\input.p'.format(_year), 'wb'))
    return puzzle_input


def _day1():
    """
    How many calories does an elf carry
    """
    day = "1000\n2000\n3000\n\n4000\n\n5000\n6000\n\n7000\n8000\n9000\n\n10000\n"
    day = 1
    puzzle = get_input(day, '\n', None)
    elves = []
    cal = 0
    for val in puzzle:
        if val == "":
            elves.append(cal)
            cal=0
        else:
            cal += int(val)
    elves.append(cal)  # Last elf (might not be a \n after the last calorie data point)
    elves.sort(reverse=True)
    print(f"Single most calories {elves[0]}")
    print(f"Total of the top three elves {sum(elves[:3])}")


def _day1_eval():
    day = "1000\n2000\n3000\n\n4000\n\n5000\n6000\n\n7000\n8000\n9000\n\n10000\n"
    day = 1
    puzzle = list(get_input(day, '\n\n', None, True))
    puzzle[-1]=puzzle[-1].strip('\n')  # Formatting fix
    elves = [eval(x.replace("\n",'+')) for x in puzzle]
    elves.sort(reverse=True)
    print(f"Single most calories {elves[0]}")
    print(f"Total of the top three elves {sum(elves[:3])}")


def _day2_orig():
    """
    Rock Paper Scissors
    """
    day = "A Y\nB X\nC Z"
    day = 2
    puzzle = get_input(day, '\n', None)
    score = {"X":1, "Y":2, "Z":3}
    win =  {"A":"Y", "B":"Z", "C":"X"}  # What to have to win
    lose = {"A":"Z", "B":"X", "C":"Y"}  # What to pick to lose
    draw = {"A":"X", "B":"Y", "C":"Z"}  # Lookup for a draw
    total_score = 0
    for move in puzzle:
        elf, me = move.split(" ")
        if win[elf] == me:
            total_score += 6
        elif draw[elf] == me:
            total_score += 3
        else:
            total_score += 0
        total_score += score[me]
    print(f"Part 1 total score {total_score}")
    total_score = 0
    for move in puzzle:
        elf, result = move.split(" ")
        if result == "Z":  # Win
            me = win[elf]
            total_score += 6
        elif result == "Y":  # Draw
            me = draw[elf]
            total_score += 3
        else:
            me = lose[elf]
        total_score += score[me]
    print(f"Part 2 total score {total_score}")


def _day2():
    """
    Rock, Paper, Scissors with Elves!
    """
    day = "A Y\nB X\nC Z"
    day = 2
    puzzle = get_input(day, '\n', None)
    p1_dict=  {"B X":1, "C Y":2, "A Z":3, "A X":4, "B Y":5, "C Z":6, "C X":7, "A Y":8, "B Z":9}
    p2_dict = {"B X":1, "C X":2, "A X":3, "A Y":4, "B Y":5, "C Y":6, "C Z":7, "A Z":8, "B Z":9}
    print(f"Part 1 total score {sum([p1_dict[move] for move in puzzle])}")
    print(f"Part 2 total score {sum([p2_dict[move] for move in puzzle])}")


def _day3():
    """
    What's in your rucksack?!?
    """
    day = "vJrwpWtwJgWrhcsFMMfFFhFp\njqHRNqRjqzjGDLGLrsFMfFZSrLrFZsSL\nPmmdzqPrVvPwwTWBwg\nwMqvLMZHhHMvwLHjbvcjnnSBnvTQFn\nttgJtRGJQctTZtZT\nCrZsJsPPZsGzwwsLwLmpwMDw"
    day = 3
    puzzle = get_input(day, '\n', None)
    # Make a string of all lower and upper case letter to use to get the score for each letter.
    scoring_guide = " " + string.ascii_lowercase + string.ascii_uppercase
    score = 0
    for rucksack in puzzle:
        half = len(rucksack) // 2
        compartments = set.intersection(set(rucksack[:half]), set(rucksack[half:]))
        if len(compartments) != 1:
            raise Exception("Part 1; What? {compartments}")
        score += scoring_guide.find(compartments.pop())
    print(f"Part 1 priorities sum is {score}")
    score = 0
    for one, two, three in zip(*[iter(puzzle)]*3):
        group = set.intersection(set(one), set(two), set(three))
        if len(group) != 1:
            raise Exception(f"Part 2; What? {group}")
        score += scoring_guide.find(group.pop())
    print(f"Part 2 priorities sum is {score}")


def _day4():
    """
    Jungle clear-cutting elves.
    """
    day ="2-4,6-8\n2-3,4-5\n5-7,7-9\n2-8,3-7\n6-6,4-6\n2-6,4-8"
    day = 4
    puzzle = get_input(day, '\n', None)
    p1_score = p2_score = 0
    for pair in puzzle:
        first, second = pair.split(",")
        first_start, first_end = map(int, first.split('-'))
        second_start, second_end = map(int, second.split('-'))
        first_set = set(range(first_start, first_end + 1))
        second_set = set(range(second_start, second_end + 1))
        if first_set.issubset(second_set) or second_set.issubset(first_set):
            p1_score += 1
        if first_set.intersection(second_set):
            p2_score += 1
    print(f"Part 1 {p1_score} assignment pairs fully contian the other")
    print(f"Part 2 {p2_score} assignments overlap")


def _day5():
    """
    Well at least it wasn't one of those three tower colored ring puzzles.
    """
    day = "    [D]    \n[N] [C]    \n[Z] [M] [P]\n 1   2   3 \n\nmove 1 from 2 to 1\nmove 3 from 1 to 3\nmove 2 from 2 to 1\nmove 1 from 1 to 2"
    day = 5
    puzzle = get_input(day, "\n", None)
    # Get the number of stacks to make processing the table easier.
    stack_numbers = []
    for line in puzzle:
        if line.startswith(" 1 "):
            stacks = line.strip().split(" ")
            for char in stacks:
                if char:
                    stack_numbers.append(char)
            break
    p1_stacks_dict = {}
    for line in puzzle:
        if not line:
            continue
        elif line.startswith(" 1 "):
            # This is the line with the stack numbers, done loading now. Create a copy for part 2.
            p2_stacks_dict = copy.deepcopy(p1_stacks_dict)
        elif "move" in line:  # This is a stack movement line
            temp = []
            directions = line.split(" ")
            number_of_crates = -1 * int(directions[1])
            # Part 1 crates are reversed because they get picked 1 by 1.
            p1_stacks_dict[directions[5]] += reversed(p1_stacks_dict[directions[3]][number_of_crates:])
            del p1_stacks_dict[directions[3]][number_of_crates:]
            # Part 2 crates order is not reversed.
            p2_stacks_dict[directions[5]] += p2_stacks_dict[directions[3]][number_of_crates:]
            del p2_stacks_dict[directions[3]][number_of_crates:]            
        else:  # Note: index 0 is the bottom of the stack of crates.
            crates = [" "] + list(zip(*[iter(line + " ")] * 4))  # Pad because the stacks are 1's based numbering.
            for stack in stack_numbers:
                if crates[int(stack)][1] != " ":
                    p1_stacks_dict.setdefault(stack, [])
                    p1_stacks_dict[stack].insert(0, crates[int(stack)][1])

    p1_answer = p2_answer = ""
    for stack in stack_numbers:
        p1_answer += p1_stacks_dict[stack][-1]
        p2_answer += p2_stacks_dict[stack][-1]
    print(f"Part 1 top of stacks is {p1_answer}")
    print(f"Part 2 top of stacks is {p2_answer}")


def go(day=5):
    try:
        return eval("_day{}".format(day))
    except Exception as e:
        print(e)

import concurrent.futures
import time


#if __name__ == "__main__":
#    loop = asyncio.get_event_loop()
#    loop.run_until_complete(c_thread(loop))
