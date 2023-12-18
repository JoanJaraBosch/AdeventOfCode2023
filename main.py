import re, math, functools
from collections import deque
from itertools import chain
from typing import Tuple, List, Optional
from heapq import heappush, heappop
from math import inf


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
    f = open("inputs/puzzle1", "r")
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
    f = open("inputs/puzzle2", "r").readlines()
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
    with open("inputs/puzzle3") as f:
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
    lines = open("inputs/puzzle4").readlines()

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
    file_name = "inputs/puzzle5"

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

def puzzle6():
    lines = open("inputs/puzzle6").readlines()
    list_races_seconds = []
    list_races_records = []
    cont = 1
    for line in lines:
        if(cont == 1):
             for second in line.split(":")[1].strip().split():
                 list_races_seconds.append(int(second.strip()))
        else:
            for meters in line.split(":")[1].strip().split():
                list_races_records.append(int(meters.strip()))
        cont = cont + 1

    cont = 0
    resultat_part1 = 1
    resultat_part2 = 0

    segons_part2 = ""
    metres_part2 = ""

    while(cont < len(list_races_seconds)):
        carrera = 0
        for elem in range(list_races_seconds[cont]+1):
            if(elem*(list_races_seconds[cont]-elem) > list_races_records[cont]):
                carrera = carrera + 1
        segons_part2 = segons_part2+str(list_races_seconds[cont])
        metres_part2 = metres_part2 + str(list_races_records[cont])
        resultat_part1 = resultat_part1 * carrera
        cont = cont + 1

    for elem in range(int(segons_part2) + 1):
        if (elem * (int(segons_part2) - elem) > int(metres_part2)):
            resultat_part2 = resultat_part2 + 1

    print("The result of the part 1 of the puzzle 6 is: "+str(resultat_part1))
    print("The result of the part 2 of the puzzle 6 is: " + str(resultat_part2))

def strength_part1(hand, cardValues):
    value = ""
    x = set(hand)
    match len(x):
        case 1:
            value += "6"
        case 2:
            cards = list(hand)
            for card in x:
                cards.remove(card)
            if len(set(cards)) == 1:
                value += "5"
            elif len(set(cards)) == 2:
                value += "4"
            else: print("oh no case 2")
        case 3:
            cards = list(hand)
            for card in x:
                cards.remove(card)
            if len(set(cards)) == 1:
                value += "3"
            elif len(set(cards)) == 2:
                value += "2"
            else: print("oh no case 3")
        case 4:
            value += "1"
        case 5:
            pass
    for char in hand:
        value += cardValues[char]
    return int(value)

def puzzle7_part1():
    cardValues = {"A": "14", "K": "13", "Q": "12", "J": "11", "T": "10", "9": "09", "8": "08", "7": "07", "6": "06",
                  "5": "05", "4": "04", "3": "03", "2": "02"}
    path = "inputs/puzzle7"
    f = open(path, "r")
    total = 0
    info = {}  # 1hand,2bet,3strength
    for line in f:
        line = line.split()
        if not strength_part1(line[0],cardValues) in info:
            info[strength_part1(line[0],cardValues)] = int(line[1])
        else:
            info[strength_part1(line[0],cardValues)] += int(line[1])
    sortie = sorted(info)
    for i, j in enumerate(sortie, 1):
        total += info[j] * i
    print("Result of part1 puzzle7: "+str(total))

def strength_part2(hand, cardValues):
    value = ""
    x = set(hand)
    if "J" in x:
        x.remove("J")
    match len(x):
        case 0:value+="6"
        case 1:
            value += "6"
        case 2:
            cards = list(hand)
            for j in cards[:]:
                if j == "J":
                    cards.remove("J")
            for card in x:
                cards.remove(card)
            if len(set(cards)) <= 1:
                value += "5"
            elif len(set(cards)) == 2:
                value += "4"

        case 3:
            cards = list(hand)
            for j in cards[:]:
                if j == "J":
                    cards.remove("J")
            for card in x:
                cards.remove(card)
            if len(set(cards)) <= 1:
                value += "3"
            elif len(set(cards)) == 2:
                value += "2"
            else: print("oh no case 3",set(cards),hand)
        case 4:
            value += "1"
        case 5:
            pass
    for char in hand:
        value += cardValues[char]
    return int(value)
