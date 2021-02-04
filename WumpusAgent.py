

squareRisk = {}

actionSequence = []
playerx = 0
playery = 0

haveGold = False
moving = 0
arrows = 0
wumpai = 0

def setParams(gameType,numarrows,numwumpai):
    moving = gameType
    arrows = numarrows
    wumpai = numwumpai
    haveGold = False
    squareRisk = {}
    safeSquares = []
    actionSequence = []
    playerx = 0
    playery = 0


def assignDanger(x,y,danger):
    for xx in range(x-1,x+2):
        for yy in range(y-1,y+2):
            if(xx == x or yy == y): #only do cardinal directions
                if (str(xx) + str(yy) in squareRisk.keys()):
                    squareRisk[str(xx) + str(yy)] += danger
                else:
                    squareRisk[str(xx) + str(yy)] = danger



def handlePercept(p):
    global playerx,playery
    safe = True
    if (p == 'U'): #handle bump
        move = actionSequence[len(actionSequence) - 1]
        target = [0, 0]
        if (move == 'N'):
            target[1] = -1
        if (move == 'E'):
            target[0] = 1
        if (move == 'S'):
            target[1] = 1
        if (move == 'W'):
            target[0] = -1
        playerx += -target[0]
        playery += -target[1]
        squareRisk[str(playerx + target[0]) + str(playery + target[1])] = 100
        del (actionSequence[len(actionSequence) - 1])

    if(p == 'S'):
        assignDanger(playerx,playery,1) #wumpus danger
        safe = False
    if(p == 'B'):
        assignDanger(playerx,playery,1) #pit danger
        safe = False


    if(safe):
        assignDanger(playerx,playery,0)



def bestMove():
    global playerx,playery
    bestSpace = [playerx-1,playery]
    lowestDanger = 100000000000
    for xx in range(playerx-1,playerx+2):
        for yy in range(playery-1,playery+2):

            if(xx == playerx or yy == playery):
                if(str(xx) + str(yy) not in squareRisk.keys()):
                    bestSpace = [xx,yy]
                    lowestDanger = 0
                    continue
                if(squareRisk[str(xx) + str(yy)] < lowestDanger):
                    bestSpace = [xx,yy]
                    lowerDanger = squareRisk[str(xx) + str(yy)]
    return bestSpace




def getMove(percepts):
    global haveGold,playerx,playery
    if(haveGold):
        if(len(actionSequence) > 0):
            return actionSequence[len(actionSequence) - 1]
        else:
            return "C"

    perceptList = []
    perceptList.extend(percepts)
    squareRisk[str(playerx) + str(playery)] = 2

    for p in percepts:
        handlePercept(p)
    if 'G' in percepts:
        haveGold = True
        return "G"
    bestSpace = bestMove()
    print(playerx, playery)
    print(bestSpace)
    if(bestSpace[0] < playerx):
        actionSequence.append("W")
        playerx -= 1
        return "W"
    elif(bestSpace[0] > playerx):
        actionSequence.append("E")
        playerx += 1
        return "E"
    elif(bestSpace[1] > playery):
        actionSequence.append("S")
        playery += 1
        return "S"
    else: #if(bestSpace[1] < playery)
        actionSequence.append("N")
        playery -= 1
        return "N"




