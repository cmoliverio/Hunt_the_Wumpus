#Hannah Gorel, William Capon, Christian Oliverio, Liam Pratt
#WumpusAgent.py
#Date: 2/4/2021
#Assignment:Project 1: Hunt the Wumpus
#Description: Agent designed to retrieve the gold from the cave
#while avoiding pits and the wumpus, and then escape alive!

#parameters for type of game
gametype=0
numarrows=0
numwumpi=0

#determines state of ai
foundgold = False

#actions AI can do
moveup = 'N'
movedown = 'S'
moveleft = 'W'
moveright = 'E'

shootup = 'SN'
shootdown = 'SS'
shootleft = 'SW'
shootright = 'SE'

climbout = 'C'
grabgold = 'G'

#AI can have 2 states, states of AI are of the following
# 1. Searching
# 2. Escaping
state = ''

pastmoves = []

def setParams(type, arrows, wumpi):
    gametype = type
    numarrows = arrows
    numwumpi = wumpi


def getMove(percept = ''):

    nextmove = parsePercept(percept)

    if(percept == ''):
        print("empty")
    else:
        print(percept)

    return nextmove

def parsePercept(percept):
    global foundgold
    if(foundgold == False):
        state = 'Searching'
    elif(foundgold == True):
        state = 'Escaping'

    move = moveup

    #print(*pastmoves)

    if(percept.__contains__('G')):
        foundgold = True
        move = grabgold

    if (percept.__contains__("U")):
        pastmoves.pop()

    pastmoves.append(move)
    return move