def puzzle7_part2():
    cardValues = {"A": "14", "K": "13", "Q": "12", "J": "00", "T": "10", "9": "09", "8": "08", "7": "07", "6": "06",
                  "5": "05", "4": "04", "3": "03", "2": "02"}
    path = "inputs/puzzle7"
    f = open(path, "r")
    total = 0
    info = {}  # 1hand,2bet,3strength
    for line in f:
        line = line.split()
        if not strength_part2(line[0], cardValues) in info:
            info[strength_part2(line[0],cardValues)] = int(line[1])
        else:
            info[strength_part2(line[0],cardValues)] += int(line[1])
    sortie = sorted(info)
    for i, j in enumerate(sortie, 1):
        total += info[j] * i
    print("Result of part2 puzzle7: "+str(total))
def puzzle7():
    puzzle7_part1()
    puzzle7_part2()

def get_stuff(content) -> tuple[str, dict[str, tuple[str, str]]]:
    [dirs, lookup_str] = content.split('\n\n', 1)
    dirs = dirs.strip()
    lookup = {}
    for lookup_ln in lookup_str.split('\n'):
        for c in '()=,':
            lookup_ln = lookup_ln.replace(c, '')
        [key, left, right] = lookup_ln.split(maxsplit=2)
        lookup[key] = (left, right)
    return (dirs, lookup)

def puzzle_8_part_1(content, dir_map):
    dirs, lookup = get_stuff(content)
    current = 'AAA'
    steps = 0
    while current != 'ZZZ':
        current_dir = dirs[steps % len(dirs)]
        current = lookup[current][dir_map[current_dir]]
        steps += 1
    print(steps)

def puzzle_8_part_2_helper(start: 'str', dirs: str, lookup: dict[str, tuple[str, str]], dir_map) -> int:
    steps = 0
    current = start
    while current[-1] != 'Z':
        current_dir = dirs[steps % len(dirs)]
        current = lookup[current][dir_map[current_dir]]
        steps += 1
    return(steps)

def puzzle_8_part_2(content, dir_map):
    step_ls = []
    dirs, lookup = get_stuff(content)
    for loc in lookup:
        if loc[-1] == 'A':
            step_ls.append(puzzle_8_part_2_helper(loc, dirs, lookup, dir_map))
    print(math.lcm(*step_ls))

def puzzle8():
    content = open('inputs/puzzle8').read()
    dir_map = {
        'L': 0,
        'R': 1,
    }

    puzzle_8_part_1(content, dir_map)
    puzzle_8_part_2(content, dir_map)

def all_zeros(list):
    for l in list:
        if(l != 0):
            return True
    return  False

def sum_values(list_of_lists):
    result = 0
    for list in list_of_lists:
        result = result + list[-1]
    return result

def sub_values(list_of_lists):
    result = 0
    for list in reversed(list_of_lists):
        result = list[0] - result
    return result

def puzzle9_helper(line, part):
    result = [line]
    seguir_bucle = True
    while(seguir_bucle):
        result_aux = []
        cont = 0
        while(cont < len(line)-1):
            result_aux.append(int(line[cont+1])-int(line[cont]))
            cont = cont + 1
        result.append(result_aux)
        seguir_bucle = all_zeros(result_aux)
        line = result_aux
    if(part == "1"):
        return sum_values(result)
    else:
        return sub_values(result)

def puzzle9():
    content = open('inputs/puzzle9').readlines()
    part = puzz = input("Which part do you want to solve?(1-2): ")
    result_part = 0
    for line in content:
        result_part = result_part + puzzle9_helper(list(map(int,line.strip().split())),part)

    print("The result of the part"+str(part)+" of the puzzle 9 is: "+str(result_part))

