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

pastmoves = []

def setParams(type, arrows, wumpi):
    gametype=type
    numarrows = arrows
    numwumpi = wumpi


def getMove(percept = ''):
    move = 'N'
    print(percept)

    if(percept.__contains__("U")):
        pastmoves.remove(len(pastmoves))

    pastmoves.append(move)
    return move