import re

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