def starting_position(mapa):
    i = 0
    for row in mapa:
        j = 0
        for element in row:
            if(element == "S"):
                return str(i)+"-"+str(j)
            j = j +1
        i = i +1

def keep(mapa):
    values_possible = "0123456789."
    for row in mapa:
        for element in row:
            if(element not in values_possible):
                return True
    return False

def transform_seven_into_T(mapa):
    i = 0
    for row in mapa:
        j = 0
        for element in row:
            if(element == "7"):
                mapa[i][j] = "T"
            j = j + 1
        i = i + 1
    return mapa

def shoelace(points):
    area = 0

    X = [point[0] for point in points] + [points[0][0]]
    Y = [point[1] for point in points] + [points[0][1]]

    for i in range(len(points)):
        area += X[i] * Y[i + 1] - Y[i] * X[i + 1]

    return abs(area) / 2

def puzzle10_part1(lines):
    # up, down, right, left
    steps = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    # (from): (to)
    pipes = {
        "|": {(1, 0): (1, 0), (-1, 0): (-1, 0)},
        "-": {(0, 1): (0, 1), (0, -1): (0, -1)},
        "L": {(1, 0): (0, 1), (0, -1): (-1, 0)},
        "J": {(0, 1): (-1, 0), (1, 0): (0, -1)},
        "F": {(-1, 0): (0, 1), (0, -1): (1, 0)},
        "7": {(0, 1): (1, 0), (-1, 0): (0, -1)},
    }

    # create the map
    M = []
    for r, line in enumerate(lines):
        row = []
        for c, char in enumerate(line):
            row.append(char)
            if char == "S":
                r0, c0 = r, c
        M.append(row)

    A = 0
    for dr, dc in steps:
        r, c = r0 + dr, c0 + dc
        l = 1  # the length of the path

        while M[r][c] != "S":
            l += 1

            if not -1 < r < len(M) and -1 < c < len(M[r]):
                break  # out of bounds

            if not M[r][c] in pipes:
                break  # not a pipe

            pipe = pipes[M[r][c]]
            if not (dr, dc) in pipe:
                break  # pipes don't join up

            dr, dc = pipe[(dr, dc)]
            r, c = r + dr, c + dc

        if M[r][c] == "S":
            A = l // 2
            return int(A)

def puzzle10_part2(lines):
    # up, down, right, left
    steps = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    # (from): (to)
    pipes = {
        "|": {(1, 0): (1, 0), (-1, 0): (-1, 0)},
        "-": {(0, 1): (0, 1), (0, -1): (0, -1)},
        "L": {(1, 0): (0, 1), (0, -1): (-1, 0)},
        "J": {(0, 1): (-1, 0), (1, 0): (0, -1)},
        "F": {(-1, 0): (0, 1), (0, -1): (1, 0)},
        "7": {(0, 1): (1, 0), (-1, 0): (0, -1)},
    }

    bends = ["L", "J", "F", "7"]

    # create the map
    M = []
    for r, line in enumerate(lines):
        row = []
        for c, char in enumerate(line):
            row.append(char)
            if char == "S":
                r0, c0 = r, c
        M.append(row)

    for dr, dc in steps:
        r, c = r0 + dr, c0 + dc
        V = [(r0, c0)]  # track vertices
        b = 1  # count boundary points

        while M[r][c] != "S":
            b += 1
            if M[r][c] in bends:
                V.append((r, c))

            if not -1 < r < len(M) and -1 < c < len(M[r]):
                break  # out of bounds

            if not M[r][c] in pipes:
                break  # not a pipe

            pipe = pipes[M[r][c]]
            if not (dr, dc) in pipe:
                break  # pipes don't join up

            dr, dc = pipe[(dr, dc)]
            r, c = r + dr, c + dc

        if M[r][c] == "S":
            break

    A = shoelace(V)  # area

    # pick's theorem
    return int(A + 1 - b / 2)

