# Hannah Gorel, William Capon, Christian Oliverio, Liam Pratt
# WumpusAgent.py
# Date: 2/11/2021
# Assignment:Project 1: Hunt the Wumpus
# Description: Agent designed to retrieve the gold from the cave
# while avoiding pits and the wumpus, and then escape alive!
import random

# parameters for type of game
gametype = 0
numarrows = 0
numwumpi = 0

playerx = 0
playery = 0

maxxpos: int = 999
minxpos: int = -999
maxypos: int = 999
minypos: int = -999

# determines searching or escaping state of AI
foundgold: bool = False

# actions AI can do
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

# store all past locations as a list, so when trying to find a route home,
# can just retrace all steps... not worth finding an actual path

pastLocations: list = []

# list of all squares we know don't have an immediate wumpus or pit
# but haven't been in yet
safeUnvisited: list = []

# list of all moves
moveHistory: list = []

# dictionary to store all information about spaces... no pitfall bc no breeze etc
# will be a dictionary with key (x,y) and information [bool breeze, bool stench] with both defaulting to null and
# then being updated when more information is known
knownInfo: dict = {}


def setParams(type, arrows, wumpi):
    global gametype
    global numarrows
    global numwumpi
    gametype = type
    numarrows = arrows
    numwumpi = wumpi

def updatePlayerPosition(move):
    global playerx
    global playery
    global pastLocations
    global safeUnvisited

    if move == moveup:
        playery += 1
    if move == movedown:
        playery -=1
    if move == moveright:
        playerx +=1
    if move == moveleft:
        playerx -=1
    #add the place to pastLocations if not already in the last 100
    if [playerx, playery] not in pastLocations[-100:]:
        pastLocations.append([playerx, playery])
    #remove the place from safeUnvisited list
    if [playerx, playery] in safeUnvisited:
        safeUnvisited.remove([playerx, playery])

def getMove(percept):
    global playerx
    global playery
    global moveHistory
    global safeUnvisited

    # if already found gold, just backtrack -- don't worry about other things because everything in move history
    # is known to be safe to return to -- unless with moving wumpus and there's no way to track them realistically
    # so best bet is just to retrace footsteps :)
    if foundgold is True:
        lastmove = moveHistory.pop()
        if lastmove == grabgold:
            lastmove = moveHistory.pop()
        move = invertMove(lastmove)
        print(move)
        updatePlayerPosition(move)
        return move

    # check to see if you're at an edge already... deal w/ this first
    checkBump(percept)

    move_recommendation = checkPerceptAndUpdateDict(percept)

    # the checkPerceptAndUpdateDict function only returns a move recommendation in very specific cases, so if it doesn't
    # recommend one, best to see if any of the spaces around you are safe and unexplored, because it's much better
    # to pursue one of those routes than one that is potentially risky

    if len(move_recommendation) == 0:
        # no move recommended by percept -- so check the safe unexplored paths and choose one of them
        if len(safeUnvisited) > 0:
            safe_spots = []
            # if the spots immediately around you are available, go there!
            for i in safeUnvisited[-50:]:
                if i[0] == playerx and i[1] == playery - 1:
                    safe_spots.append(movedown)
                if i[0] == playerx and i[1] == playery + 1:
                    safe_spots.append(moveup)
                if i[0] == playerx + 1 and i[1] == playery:
                    safe_spots.append(moveright)
                if i[0] == playerx - 1 and i[1] == playery:
                    safe_spots.append(moveleft)
            if len(safe_spots) > 0:
                move_index = random.randint(0, len(safe_spots)-1)
                move = safe_spots[move_index]
                if isValidMove(move):
                    updatePlayerPosition(move)
                    moveHistory.append(move)
                    return move

        # if no safe paths -- gotta pick because no infinite loops and just hope for the best
        # randomly select either up down left or right
        random_move = makeRandomMove()
        updatePlayerPosition(random_move)
        moveHistory.append(random_move)
        print("executing random move :(")
        return random_move

    else:
        moveHistory.append(move_recommendation)
        updatePlayerPosition(move_recommendation)
        return move_recommendation


def makeRandomMove():
    rand_index = random.randint(0, 3)
    if rand_index == 0:
        rand_move = movedown
    if rand_index == 1:
        rand_move = moveup
    if rand_index == 2:
        rand_move = moveright
    if rand_index == 3:
        rand_move = moveleft

    if isValidMove(rand_move):
        return rand_move
    else:
        return makeRandomMove()

