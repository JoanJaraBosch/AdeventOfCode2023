import re
from typing import Tuple, List, Optional

def matrix_initializer(f):
    row = []
    matrix = []
    # Initialize matrix for puzzle3
    for lines in f:
        for letter in lines.replace("\n", ""):
            row.append(letter)
        matrix.append(row)
        row = []
    return matrix

class RangeMap(object):
    def __init__(self):
        self.sources = []
        self.destinations = []
        self.lengths = []

    def __getitem__(self, key: int):
        for i, s in enumerate(self.sources):
            if s <= key and s + self.lengths[i] > key:
                return self.destinations[i] + key - s
        return key

    def _map_range_single(self, start: int, length: int, r_start: int, r_dest: int, r_length: int) -> Optional[
        Tuple[int, int, int]]:
        end = start + length
        r_end = r_start + r_length
        # check if the ranges overlaps
        if r_start >= end or start >= r_end:
            # range do not overlap
            return None
        if r_end > start and start >= r_start and end >= r_end:
            return start, start - r_start + r_dest, r_end - start
        if end > r_start and r_end >= end and r_start >= start:
            return r_start, r_dest, end - r_start
        if end >= r_end and start <= r_start:
            return r_start, r_dest, r_length
        if r_end >= end and r_start <= start:
            return start, r_dest + start - r_start, length
        raise ValueError("you shouldn't have been able to reach this place!!!!")

    def map_range(self, start: int, length: int) -> List[List[int]]:
        mapped_range = []
        source_range = []
        for i, source in enumerate(self.sources):
            v = self._map_range_single(start, length, source, self.destinations[i], self.lengths[i])
            if not v:
                continue
            s, d, l = v
            # print(start, length, source, self.destinations[i], self.lengths[i], v)
            mapped_range.append((d, l))
            source_range.append((s, l))

        source_range.sort()
        c_start = start
        for (s, l) in source_range:
            if c_start < s:
                mapped_range.append((c_start, s - c_start))
            c_start = s + l
        if c_start < start + length:
            mapped_range.append((c_start, start + length - c_start))
        return sorted(mapped_range)

    def add_range(self, source: int, destination: int, length: int):
        self.sources.append(source)
        self.destinations.append(destination)
        self.lengths.append(length)

    def __repr__(self):
        return str([self.sources, self.destinations, self.lengths])


def parse_seeds(line: str) -> List[int]:
    assert line.startswith("seeds:")
    seeds = [int(s) for s in line[len("seeds: "):].split()]
    return seeds


def parse_map(line: str) -> Tuple[str, str]:
    assert "map:" in line
    mapping, _ = line.split()
    source, _, dest = mapping.split("-")
    return source, dest


def parse_range(line: str) -> Tuple[int, int, int]:
    source, destination, length = line.strip().split()
    return int(source), int(destination), int(length)


def get_location(seed, maps):
    s = seed
    for (dest, source), map in maps.items():
        s = map[s]
    return s


def part1(seeds, maps):
    min_loc = float('inf')
    for seed in seeds:
        min_loc = min(min_loc, get_location(seed, maps))
    return min_loc


def part2(seeds, maps):
    seeds = [(seeds[i], seeds[i + 1]) for i in range(0, len(seeds), 2)]
    for (dest, source), map in maps.items():
        next_seeds = []
        for start, length in seeds:
            next_seeds.extend(map.map_range(start, length))
        seeds = next_seeds
    next_seeds.sort()
    return next_seeds[0][0]

def puzzle1():
    f = open("puzzle1", "r")
    cont=0
    part = input("Which part of the puzzle you want to solve? (1/2): ")
    if(part == "1"):
        #PART1- First and last number per lane, 1 number == same number 2 times.
        for lines in f.readlines():
            numbers = re.findall(r'\d+', lines)
            number=0

            if(len(numbers)<2):
                number = int(numbers[0][0]+numbers[0][-1])
            else:
                number = int(numbers[0][0] + numbers[-1][-1])
            cont=cont+number
        print("Solution part1- Puzzle1 is: " + str(cont))
    else:
        #PART2- There are numbers written like numbers, first transform it, then do the same
        for lines in f.readlines():
            lines = lines.lower()
            lines = lines.replace("zero", "zero0zero")
            lines = lines.replace("one", "one1one")
            lines = lines.replace("two", "two2two")
            lines = lines.replace("three", "three3three")
            lines = lines.replace("four", "four4three")
            lines = lines.replace("five", "five5five")
            lines = lines.replace("six", "six6six")
            lines = lines.replace("seven", "seven7seven")
            lines = lines.replace("eight", "eight8eight")
            lines = lines.replace("nine", "nine9nine")
            numbers = re.findall(r'\d', lines)
            number=0
            if(len(numbers)<2):
                number = int(numbers[0]+numbers[0])
            else:
                number = int(numbers[0] + numbers[-1])

            cont=cont+number
        print("Solution part2- Puzzle1 is: " + str(cont))