def puzzle10():
    lines = open('inputs/puzzle10').readlines()
    part = input("Which part do you want to solve?(1-2): ")

    sol = 0

    if(part == "1"):
        sol = puzzle10_part1(lines)
    else:
        sol = puzzle10_part2(lines)
    print("The result of the part"+str(part)+" of the puzzle 10 is: "+str(sol))

def ini_universe(lines):
    result = []
    for line in lines:
        aux_row = []
        for letter in line.strip():
            if(letter != "\n"):
                aux_row.append(letter)
        result.append(aux_row)
        if("#" not in line):
            result.append(line.split())
    A = zip(*result)
    positions_col = []
    #check for colums to duplicate
    j = 0
    for column in A:
        if("#" not in column):
            positions_col.append(j)
        j = j + 1

    result_real = []
    i = 0
    for row in result:
        j = 0
        row_aux = []
        for elem in row:
            row_aux.append(elem)
            if(j in positions_col):
                row_aux.append(elem)
            j = j + 1
        result_real.append(row_aux)
        i = i + 1
    return result_real

def sum_distances(map, posX, posY):
    result = 0
    i = posX
    j = posY
    while(i < len(map)):
        while(j < len(map[i])):
            if(map[i][j] == "#"):
                result = result + abs(posX - i) + abs(posY - j)
            j = j + 1
        j = 0
        i = i + 1
    return result

def puzzle11_part1(lines):
    map = ini_universe(lines)
    print(map)
    posX = 0
    result = 0
    for row in map:
        posY = 0
        for ele in row:
            if(ele == "#"):
                result = result + sum_distances(map, posX, posY)
            posY = posY + 1
        posX = posX + 1

    return result

def puzzle11():
    with open("inputs/puzzle11", "r") as f:
        data = f.read().splitlines()
        rows = []
        cols = []
        galaxies = []
        for y, row in enumerate(data):
            if not '#' in row:
                rows.append(y)
                continue
            for x, c in enumerate(row):
                if c == '#':
                    galaxies.append((x, y))
        for x, _ in enumerate(data[0]):
            if not '#' in [row[x] for _, row in enumerate(data)]:
                cols.append(x)

        short = long = 0
        for k, galaxy in enumerate(galaxies):
            for n in range(k + 1, len(galaxies)):
                y = (min(galaxies[n][0], galaxy[0]), max(galaxies[n][0], galaxy[0]))
                x = (min(galaxies[n][1], galaxy[1]), max(galaxies[n][1], galaxy[1]))

                short += y[1] - y[0] + x[1] - x[0]
                short += sum(1 for e in cols if e in range(y[0], y[1]))
                short += sum(1 for e in rows if e in range(x[0], x[1]))

                long += y[1] - y[0] + x[1] - x[0]
                long += sum(999999 for e in cols if e in range(y[0], y[1]))
                long += sum(999999 for e in rows if e in range(x[0], x[1]))

        print(f"Part 1: {short}")
        print(f"Part 2: {long}")


@functools.cache
def puzzle_12_helper(pattern, size, splits):
    a = splits[0]
    rest = splits[1:]
    after = sum(rest) + len(rest)

    count = 0

    for before in range(size - after - a + 1):
        if all(c in '#?' for c in pattern[before:before + a]):
            if len(rest) == 0:
                if all(c in '.?' for c in pattern[before + a:]):
                    count += 1
            elif pattern[before + a] in '.?':
                count += puzzle_12_helper(pattern[before + a + 1:],
                                       size - a - before - 1,
                                       rest)

        if pattern[before] not in '.?':
            break

    return count

