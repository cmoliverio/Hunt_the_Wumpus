#Hannah Gorel, William Capon, Christian Oliverio, Liam Pratt
#WumpusAgent.py
#Date: 2/4/2021
#Assignment:Project 1: Hunt the Wumpus
#Description: Agent designed to retrieve the gold from the cave
#while avoiding pits and the wumpus, and then escape alive!

#parameters for type of game
from typing import List, Any
gametype: int = 0
numarrows: int = 0
numwumpi: int = 0

#map
map = []
virtualoriginy = 0
virtualoriginx = 0
playerpositionx = 0
playerpositiony = 0

#determines searching or escaping state of AI
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

#AI can either be searching or escaping
# 1. Searching
# 2. Escaping
state: str = ''

#if a wumpus or pit is nearby, this will be flagged for the agent
dangernear: bool = False

#list of past moves, for memory
pastmoves: list[str] = []

def setParams(type, arrows, wumpi):
    global gametype
    global numarrows
    global numwumpi
    gametype= type
    numarrows = arrows
    numwumpi = wumpi

    #sets map with nothing but start square
    temp = ['START']
    map.append(temp)


movecount = 0
def getMove(percept = ''):

    printMap()

    nextmove: str = parsePercept(percept)
    editMapAndPlayerPosition(nextmove)

    if percept == '':
        print("empty")
    else:
        print(percept)

    return nextmove

def printMap():
    for i in range(0, len(map)):
        print("[", *map[i], "]")

def editMapAndPlayerPosition(themove):
    global playerpositionx
    global playerpositiony
    global virtualoriginy
    global virtualoriginx

    print("position: ", playerpositionx, playerpositiony)
    print("virtual origin: ", virtualoriginx, virtualoriginy)

    #tracks player position, also when discovering a new row or column,
    # adds new column to list, updates virtual origin for AI
    if themove == moveup:
        if virtualoriginy + playerpositiony == 0:
            map.insert(0, [0] * len(map[0]))
            virtualoriginy = virtualoriginy + 1
        playerpositiony = playerpositiony - 1

    if themove == movedown:
        if virtualoriginy - playerpositionx == 0:
            map.append([0] * len(map[0]))
        playerpositiony = playerpositiony + 1



def parsePercept(percept):
    global foundgold
    global movecount
    if(foundgold == False):
        state = 'Searching'
    elif(foundgold == True):
        state = 'Escaping'

    if movecount == 3:
        move = moveup
    else:
        move = movedown
    movecount = movecount + 1
    if(percept.__contains__('G')):
        foundgold = True
        move = grabgold

    if (percept.__contains__("U")):
        pastmoves.pop()


    pastmoves.append(move)
    return move