def puzzle2():
    #Max of 12 red, 13 green and 14 blue
    cont=1 #id game
    result_part1= 0
    result_part2 = 0
    f = open("puzzle2", "r").readlines()
    part = input("Which part of the puzzle you want to solve? (1/2): ")
    if(part == "1"):
        for l in f:
            round_game = l.split(":")[1].split(";")
            possible = True
            size=0
            while(size<len(round_game) and possible):
                for cub in round_game[size].split(","):
                    if("red" in cub.lower()):
                        if(int(re.findall(r'\d+', cub)[0]) > 12):
                            possible=False
                    if ("green" in cub.lower()):
                        if (int(re.findall(r'\d+', cub)[0]) > 13):
                            possible = False

                    if ("blue" in cub.lower()):
                        if (int(re.findall(r'\d+', cub)[0]) > 14):
                            possible = False
                size=size+1
            if(possible):
                result_part1=result_part1+cont
            cont=cont+1
        print("The result of the Puzzle 2 part 1 is: "+str(result_part1))
    else:
        for l in f:
            round_game = l.split(":")[1].split(";")
            max_red=0
            max_green=0
            max_blue=0
            for round in round_game:
                for cub in round.split(","):
                    if ("red" in cub.lower()):
                        if (int(re.findall(r'\d+', cub)[0]) > max_red):
                            max_red = int(re.findall(r'\d+', cub)[0])
                    if ("green" in cub.lower()):
                        if (int(re.findall(r'\d+', cub)[0]) > max_green):
                            max_green = int(re.findall(r'\d+', cub)[0])
                    if ("blue" in cub.lower()):
                        if (int(re.findall(r'\d+', cub)[0]) > max_blue):
                            max_blue = int(re.findall(r'\d+', cub)[0])
            result_part2 = result_part2 + (max_blue*max_red*max_green)
        print("The result of the Puzzle 2 part 2 is: " + str(result_part2))


def puzzle3():
    with open("puzzle3") as f:
        input = [line.strip() for line in f.readlines()]

    symbols = []
    numbers = []
    gears = []
    for line in input:
        symbols.append(list(re.finditer(r"[^0-9.\s]", line)))
        numbers.append(list(re.finditer(r"[0-9]+", line)))
        gears.append(list(re.finditer(r"\*", line)))

    parts = []
    gear_ratios = []
    for i in range(len(input)):
        before = i - 1 if i >= 1 else None
        after = i + 1 if i < len(input) - 1 else None

        for s in symbols[i]:
            for n in numbers[i]:
                parts.append(int(n.group())) if s.end() >= n.start() and n.end() >= s.start() else None
            for n in numbers[before]:
                parts.append(int(n.group())) if s.end() >= n.start() and n.end() >= s.start() else None
            for n in numbers[after]:
                parts.append(int(n.group())) if s.end() >= n.start() and n.end() >= s.start() else None
        for g in gears[i]:
            __gear_parts = []
            for n in numbers[i]:
                __gear_parts.append(int(n.group())) if g.end() >= n.start() and n.end() >= g.start() else None
            for n in numbers[before]:
                __gear_parts.append(int(n.group())) if g.end() >= n.start() and n.end() >= g.start() else None
            for n in numbers[after]:
                __gear_parts.append(int(n.group())) if g.end() >= n.start() and n.end() >= g.start() else None
            if (len(__gear_parts) == 2):
                gear_ratios.append(__gear_parts[0] * __gear_parts[1])

    print("------ part number sums -------")
    print(sum(parts))
    print("------ gear ratio sums --------")
    print(sum(gear_ratios))

def puzzle4():
    lines = open("puzzle4").readlines()

    part1 = 0
    matching_nums = []
    for i, line in enumerate(lines):
        line = line.split(':')[1].strip()
        winning_nums = set(line.split('|')[0].strip().split())
        nums_i_have = set(line.split('|')[1].strip().split())
        matching_nums.append(len(winning_nums.intersection(nums_i_have)))
        part1 += int(2 ** (matching_nums[i] - 1))
    print("Part 2 puzzle 4 result is: " +str(part1))

    scratchcard_nums = {i: 1 for i in range(1, len(lines) + 1)}
    result_part2 = 0
    for i in range(1, len(lines) + 1):
        for j in range(scratchcard_nums[i]):
            for k in range(i + 1, i + matching_nums[i - 1] + 1):
                scratchcard_nums[k] += 1
        result_part2 += scratchcard_nums[i]
    print("Part 2 puzzle 4 result is: " + str(result_part2))

def puzzle5():
    file_name = "puzzle5"

    maps = {}

    with open(file_name, "r") as f:
        seeds = parse_seeds(f.readline())

        line = f.readline()
        while line:
            line = line.strip()
            if not line:
                pass
            elif "map:" in line:
                source_name, dest_name = parse_map(line)
                r_map = RangeMap()
                maps[(source_name, dest_name)] = r_map
            else:
                d, s, r = parse_range(line)
                r_map.add_range(s, d, r)
            line = f.readline()
    # print(maps)
    print("PART1 OF DAY 5 IS: "+str(part1(seeds, maps)))
    print("PART2 OF DAY 5 IS: "+str(part2(seeds, maps)))

if __name__ == '__main__':
    puzz = input("Which puzzle do you want to solve?(1-25): ")
    if(puzz == "1"):
        puzzle1()
    else:
        if(puzz == "2"):
            puzzle2()
        else:
            if (puzz == "3"):
                puzzle3()
            else:
                if (puzz == "4"):
                    puzzle4()
                else:
                    if (puzz == "5"):
                        puzzle5()