import collections
import collections as C
import itertools
import re, math, functools, operator
import sys
from collections import deque
from itertools import chain
from typing import Tuple, List, Optional
from heapq import heappush, heappop
from math import inf
import numpy as np
from decimal import Decimal as D, getcontext

def solve_puzzle23(part1):
    D = open("inputs/puzzle23").read().strip()
    L = D.split('\n')
    G = [[c for c in row] for row in L]
    R = len(G)
    C = len(G[0])
    sys.setrecursionlimit(10 ** 6)
    V = set()
    for r in range(R):
        for c in range(C):
          nbr = 0
          for ch,dr,dc in [['^',-1,0],['v', 1,0],['<', 0,-1],['>',0,1]]:
            if (0<=r+dr<R and 0<=c+dc<C and G[r+dr][c+dc]!='#'):
              nbr += 1
          if nbr>2 and G[r][c]!='#':
            V.add((r,c))
    for c in range(C):
        if G[0][c]=='.':
          V.add((0,c))
          start = (0,c)
        if G[R-1][c]=='.':
          V.add((R-1,c))
          end = (R-1,c)

    E = {}
    for (rv,cv) in V:
        E[(rv,cv)] = []
        Q = deque([(rv,cv,0)])
        SEEN = set()
        while Q:
          r,c,d = Q.popleft()
          if (r,c) in SEEN:
            continue
          SEEN.add((r,c))
          if (r,c) in V and (r,c) != (rv,cv):
            E[(rv,cv)].append(((r,c),d))
            continue
          for ch,dr,dc in [['^',-1,0],['v', 1,0],['<', 0,-1],['>',0,1]]:
            if (0<=r+dr<R and 0<=c+dc<C and G[r+dr][c+dc]!='#'):
              if part1 and G[r][c] in ['<', '>', '^', 'v'] and G[r][c]!=ch:
                continue
              Q.append((r+dr,c+dc,d+1))
    count = 0
    ans = 0
    SEEN = [[False for _ in range(C)] for _ in range(R)]
    seen = set()
    def dfs(v,d):
        nonlocal count
        nonlocal ans
        count += 1
        r,c = v
        if SEEN[r][c]:
          return
        SEEN[r][c] = True
        if r==R-1:
          ans = max(ans, d)
        for (y,yd) in E[v]:
          dfs(y,d+yd)
        SEEN[r][c] = False
    dfs(start,0)
    #print(count)
    return ans

getcontext().prec = 50
numParser = re.compile(r"(-?\d+)")
parseNums = lambda inp: [D(x) for x in numParser.findall(inp)]
class Hail:
    def __init__(self, inp, debug=False):
        self.debug = debug
        self.px, self.py, self.pz, self.vx, self.vy, self.vz = parseNums(inp)
        self.XYslope = D('inf') if self.vx == 0 else self.vy / self.vx
        self.ax, self.ay, self.az = 0, 0, 0
    def __repr__(self):
        return str(self)
    def __str__(self):
        return f'<{self.px}, {self.py}, {self.pz} @ {self.vx}, {self.vy}, {self.vz}>'
    def intersectXY(self, other):
        # returns None, if parallel / intersect in a past
        if self.XYslope == other.XYslope:
            return None
        if self.XYslope == float('inf'):  # self is vertical
            intX = self.px
            intY = other.XYslope * (intX - other.px) + other.py
        elif other.XYslope == float('inf'):  # other is vertical
            intX = other.px
            intY = self.XYslope * (intX - self.px) + self.py
        else:
            # y - y1 = m1 * ( x - x1 ) reduced to solve for x
            intX = (self.py - other.py - self.px * self.XYslope + other.px * other.XYslope) / (
                        other.XYslope - self.XYslope)
            intY = self.py + self.XYslope * (intX - self.px)
        intX, intY = intX.quantize(D(".1")), intY.quantize(D(".1"))
        # intY = round(intY)
        selfFuture = np.sign(intX - self.px) == np.sign(self.vx)
        otherFuture = np.sign(intX - other.px) == np.sign(other.vx)
        if not (selfFuture and otherFuture):
            return None
        return (intX, intY)
    def adjust(self, ax, ay, az):
        self.vx -= ax - self.ax
        self.vy -= ay - self.ay
        self.vz -= az - self.az
        assert type(self.vx) is D
        self.XYslope = D('inf') if self.vx == 0 else self.vy / self.vx
        self.ax, self.ay, self.az = ax, ay, az
    def getT(self, p):  # if both vx and vy are 0... good luck
        if self.vx == 0:
            return (p[1] - self.py) / self.vy
        return (p[0] - self.px) / self.vx
    def getZ(self, other, inter):  # given an intersection point and an other Hail
        # now we KNOW: z = pz_i + t_i*(vz_i-aZ)   [t = (inter[0]-px_i)/(vx_i)]
        #              z = pz_j + t_j*(vz_j-aZ)
        # (pz_i - pz_j + t_i*vz_i - t_j*vz_j)/(t_i - t_j) =  aZ
        tS = self.getT(inter)
        tO = other.getT(inter)
        if tS == tO:
            assert self.pz + tS * self.vz == other.pz + tO * other.vz
            return None
        return (self.pz - other.pz + tS * self.vz - tO * other.vz) / (tS - tO)