def checkPerceptAndUpdateDict(percept):
    global foundgold
    global playerx
    global playery
    global knownInfo
    global safeUnvisited
    breeze = False
    stench = False
    glitter = False
    scream = False
    dangerlevel = 0
    nextmove = ''

    # handle breeze
    if "B" in percept:
        # increase the dangerlevel by 1
        breeze = True
        dangerlevel += 1
    if "W" in percept:
        stench = True
        dangerlevel += 1
    if "G" in percept:
        glitter = True
    if "C" in percept:
        scream = True

    # now all boolean values accurately reflect whether or not the percept was involved
    # much easier to see what's happening now

    # if the square is safe, no dangerous percepts, set all the surrounding squares
    # to safeUnvisited, because those should be our next moves
    if dangerlevel == 0:
        # we know this is a safe square, and all four places around this are safe
        # to at least move into
        safeUnvisited.append([playerx + 1, playery])
        safeUnvisited.append([playerx, playery + 1])
        safeUnvisited.append([playerx - 1, playery])
        safeUnvisited.append([playerx, playery - 1])

    # if in square with gold -- grab it!
    if glitter is True:
        print("FOUND GOLD")
        foundgold = True
        nextmove = grabgold

    # if scream, we know wumpus is dead and we may decrease our internal wumpus count
    # by 1 -- other than that this doesn't really make a difference because still need to move and find gold
    if scream is True:
        numwumpi -= 1

    # if there's both a pit and wumpus near -- danger will robinson go back, this is probably death
    if breeze is True and stench is True:
        nextmove = invertMove(moveHistory[-1])

    # if there's only a breeze and no wumpus, we can update the dictionary to show that there's not wumpi
    # in those squares
    if breeze is True and stench is False:
        # if the space is already in the dictionary -- update it
        if (playerx + 1, playery) in knownInfo:
            already_stored = knownInfo.get((playerx + 1, playery))
            already_stored[0] = True
            new_info = {(playerx + 1, playery): already_stored}
            knownInfo.update(new_info)
        else:
            knownInfo[(playerx + 1, playery)] = [True, False]

        if (playerx, playery + 1) in knownInfo:
            already_stored = knownInfo.get((playerx, playery + 1))
            already_stored[0] = True
            new_info = {(playerx, playery + 1): already_stored}
            knownInfo.update(new_info)
        else:
            knownInfo[(playerx, playery + 1)] = [True, False]

        if (playerx - 1, playery) in knownInfo:
            already_stored = knownInfo.get((playerx - 1, playery))
            already_stored[0] = True
            new_info = {(playerx - 1, playery): already_stored}
            knownInfo.update(new_info)
        else:
            knownInfo[(playerx - 1, playery)] = [True, False]

        if (playerx, playery - 1) in knownInfo:
            already_stored = knownInfo.get((playerx, playery - 1))
            already_stored[0] = True
            new_info = {(playerx, playery - 1): already_stored}
            knownInfo.update(new_info)
        else:
            knownInfo[(playerx, playery - 1)] = [True, False]

    # if there's only a breeze and no wumpus, we can update the dictionary to show that there's not wumpi
    # in those squares
    if breeze is False and stench is True:
        # if the space is already in the dictionary -- update it
        if (playerx + 1, playery) in knownInfo:
            already_stored = knownInfo.get((playerx + 1, playery))
            already_stored[1] = True
            new_info = {(playerx + 1, playery): already_stored}
            knownInfo.update(new_info)
        else:
            knownInfo[(playerx + 1, playery)] = [False, True]

        if (playerx, playery + 1) in knownInfo:
            already_stored = knownInfo.get((playerx, playery + 1))
            already_stored[1] = True
            new_info = {(playerx, playery + 1): already_stored}
            knownInfo.update(new_info)
        else:
            knownInfo[(playerx, playery + 1)] = [False, True]

        if (playerx - 1, playery) in knownInfo:
            already_stored = knownInfo.get((playerx - 1, playery))
            already_stored[1] = True
            new_info = {(playerx - 1, playery): already_stored}
            knownInfo.update(new_info)
        else:
            knownInfo[(playerx - 1, playery)] = [False, True]

        if (playerx, playery - 1) in knownInfo:
            already_stored = knownInfo.get((playerx, playery - 1))
            already_stored[1] = True
            new_info = {(playerx, playery - 1): already_stored}
            knownInfo.update(new_info)
        else:
            knownInfo[(playerx, playery - 1)] = [False, True]

    return nextmove


def checkBump(percept):
    if "U" in percept:
        last_move = moveHistory.pop()
        pastLocations.pop() #remove the last location from this list since past wall
        dealWithWallHit(last_move)


def dealWithWallHit(previousMove):
    global playerx
    global playery
    global minxpos
    global minypos
    global maxxpos
    global maxypos
    global safeUnvisited

    if previousMove == moveleft:
        # set the min x number to define that edge and move playerx back over to right
        # since the driver won't let us move past... don't need to return a 'moveright'
        # just need to move my internal x value back and set the minimum to not bump again
        playerx += 1
        minxpos = playerx
    if previousMove == moveright:
        # set the max x number to define that edge
        playerx -= 1
        maxxpos = playerx
    if previousMove == moveup:
        # set the max y number to define the edge and adjust player y count
        playery -= 1
        maxypos = playery
    if previousMove == movedown:
        playery += 1
        minypos = playery

    print("FOUND Wall")
    print('Max x', maxxpos, ' Max y', maxypos,  'Min x', minxpos, 'Min y', minypos)

    for i in safeUnvisited:
        if i[0] < minxpos or i[0] > maxxpos or i[1] < minypos or i[1] > maxypos:
            safeUnvisited.remove(i)


def invertMove(move):
    if move == moveleft:
        return moveright
    if move == moveright:
        return moveleft
    if move == moveup:
        return movedown
    if move == movedown:
        return moveup

def isValidMove(move):
    potential_x = playerx
    potential_y = playery
    if move == moveright:
        potential_x += 1
    if move == moveleft:
        potential_x -= 1
    if move == moveup:
        potential_y += 1
    if move == movedown:
        potential_y -= 1

    if potential_x not in range(minxpos, maxxpos+1):
        return False
    if potential_y not in range(minypos, maxypos+1):
        return False
    return True