def puzzle12():
    lines = open('inputs/puzzle12').readlines()
    part = input("Which part do you want to solve?(1-/2): ")
    result = 0
    for l in lines:
        pattern, splits = l.split()
        if(part == "1"):
            pattern = '?'.join((pattern,))
            splits = tuple(map(int, splits.split(',')))
            result = result + puzzle_12_helper(pattern, len(pattern), tuple(splits))
        elif(part == "2"):
                pattern = '?'.join((pattern,)*5)
                splits = tuple(map(int, splits.split(',')))*5
                result = result + puzzle_12_helper(pattern, len(pattern), tuple(splits))
    print("The solution for the puzzle 12 part"+part+"is: "+str(result))

# extract a single string from arbitrarily nested lists of strings
def collapse(l):
    return ''.join(chain.from_iterable(l))

# check if 2 grids differ by exactly 1 character
def smudgeEqual(a,b):
    count = 0
    for i,j in zip(collapse(a),collapse(b)):
        count += (i != j)
        if count > 1:
            return False
    if count == 1:
        return True
    return False

def checkVerticalReflections(grid, part):
    if(part==1):
        for i in [i + 1 for i in range(len(grid[0]) - 1)]:
            reflection = flipVertical([''.join(r[:i]) for r in grid])
            a = min(i, len(grid[0]) - i)
            if [''.join(r[:a]) for r in reflection] == [''.join(r[i:i + a]) for r in grid]:
                return i
        return 0
    else:
        for i in [i + 1 for i in range(len(grid[0]) - 1)]:
            reflection = flipVertical([''.join(r[:i]) for r in grid])
            a = min(i, len(grid[0]) - i)
            if smudgeEqual([''.join(r[:a]) for r in reflection], [''.join(r[i:i + a]) for r in grid]):
                return i
        return 0

def checkHorizontalReflections(grid, part):
    if(part == 1):
        for i in [i + 1 for i in range(len(grid) - 1)]:
            reflection = flipHorizontal(grid[:i])
            a = min(i, len(grid) - i)
            if reflection[:a] == grid[i:i + a]:
                return 100 * i
        return 0
    else:
        for i in [i + 1 for i in range(len(grid) - 1)]:
            reflection = flipHorizontal(grid[:i])
            a = min(i, len(grid) - i)
            if smudgeEqual(reflection[:a], grid[i:i + a]):
                return 100 * i
        return 0

# reflect grid over a vertical line
def flipVertical(grid):
    return [''.join(r[::-1]) for r in grid]

# reflect grid over a horizontal line
def flipHorizontal(grid):
    return grid[::-1]

def puzzle13_helper(grids , part):
    summaries = []
    for item in grids:
        grid = item.split('\n')
        summaries.append(checkVerticalReflections(grid, part))
        summaries.append(checkHorizontalReflections(grid, part))

    return sum(summaries)

def puzzle13():
    file = open('inputs/puzzle13', 'r')
    input = file.read()
    grids = input.split('\n\n')
    print("The vaue for puzzle13 part1 is: "+str(puzzle13_helper(grids, 1)))
    print("The vaue for puzzle13 part2 is: "+str(puzzle13_helper(grids, 2)))

def spin_north(data, m, n):
    ndata = [['.'] * n for _ in range(m)]
    for j in range(n):
        to_place = 0
        for i in range(m):
            if data[i][j] == '#':
                ndata[i][j] = '#'
                to_place = i + 1
            elif data[i][j] == 'O':
                ndata[to_place][j] = 'O'
                to_place += 1
    return ndata

def spin_west(data, m, n):
    ndata = [['.'] * n for _ in range(m)]
    for i in range(m):
        to_place = 0
        for j in range(n):
            if data[i][j] == '#':
                ndata[i][j] = '#'
                to_place = j + 1
            elif data[i][j] == 'O':
                ndata[i][to_place] = 'O'
                to_place += 1
    return ndata

def spin_south(data, m, n):
    ndata = [['.'] * n for _ in range(m)]
    for j in range(n):
        to_place = m - 1
        for i in reversed(range(m) ):
            if data[i][j] == '#':
                ndata[i][j] = '#'
                to_place = i - 1
            elif data[i][j] == 'O':
                ndata[to_place][j] = 'O'
                to_place -= 1
    return ndata