P = complex
class Grid:
	def __init__(self, input):
		self.size = len(input.splitlines())
		self.grid = set()
		self.positions = set()
		for y, l in enumerate(input.splitlines()):
			for x, v in enumerate(l):
				if v == '#':
					self.grid.add(P(x,y))
				if v == 'S':
					self.positions.add(P(x,y))
	def step(self):
		newPos = set()
		for p in self.positions:
			for d in (1,-1,1j,-1j):
				if self.wrap(p+d) not in self.grid:
					newPos.add(p+d)
		self.positions = newPos
	def wrap(self, p):
		return P(p.real%self.size, p.imag%self.size)
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
    print("Part 1 puzzle 4 result is: " +str(part1))
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

def puzzle18():
    y1, x1 = 0, 0
    y2, x2 = 0, 0
    vertices1 = []
    vertices2 = []
    perimeter1 = 0
    perimeter2 = 0
    with open("inputs/puzzle18") as file:
        for row in file:
            dir1, n1, p2instr = row.split()
            n1 = int(n1)
            dir2 = p2instr[-2]
            n2 = int(p2instr[2:-2], 16)
            vertices1.append((y1, x1))
            perimeter1 += n1
            if dir1 == "U":
                y1 -= n1
            elif dir1 == "R":
                x1 += n1
            elif dir1 == "D":
                y1 += n1
            elif dir1 == "L":
                x1 -= n1
            vertices2.append((y2, x2))
            perimeter2 += n2
            if dir2 == "3":
                y2 -= n2
            elif dir2 == "0":
                x2 += n2
            elif dir2 == "1":
                y2 += n2
            elif dir2 == "2":
                x2 -= n2
    area1, area2 = 0, 0
    for i, (y, x) in enumerate(vertices1):
        y2, x2 = vertices1[(i + 1) % len(vertices1)]
        area1 += x * y2 - x2 * y
    for i, (y, x) in enumerate(vertices2):
        y2, x2 = vertices2[(i + 1) % len(vertices2)]
        area2 += x * y2 - x2 * y
    print(area1 // 2 + perimeter1 // 2 + 1)
    print(area2 // 2 + perimeter2 // 2 + 1)

def build_single_workflow_puzzle19(line, Condition, XMAS):
    conds = []
    for entry in line.split(","):
        if ":" in entry:
            xmas, op, n, res = re.search(r"(\w)([<>])(\d+):(\w+)", entry).groups()
            conds.append(Condition(XMAS[xmas], op, int(n), res))
        else:
            conds.append(Condition(None, None, None, entry))
    return conds

def parse_puzzle19(text, Condition, XMAS):
    workflows, parts = {}, []
    for l in text.split("\n\n")[0].split("\n"):
        label, l_text = l.split("{")
        workflows[label] = build_single_workflow_puzzle19(l_text[:-1], Condition, XMAS)
    for l in text.split("\n\n")[1].split("\n"):
        parts.append(tuple(map(int, re.findall("\d+", l))))
    return workflows, parts

def process_single_part_workflow_puzzle19(workflow, part):
    loc = "in"
    while loc not in "AR":
        for cond in workflow:
            if not cond.op:
                return cond.result
            else:
                op = operator.lt if cond.op == "<" else operator.gt
                if op(part[cond.xmas], cond.n):
                    return cond.result

def puzzle19_part1(workflows, parts):
    accepted = []
    for part in parts:
        loc = "in"
        while loc not in "AR":
            loc = process_single_part_workflow_puzzle19(workflows[loc], part)
        accepted.append(part) if loc == "A" else None
    print(sum(sum(a) for a in accepted))

def split_gaggle_puzzle19(gg, xmas, n):
    a = tuple((g[0], g[1]) if xmas != i else (g[0], n - 1) for i, g in enumerate(gg))
    b = tuple((g[0], g[1]) if xmas != i else (n, g[1]) for i, g in enumerate(gg))
    return a, b

def process_puzzle19(workflow, gaggle, is_empty_gaggle):
    to_enqueue = []
    for cond in workflow:
        if is_empty_gaggle(gaggle):
            continue
        elif not cond.op:
            to_enqueue.append((cond.result, gaggle))
        else:
            xmas, op, n, result = cond
            if op == "<":
                a, b = split_gaggle_puzzle19(gaggle, xmas, n)
                if not is_empty_gaggle(a):
                    to_enqueue.append((result, a))
                gaggle = b
            else:
                a, b = split_gaggle_puzzle19(gaggle, xmas, n + 1)
                if not is_empty_gaggle(b):
                    to_enqueue.append((result, b))
                gaggle = a
    return to_enqueue

def puzzle19_part2(workflows, is_empty_gaggle):
    accepted = 0
    q = [("in", ((1, 4000), (1, 4000), (1, 4000), (1, 4000)))]
    while q:
        wf_label, gaggle = q.pop()
        if wf_label == "A":
            accepted += math.prod(g[1] - g[0] + 1 for g in gaggle)
        elif wf_label != "R":
            q.extend(process_puzzle19(workflows[wf_label], gaggle, is_empty_gaggle))
    print(accepted)

def puzzle19():
    XMAS = {"x": 0, "m": 1, "a": 2, "s": 3}
    Condition = collections.namedtuple("Condition", ("xmas", "op", "n", "result"))
    is_empty_gaggle = lambda g: any(x[1] < x[0] for x in g)
    workflows, parts = parse_puzzle19(open("inputs/puzzle19").read(), Condition, XMAS)
    puzzle19_part1(workflows, parts)
    puzzle19_part2(workflows, is_empty_gaggle)

def read_lines_to_list(FILE) -> List[str]:
    lines: List[str] = []
    with open(FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            split = line.split(" -> ")
            name = split[0]
            flip_flop = name.startswith("%")
            conjunction = name.startswith("&")
            target = split[1].split(", ")
            if flip_flop:
                state = False
                name = split[0][1:]
            elif conjunction:
                state = {}
                name = split[0][1:]
            else:
                state = None
            val = (name, [target, flip_flop, conjunction, state])
            lines.append(val)
    return lines

def puzzle20_part1(FILE):
    lines = read_lines_to_list(FILE)
    mappings = dict((a, b) for (a, b) in lines)
    # For any conjunction modules we must initialize inputs...
    for k, v in mappings.items():
        if v[2]:
            for a, b in mappings.items():
                if k in b[0]:
                    v[3][a] = False
    low = 0
    high = 0
    for _ in range(1000):
        queue = [("broadcaster", 0, None)]
        while queue:
            (curr, signal, input) = queue.pop(0)
            if signal:
                high += 1
            else:
                low += 1
            if curr not in mappings:
                continue
            [targets, is_ff, is_con, state] = mappings[curr]
            if is_ff:
                if not signal:
                    if state:
                        mappings[curr][3] = False
                        new_signal = 0
                    else:
                        mappings[curr][3] = True
                        new_signal = 1
                    for target in targets:
                        queue.append((target, new_signal, curr))
            elif is_con:
                state[input] = bool(signal)
                if all(state.values()):
                    new_signal = 0
                else:
                    new_signal = 1
                for target in targets:
                    queue.append((target, new_signal, curr))
            else:
                for target in targets:
                    queue.append((target, signal, curr))
    answer = low * high
    print(f"Puzzle 20 part 1: {answer}")


def puzzle20_part2(FILE):
    m = {}
    f = {}
    c = {}
    for l in open(FILE, "r").readlines():
        s, *d = l.replace(',', '').replace("->", "").split()
        t = None
        if s != "broadcaster":
            t = s[0]
            s = s[1:]
        m[s] = (t, d)
        f[s] = "off"
        for o in d:
            if o not in c:
                c[o] = {}
            c[o][s] = "low"
        if d == ['rx']:
            r = s
    b = 0
    l = {k: 0 for k in c[r]}
    while True:
        b += 1
        q = [("button", "broadcaster", "low")]
        while q:
            i, n, p = q.pop(0)
            if n not in m:
                continue
            t, d = m[n]
            if t == None:
                for o in d:
                    q.append((n, o, p))
            elif t == '%':
                if p == "low":
                    s = f[n]
                    if s == "off":
                        f[n] = "on"
                        for o in d:
                            q.append((n, o, "high"))
                    else:
                        f[n] = "off"
                        for o in d:
                            q.append((n, o, "low"))
            elif t == '&':
                c[n][i] = p
                if all(v == "high" for v in c[n].values()):
                    for o in d:
                        q.append((n, o, "low"))
                else:
                    for o in d:
                        q.append((n, o, "high"))
                if n == r:
                    for k, v in c[n].items():
                        if v == "high" and l[k] == 0:
                            l[k] = b
        if all(v > 0 for v in l.values()):
            print(f"Puzzle 20 part 2: {functools.reduce((lambda a, b: a * b), l.values())}")
            break

def puzzle20():
    FILE = "inputs/puzzle20"
    puzzle20_part1(FILE)
    puzzle20_part2(FILE)

def find_garden_x(matrix):
    posX = []
    cont_i = 0
    for row in matrix:
        for l in row:
            if(l.upper() == "O"):
                posX.append(cont_i)
        cont_i = cont_i + 1
    return posX

def find_garden_y(matrix):
    posY = []
    for row in matrix:
        cont_j = 0
        for l in row:
            if (l.upper() == "O"):
                posY.append(cont_j)
            cont_j = cont_j + 1
    return posY

def steps_garden(matrix, starting_x, starting_y):
    matrix[starting_x][starting_y] = "."
    if (starting_x - 1 > -1 and matrix[starting_x - 1][starting_y] == '.'):
        matrix[starting_x - 1][starting_y] = "O"
    if (starting_y - 1 > -1 and matrix[starting_x][starting_y - 1] == '.'):
        matrix[starting_x][starting_y - 1] = "O"
    if (starting_x + 1 < len(matrix) and matrix[starting_x + 1][starting_y] == '.'):
        matrix[starting_x + 1][starting_y] = "O"
    if (starting_y + 1 < len(matrix[starting_x]) and matrix[starting_x][starting_y + 1] == '.'):
        matrix[starting_x][starting_y + 1] = "O"
    for i in range(63):
        positionX = find_garden_x(matrix)
        positionY = find_garden_y(matrix)
        for x, y in zip(positionX, positionY):
            matrix[x][y] = "."
        for x, y in zip(positionX, positionY):
            if (x - 1 > -1 and matrix[x - 1][y] == '.'):
                matrix[x - 1][y] = "O"
            if (y - 1 > -1 and matrix[x][y - 1] == '.'):
                matrix[x][y - 1] = "O"
            if (x + 1 < len(matrix) and matrix[x + 1][y] == '.'):
                matrix[x + 1][y] = "O"
            if (y + 1 < len(matrix[x]) and matrix[x][y + 1] == '.'):
                matrix[x][y + 1] = "O"
    cont = 0
    for row in matrix:
        for l in row:
            if(l.upper() == "O"):
                cont = cont + 1
    print_garden(matrix)
    return cont

def print_garden(matrix):
    f = open("puzzle21.out", "w")
    for row in matrix:
        for l in row:
            f.write(l)
        f.write("\n")
    f.close()

def puzzle21_part1_input():
    matrix = []
    staring_x = 0
    starting_y = 0
    cont_i = 0
    cont_j = 0
    for row in open("inputs/puzzle21", "r").readlines():
        array_row = []
        cont_j = 0
        for position in row.replace("\n", ""):
            if (position.upper() == "S"):
                starting_y = cont_j
                starting_x = cont_i
            array_row.append(position)
            cont_j = cont_j + 1
        matrix.append(array_row)
        cont_i = cont_i + 1
    return matrix, starting_x, starting_y

def steps_garden_2(input):
    g = Grid(input)
    # f(x) = how many squares are visited at time 65 + 131*x
    X, Y = [0, 1, 2], []
    target = (26501365 - 65) // 131
    for s in range(65 + 131 * 2 + 1):
        if s % 131 == 65:
            Y.append(len(g.positions))
        if s == 64:
            p1 = len(g.positions)
        g.step()
    poly = np.rint(np.polynomial.polynomial.polyfit(X, Y, 2)).astype(int).tolist()
    return sum(poly[i] * target ** i for i in range(3))

def puzzle21():
    matrix, starting_x, starting_y = puzzle21_part1_input()
    steps = steps_garden(matrix, starting_x, starting_y)
    steps2 = steps_garden_2(open("inputs/puzzle21", "r").read())
    print(f"Puzzle21, part1 solution is: {steps}")
    print(f"Puzzle21, part2 solution is: {steps2}")

def drop_puzzle22(stack, skip=None):
    peaks = C.defaultdict(int)
    falls = 0
    for i, (u, v, w, x, y, z) in enumerate(stack):
        if i == skip: continue
        area = [(a, b) for a in range(u, x + 1)
                for b in range(v, y + 1)]
        peak = max(peaks[a] for a in area) + 1
        for a in area: peaks[a] = peak + z - w
        stack[i] = (u, v, peak, x, y, peak + z - w)
        falls += peak < w
    return not falls, falls

def puzzle22():
    stack = sorted([[*map(int, re.findall(r'\d+', l))]
                    for l in open('inputs/puzzle22')], key=lambda b: b[2])
    drop_puzzle22(stack)
    print(*map(sum, zip(*[drop_puzzle22(stack.copy(), skip=i)
                          for i in range(len(stack))])))

def neighbors(x,y, width, height, grid):
    for dx,dy in ((0,1),(1,0),(0,-1),(-1,0)):
        nx,ny = x+dx,y+dy
        if 0 <= nx < width and 0 <= ny < height:
            if grid[ny][nx] in '.<>^v':
                yield (nx,ny)

def measure(edges, start, head):
    count = 1
    while len(edges[head]) == 2:
        count += 1
        next = [n for _,n in edges[head] if n != start][0]
        start, head = (head, next)
    return (count, head)

def trails(width, height, grid):
    edges = {}
    for y in range(height):
        for x in range(width):
            if grid[y][x] in '.<>^v':
                edges[(x,y)] = [(1,n) for n in neighbors(x,y,width, height, grid)]
    # Collapse all trail segments into a single measured edge
    newedges = {}
    for k,v in edges.items():
        if len(v) != 2:
            newedges[k] = [measure(edges, k, n[1]) for n in v]
    return newedges

def dfs(trails, start, end):
    seen = set([start])
    stack = [(start, 0, seen)]
    mx = 0
    while stack:
        pos, dist, seen = stack.pop()
        if pos == end:
            mx = max(mx, dist)
        for d, next in trails[pos]:
            if next not in seen:
                stack.append((next, dist+d, seen | set([next])))
    return mx

def puzzle23_part1():
    print("Part 1 of puzzle 23 solution is: "+str(solve_puzzle23(True)))

def puzzle23_part2():
    input = open('inputs/puzzle23').read()
    grid = tuple(input.split('\n'))
    width = len(grid[0])
    height = len(grid)
    start = (1, 0)
    end = (width - 2, height - 1)
    #6874
    print("Part 2 of puzzle 23 solution is: "+str(dfs(trails(width, height, grid), start, end)))

def puzzle23():
    puzzle23_part1()
    puzzle23_part2()

def puzzle24_p1(inp, pMin, pMax, debug=False):
    hailstones = []
    for row in inp.strip().splitlines():
        hailstones.append(Hail(row, debug=debug))
    sm = 0
    for idx, H1 in enumerate(hailstones):
        for H2 in hailstones[idx + 1:]:
            p = H1.intersectXY(H2)
            if p is None:
                if debug: print(f'NO INTERSECT : {H1} x {H2}')
            elif p[0] >= pMin and p[0] <= pMax and p[1] >= pMin and p[1] <= pMax:
                if debug: print(f'YES {H1} x {H2} (@ {p})')
                sm += 1
            else:
                if debug: print(f'NO [OUTSIDE] :{H1} x {H2} (@ {p})')
    return sm


def puzzle24_p2(inp, debug=False):
    hailstones = []
    for row in inp.strip().splitlines():
        hailstones.append(Hail(row, debug=debug))
    N = 0
    while True:
        for X in range(N + 1):
            Y = N - X
            for negX in (-1, 1):
                for negY in (-1, 1):
                    aX = X * negX
                    aY = Y * negY
                    # if debug: print(f'checking v=<{aX},{aY},?>')
                    H1 = hailstones[0]
                    H1.adjust(aX, aY, 0)
                    inter = None
                    # if debug: print(f'comparing v {H1}')
                    for H2 in hailstones[1:]:
                        H2.adjust(aX, aY, 0)
                        p = H1.intersectXY(H2)
                        if p is None:
                            # if debug: print(f'v {H2} — NONEE')
                            break
                        if inter is None:
                            # if debug: print(f'v {H2} — setting to {p}')
                            inter = p
                            continue
                        if p != inter:
                            # if debug: print(f'v {H2} — NOT SAME P {p}')
                            break
                        # if debug: print(f'v {H2} — continuing{p}')
                    if p is None or p != inter:
                        continue
                    # if debug: print(f'FOUND COMMON INTERSECTION {p}')
                    # we escaped intersecting everything with H1 with a single valid XY point!
                    aZ = None
                    H1 = hailstones[0]
                    # print(f'v {H1}')
                    for H2 in hailstones[1:]:
                        nZ = H1.getZ(H2, inter)
                        if aZ is None:
                            # print(f'first aZ is {aZ} from {H2}')
                            aZ = nZ
                            continue
                        elif nZ != aZ:
                            return
                            break
                    if aZ == nZ:
                        H = hailstones[0]
                        Z = H.pz + H.getT(inter) * (H.vz - aZ)
                        return int(Z + inter[0] + inter[1])
        N += 1

def puzzle24():
    with open('inputs/puzzle24') as f:
        d24s = f.read()
    print("The solution of part 1 for the puzzle 24 is: "+str(puzzle24_p1(d24s, 200000000000000, 400000000000000, debug=False)))
    print("The solution of part 2 for the puzzle 24 is: " + str(puzzle24_p2(d24s, debug=False)))

def puzzle25_pathing(src, dst, cuts, nodes, cs):
    come_from = {src: ""}
    to_visit = set()
    to_visit.add(src)
    while len(to_visit):
        n = to_visit.pop()
        for nn in cs[n]:
            proposed_edge = tuple(sorted((n, nn)))
            if proposed_edge in cuts:
                continue
            if nn not in come_from:
                assert(nn != n)
                come_from[nn] = n
                if nn == dst:
                    break
                to_visit.add(nn)
    if dst not in come_from:
        return None
    path = set()
    cur = dst
    while cur != src:
        prev = come_from[cur]
        path.add(tuple(sorted((cur, prev))))
        cur = prev
    return path

def puzzle25():
    infile = open("inputs/puzzle25")
    # infile = open("sample.txt")
    nodes = set()
    cs = collections.defaultdict(set)
    for line in infile:
        line = line.strip()
        ends = line.split()
        fr = ends[0][:-1]
        nodes.add(fr)
        for to in ends[1:]:
            cs[fr].add(to)
            cs[to].add(fr)
            nodes.add(to)
    nodes = list(nodes)
    node_unions = {v: i for i, v in enumerate(nodes)}
    node_union_count = len(nodes)
    known_separate = set()
    for n0, n1 in itertools.combinations(nodes, 2):
        if node_unions[n0] == node_unions[n1]:
            continue
        if frozenset([node_unions[n0], node_unions[n1]]) in known_separate:
            continue
        path = set()
        exclude = set()
        for _ in range(4):
            exclude.update(path)
            path = puzzle25_pathing(n0, n1, exclude, nodes, cs)
            if path is None:
                break
        if path is None:
            known_separate.add(frozenset([node_unions[n0], node_unions[n1]]))
        else:
            # merge nodes
            node_union_count -= 1
            sys.stdout.flush()
            to_replace = node_unions[n1]
            to_replace_with = node_unions[n0]
            for k in node_unions:
                if node_unions[k] == to_replace:
                    node_unions[k] = to_replace_with
            known_separate = set(
                (s - frozenset([to_replace])).union(frozenset([to_replace_with])) if to_replace in s else s for s in
                known_separate)
    root_ids = set(node_unions.values())
    union0, union1 = iter(root_ids)
    union0_size = sum(1 if v == union0 else 0 for v in node_unions.values())
    union1_size = sum(1 if v == union1 else 0 for v in node_unions.values())
    print("Solution of puzzle 25 is: "+str(union0_size * union1_size))

def menu(puzz):
    if (puzz == "1"):
        puzzle1()
    elif (puzz == "2"):
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
    elif (puzz == "18"):
        puzzle18()
    elif (puzz == "19"):
        puzzle19()
    elif (puzz == "20"):
        puzzle20()
    elif (puzz == "21"):
        puzzle21()
    elif (puzz == "22"):
        puzzle22()
    elif (puzz == "23"):
        puzzle23()
    elif (puzz == "24"):
        puzzle24()
    elif (puzz == "25"):
        puzzle25()
    else:
        print("Choose a number between 1 and 25 included both. You dumbass!!!")

if __name__ == '__main__':
    bucle = "S"
    while(bucle == "S"):
        puzz = input("Which puzzle do you want to solve?(1-25): ")
        menu(puzz)
        bucle = input("Do you want to solve another puzzle? (s/n): ").upper()