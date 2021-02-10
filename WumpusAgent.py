# Hannah Gorel, William Capon, Christian Oliverio, Liam Pratt
# WumpusAgent.py
# Date: 2/4/2021
# Assignment:Project 1: Hunt the Wumpus
# Description: Agent designed to retrieve the gold from the cave
# while avoiding pits and the wumpus, and then escape alive!

# parameters for type of game
gametype: int = 0
numarrows: int = 0
numwumpi: int = 0

# map and player virtual positions
# actual_player_x_position_in_array = playerpositionx + virtualoriginx
map = []
virtualoriginy: int = 0
virtualoriginx: int = 0
playerpositionx: int = 0
playerpositiony: int= 0

maxxpos: int = 999
minxpos: int = -999
maxypos: int = 999
minypos: int = -999

# determines searching or escaping state of AI
foundgold: bool = False

#actions AI can do
moveup: str = 'N'
movedown: str = 'S'
moveleft: str = 'W'
moveright: str = 'E'

shootup: str = 'SN'
shootdown: str = 'SS'
shootleft: str = 'SW'
shootright: str = 'SE'

climbout: str = 'C'
grabgold: str = 'G'

# AI can either be searching or escaping
# 1. Searching
# 2. Escaping
state: str = ''

# if a wumpus or pit is nearby, this will be flagged for the agent
dangernear: bool = False

# list of past moves, for memory
pastmoves: list[str] = []

def setParams(type, arrows, wumpi):
    global gametype
    global numarrows
    global numwumpi
    gametype = type
    numarrows = arrows
    numwumpi = wumpi

    # sets map with nothing but start square
    temp = ['E']
    map.append(temp)

def printMap():
    print("MAP")
    for x in range(len(map)):
        for y in range(len(map[x])):
            if(y == getActualPlayerXPosition() and getActualPlayerYPosition() == x):
                print('*', ' ', end='',)
            else:
                print(map[x][y], ' ', end = '')
        print()

def getMove(percept = ''):
    global playerpositionx
    global playerpositiony
    global virtualoriginx
    global virtualoriginy

    checkBump(percept)
    print("Percept:", percept, "\tPlyPos: x:", playerpositionx, "y:", playerpositiony)
    print("virtualorigin x:", virtualoriginx, "y:", virtualoriginy)
    printMap()
    print()
    nextmove = parsePercept(percept)
    editMapAndPlayerPosition(nextmove)
    pastmoves.append(nextmove)

    return nextmove

def checkBump(perceptstring):
    if (perceptstring.__contains__('U')):
        lastmove = pastmoves.pop()
        undoMoveSetLimitRemoveRowOrColumn(lastmove)

def parsePercept(percept):
    global foundgold

    #if(foundgold == False):
    #    state = 'Searching'
    #elif(foundgold == True):
    #    state = 'Escaping'

    move = moveleft

    if (percept.__contains__('G')):
        move = grabgold
        foundgold = True

    pastmoves.append(move)
    return move

# tracks player position, also when discovering a new row or column,
# adds new column to list, updates virtual origin for AI
# in order to make a move, must be within grid,
# grid walls are defined by minypos, maxypos, minxpos, and maxxpos
def editMapAndPlayerPosition(themove):
    global playerpositionx
    global playerpositiony
    global virtualoriginy
    global virtualoriginx

    if themove == moveup and playerpositiony > minypos:
        if virtualoriginy + playerpositiony == 0:
            map.insert(0, [0] * len(map[0]))
            virtualoriginy = virtualoriginy + 1
        playerpositiony = playerpositiony - 1

    if themove == movedown and playerpositiony < maxypos:
        if virtualoriginy + playerpositiony == len(map) - 1:
            map.append([0] * len(map[0]))
        playerpositiony = playerpositiony + 1

    if themove == moveleft and playerpositionx > minxpos:
        if virtualoriginx + playerpositionx == 0:
            virtualoriginx = virtualoriginx + 1
            for row in range(len(map)):
                map[row].insert(0, 0)
        playerpositionx = playerpositionx - 1

    if themove == moveright and playerpositionx < maxxpos:
        if virtualoriginx + playerpositionx == len(map[0]) - 1:
            for row in range(len(map)):
                map[row].append(0)
        playerpositionx = playerpositionx + 1

# this method undoes the last move,
# so that when a wall is hit, the max and min x or y
# a player can move is set, this way we will
# never run into walls again
def undoMoveSetLimitRemoveRowOrColumn(last_move):
    global playerpositionx
    global playerpositiony
    global virtualoriginx
    global virtualoriginy
    global minxpos
    global maxxpos
    global minypos
    global maxypos
    # undoes last move, also sets limit of
    # player x and y values to current pos
    if last_move == moveleft:
        # when removing left column, virtual origin needs to be adjusted leftward
        # to account for the move of virtual origin of last move
        virtualoriginx = virtualoriginx - 1
        for row in range(len(map)):
            # map[row].pop(removes_column_of_index_passed)
            map[row].pop(0)
        #player must be incremented to right spot, x low limit set
        minxpos = playerpositionx
        playerpositionx = playerpositionx + 1
    if last_move == moveright:
        for row in range(len(map)):
            # pops rightmost column in map
            map[row].pop()
        # have to set x max move to the right, also decrement to put back in map
        maxxpos = playerpositionx
        playerpositionx = playerpositionx - 1
    if last_move == moveup:
        # when removing top row, need to account for virtual origin
        # being adjusted by move, so decrement to put back in correct spot
        virtualoriginy = virtualoriginy - 1
        #map.pop(removes_the_row_of_index_passed)
        map.pop(0)
        # set minimum y value, reset player up a square
        minypos = playerpositiony
        playerpositiony = playerpositiony + 1
    if last_move == movedown:
        #removes the whole bottom row
        map.pop()
        # player mover decremented to correct spot, also sets limit
        maxypos = playerpositiony
        playerpositiony = playerpositiony - 1


def getActualPlayerYPosition():
    return playerpositiony + virtualoriginy

def getActualPlayerXPosition():
    return playerpositionx + virtualoriginx