def spin_east(data, m, n):
    ndata = [['.'] * n for _ in range(m)]
    for i in range(m):
        to_place = n - 1
        for j in reversed(range(n) ):
            if data[i][j] == '#':
                ndata[i][j] = '#'
                to_place = j - 1
            elif data[i][j] == 'O':
                ndata[i][to_place] = 'O'
                to_place -= 1
    return ndata

def puzzle14():
    data = open('inputs/puzzle14', 'r').read().strip().split('\n')
    data = list(list(x) for x in data)
    m, n = len(data), len(data[0])
    ndata = spin_north(data, m, n)
    print("Puzzle 14 Part 1:", sum((m - i) for i in range(m) for j in range(n) if ndata[i][j] == 'O'))
    TIMES = 10 ** 9
    ndata, recur = data[:], {}
    for x in range(TIMES):
        # spin a cycle
        ndata = spin_north(ndata, m, n)
        ndata = spin_west(ndata, m, n)
        ndata = spin_south(ndata, m, n)
        ndata = spin_east(ndata, m, n)

        tuple_data = tuple(tuple(x) for x in ndata)
        if tuple_data in recur:
            diff = x - recur[tuple_data]
            TIMES = (TIMES - x) % diff - 1
            break
        recur[tuple_data] = x

    for x in range(TIMES):
        # spin a cycle
        ndata = spin_north(ndata, m, n)
        ndata = spin_west(ndata, m, n)
        ndata = spin_south(ndata, m, n)
        ndata = spin_east(ndata, m, n)

    print("Part 2:", sum((m - i) for i in range(m) for j in range(n) if ndata[i][j] == 'O'))

def hash_puzzl15(word):
    current_value = 0
    for letter in word:
        current_value = ((current_value + ord(letter))*17) % 256
    return  current_value

def power_puzzl15(hashmap: dict[int, list[dict[str, int]]]) -> int:
    total = 0
    for box_no, box in hashmap.items():
        for slot, lens in enumerate(box):
            total += (box_no + 1) * (slot + 1) * lens[list(lens.keys())[0]]
    return total

def puzzle15():
    data = open('inputs/puzzle15', 'r').read().strip().split(',')
    result_part1 = 0
    hashmap: dict[int, list[dict[str, int]]] = {key: [] for key in range(256)}

    for word in data:
        word = word.replace("\n", "").strip()
        if word[-1].isdigit():
            focal_length = int(word[-1])
            label = word[:-2]
            hash = hash_puzzl15(label)
            box = hashmap[hash]
            if len(box) != 0:
                labels = list({k: None for lens in box for k in lens.keys()}.keys())
                if label in labels:
                    idx = labels.index(label)
                    box[idx][label] = focal_length
                else:
                    box.append({label: focal_length})
            else:
                box.append({label: focal_length})
        else:
            label = word[:-1]
            hash = hash_puzzl15(label)
            box = hashmap[hash]
            labels = list({k: None for lens in box for k in lens.keys()}.keys())
            if label in labels:
                del box[labels.index(label)]
        result_part1 = result_part1 + hash_puzzl15(word)

    result_part2 = power_puzzl15(hashmap)

    print("The result of the puzzle 15 part 1 is: "+str(result_part1))
    print("The result of the puzzle 15 part 2 is: "+str(result_part2))


def parse_input_file():
    with open('inputs/puzzle16', 'r') as f:
        file = f.read()

    matrix = []
    for y, line in enumerate(file.split('\n')):
        matrix_y = []
        for symbol in list(line):
            matrix_y.append(symbol)
        matrix.append(matrix_y)

    return matrix

def next_state(current_state, dir):
    UP = 'up'
    DOWN = 'down'
    LEFT = 'left'
    RIGHT = 'right'

    DIR_TO_COORD = {
        UP: (0, -1),
        DOWN: (0, 1),
        LEFT: (-1, 0),
        RIGHT: (1, 0)
    }
    (x, y), _ = current_state
    xd, yd = DIR_TO_COORD[dir]
    return ((x + xd, y + yd), dir)


def is_valid(state):
    '''
        returns True iff (x,y) in matrix limit && state not in visited_states
    '''
    (x, y), _ = state
    if x < 0 or y < 0 or x >= L or y >= L:
        return False
    if state in visited_states:
        return False
    return True

def puzzle16_part1():
    UP = 'up'
    DOWN = 'down'
    LEFT = 'left'
    RIGHT = 'right'

    global L, visited_states
    matrix = parse_input_file()  # matrix[y][x] ∈ {.,|,-,/,\}
    L = len(matrix)

    visited_tiles = set()  # set of visited tiles (x, y)
    visited_states = set()  # set of visited states ((x, y), dir)

    s0 = ((0, 0), RIGHT)  # initial state

    queue = deque()
    queue.append(s0)

    while queue:
        s = queue.popleft()

        if (not is_valid(s)):
            continue

        (x, y), dir = s
        visited_states.add(s)
        visited_tiles.add((x, y))

        symbol = matrix[y][x]

        # NOTE: bad
        match symbol:
            case '.':
                queue.append(next_state(s, dir))
            case '\\':
                match dir:
                    case 'down':
                        queue.append(next_state(s, RIGHT))
                    case 'up':
                        queue.append(next_state(s, LEFT))
                    case 'left':
                        queue.append(next_state(s, UP))
                    case 'right':
                        queue.append(next_state(s, DOWN))
            case '/':
                match dir:
                    case 'down':
                        queue.append(next_state(s, LEFT))
                    case 'up':
                        queue.append(next_state(s, RIGHT))
                    case 'left':
                        queue.append(next_state(s, DOWN))
                    case 'right':
                        queue.append(next_state(s, UP))
            case '-':
                match dir:
                    case 'left' | 'right':
                        queue.append(next_state(s, dir))
                    case 'up' | 'down':
                        queue.append(next_state(s, RIGHT))
                        queue.append(next_state(s, LEFT))
            case '|':
                match dir:
                    case 'up' | 'down':
                        queue.append(next_state(s, dir))
                    case 'left' | 'right':
                        queue.append(next_state(s, UP))
                        queue.append(next_state(s, DOWN))

    # Part 1
    print("Puzzle 16 result for part 1 is: "+str(len(visited_tiles)))

def puzzle16_part2():
    UP = 'up'
    DOWN = 'down'
    LEFT = 'left'
    RIGHT = 'right'
    global L, visited_states
    matrix = parse_input_file()  # matrix[y][x] ∈ {.,|,-,/,\}
    L = len(matrix)

    max_val = 0

    initial_states = set()
    initial_states.update([((x, 0), DOWN) for x in range(L)])
    initial_states.update([((x, L - 1), UP) for x in range(L)])
    initial_states.update([((0, y), RIGHT) for y in range(L)])
    initial_states.update([((L - 1, y), LEFT) for y in range(L)])

    for initial_state in initial_states:
        visited_tiles = set()  # set of visited tiles (x, y)
        visited_states = set()  # set of visited states ((x, y), dir)

        s0 = initial_state

        queue = deque()
        queue.append(s0)

        while queue:
            s = queue.popleft()

            if (not is_valid(s)):
                continue

            (x, y), dir = s
            visited_states.add(s)
            visited_tiles.add((x, y))

            symbol = matrix[y][x]

            # NOTE: bad
            match symbol:
                case '.':
                    queue.append(next_state(s, dir))
                case '\\':
                    match dir:
                        case 'down':
                            queue.append(next_state(s, RIGHT))
                        case 'up':
                            queue.append(next_state(s, LEFT))
                        case 'left':
                            queue.append(next_state(s, UP))
                        case 'right':
                            queue.append(next_state(s, DOWN))
                case '/':
                    match dir:
                        case 'down':
                            queue.append(next_state(s, LEFT))
                        case 'up':
                            queue.append(next_state(s, RIGHT))
                        case 'left':
                            queue.append(next_state(s, DOWN))
                        case 'right':
                            queue.append(next_state(s, UP))
                case '-':
                    match dir:
                        case 'left' | 'right':
                            queue.append(next_state(s, dir))
                        case 'up' | 'down':
                            queue.append(next_state(s, RIGHT))
                            queue.append(next_state(s, LEFT))
                case '|':
                    match dir:
                        case 'up' | 'down':
                            queue.append(next_state(s, dir))
                        case 'left' | 'right':
                            queue.append(next_state(s, UP))
                            queue.append(next_state(s, DOWN))

        max_val = max(max_val, len(visited_tiles))

    # Part 2
    print("Puzzle16 result for part2 is: "+str(max_val))
def puzzle16():
    puzzle16_part1()
    puzzle16_part2()

def puzzle17_helper(parts: str, mmin: int, mmax: int):
    legal_moves = {(0, 0): ((1, 0), (0, 1)),
                   (0, -1): ((1, 0), (-1, 0)),
                   (1, 0): ((0, -1), (0, 1)),
                   (0, 1): ((1, 0), (-1, 0)),
                   (-1, 0): ((0, -1), (0, 1))}

    with open('inputs/puzzle17') as f:
        grid = [[int(x) for x in line] for line in f.read().splitlines()]
    destination_coord = (len(grid[0]) - 1, len(grid) - 1)
    heap = [(0, (0, 0), (0, 0))]
    heat_map = {(0, 0): 0}
    visited = set()

    while heap:
        heat_loss, coord, direction = heappop(heap)

        if coord == destination_coord:
            break

        if (coord, direction) in visited: continue

        visited.add((coord, direction))

        for new_direction in legal_moves[direction]:
            new_heat_loss = heat_loss
            for steps in range(1, mmax + 1):
                new_coord = (coord[0] + steps * new_direction[0], coord[1] + steps * new_direction[1])
                if new_coord[0] < 0 or new_coord[1] < 0 \
                        or new_coord[0] > destination_coord[0] or new_coord[1] > destination_coord[1]:
                    continue
                new_heat_loss = new_heat_loss + grid[new_coord[1]][new_coord[0]]
                if steps >= mmin:
                    new_node = (new_coord, new_direction)
                    if heat_map.get(new_node, inf) <= new_heat_loss: continue
                    heat_map[new_node] = new_heat_loss
                    heappush(heap, (new_heat_loss, new_coord, new_direction))
    print(parts, heat_loss)
def puzzle17():
    puzzle17_helper("Solution puzzle17 Part 1:", 1, 3)
    puzzle17_helper("Solution puzzle17 Part 2:", 4, 10)

if __name__ == '__main__':
    bucle = "S"
    while(bucle == "S"):
        puzz = input("Which puzzle do you want to solve?(1-25): ")
        if(puzz == "1"):
            puzzle1()
        elif(puzz == "2"):
            puzzle2()
        elif (puzz == "3"):
            puzzle3()
        elif (puzz == "4"):
            puzzle4()
        elif (puzz == "5"):
            puzzle5()
        elif (puzz == "6"):
            puzzle6()
        elif (puzz == "7"):
            puzzle7()
        elif (puzz == "8"):
            puzzle8()
        elif (puzz == "9"):
            puzzle9()
        elif (puzz == "10"):
            puzzle10()
        elif (puzz == "11"):
            puzzle11()
        elif (puzz == "12"):
            puzzle12()
        elif (puzz == "13"):
            puzzle13()
        elif (puzz == "14"):
            puzzle14()
        elif (puzz == "15"):
            puzzle15()
        elif (puzz == "16"):
            puzzle16()
        elif (puzz == "17"):
            puzzle17()
        bucle = input("Do you want to solve another puzzle? (s/n): ").upper()