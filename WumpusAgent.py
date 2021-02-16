# Hannah Gorel, William Capon, Christian Oliverio, Liam Pratt
# WumpusAgent.py
# Date: 2/16/2021
# Assignment:Project 1: Hunt the Wumpus
# Description: Agent designed to retrieve the gold from the cave
# while avoiding pits and the wumpus, and then escape alive!
import random
import time

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

# counter to see if in infinite loop
move_recommendation = ""


def setParams(type, arrows, wumpi):
    global gametype
    global numarrows
    global numwumpi
    global knownInfo
    global moveHistory
    global safeUnvisited
    global pastLocations
    global foundgold
    global playerx
    global playery
    global maxxpos
    global maxypos
    global minxpos
    global minypos
    global move_recommendation
    gametype = type
    numarrows = arrows
    numwumpi = wumpi

    # handle input errors!
    if gametype != 1 and gametype != 2:
        # default to one for non-moving wumpi
        gametype = 1
    if numarrows < 0:
        # impossible to have a negative number of arrows - default to one
        numarrows = 1
    if numwumpi not in range(0, 198):
        # cannot have negative number of wumpi, and in the driver there's line that says in range (wumpi+2, 200) so
        # we can deduce that the number of wumpi must be between 0 and 198 in order to make that statement not error
        numwumpi = 1

    knownInfo = {}
    moveHistory = []
    safeUnvisited = []
    pastLocations = []
    foundgold = False
    playerx = 0
    playery = 0
    maxxpos = 999
    minxpos = -999
    maxypos = 999
    minypos = -999
    move_recommendation = ""


def updatePlayerPosition(move):
    global playerx
    global playery
    global pastLocations
    global safeUnvisited

    if move == moveup:
        playery += 1
    if move == movedown:
        playery -= 1
    if move == moveright:
        playerx += 1
    if move == moveleft:
        playerx -= 1

    # add the place to pastLocations if not already in the last 100
    if [playerx, playery] not in pastLocations[-50:]:
        pastLocations.append([playerx, playery])
    # remove the place from safeUnvisited list
    if [playerx, playery] in safeUnvisited:
        safeUnvisited.remove([playerx, playery])


def getMove(percept):
    global playerx
    global playery
    global moveHistory
    global safeUnvisited
    global move_recommendation

    move_recommendation = ''

    # if already found gold, just backtrack -- don't worry about other things because everything in move history
    # is known to be safe to return to -- unless with moving wumpus and there's no way to track them realistically
    # so best bet is just to retrace footsteps :)
    if foundgold is True:
        if len(moveHistory) > 0:
            lastmove = moveHistory.pop()
            if lastmove == grabgold:
                lastmove = moveHistory.pop()
            move = invertMove(lastmove)
            updatePlayerPosition(move)
            return move
        else:
            print("climbing out")
            time.sleep(1)
            return climbout

    # check to see if you're at an edge already... deal w/ this first
    checkBump(percept)

    move_recommendation = checkPerceptAndUpdateDict(percept)

    # the checkPerceptAndUpdateDict function only returns a move recommendation in very specific cases, so if it doesn't
    # recommend one, best to see if any of the spaces around you are safe and unexplored, because it's much better
    # to pursue one of those routes than one that is potentially risky

    if len(move_recommendation) <= 0:
        # no move recommended by percept -- so check the safe unexplored paths and choose one of them
        if len(safeUnvisited) > 0:
            safe_spots = []
            # if the spots immediately around you are available, go there!
            for i in safeUnvisited[-200:]:
                if i[0] == playerx and i[1] == playery - 1 and isInBounds(i[0], i[1]):
                    safe_spots.append(movedown)
                if i[0] == playerx and i[1] == playery + 1 and isInBounds(i[0], i[1]):
                    safe_spots.append(moveup)
                if i[0] == playerx + 1 and i[1] == playery and isInBounds(i[0], i[1]):
                    safe_spots.append(moveright)
                if i[0] == playerx - 1 and i[1] == playery and isInBounds(i[0], i[1]):
                    safe_spots.append(moveleft)

            # first choice would be to move to a safe, unexplored spot because there is a chance of finding gold!
            # if such a space is available
            if len(safe_spots) > 0:
                move_index = random.randint(0, len(safe_spots) - 1)  # choose one of those safe spaces randomly
                move = safe_spots[move_index]
                updatePlayerPosition(move)  # and move there
                moveHistory.append(move)
                return move
            else:
                # check and see if any of the spots around us have been traveled before -- those should be our next
                # preferred move because we KNOW they're not instant death
                # currently deleted the possibleMoves part -- unnecessary but this is where it would go
                # if there is an already traveled space around you, and you have moves to invert
                if len(moveHistory) > 0:
                    # just directly inverting the moves until reaching somewhere with unexplored spots
                    prev_move = moveHistory.pop()
                    move = invertMove(prev_move)
                    updatePlayerPosition(move)
                    return move
                else:
                    # if no moves left to reverse -- gotta pick because no infinite loops and just hope for the best
                    # choose a potentially unsafe move
                    random_move = randomlyMove()
                    updatePlayerPosition(random_move)
                    moveHistory.append(random_move)
                    return random_move
        else:
            # if there's no safe unexplored spots, you want to make a random move to hopefully find one -- no use
            # in backtracking or anything because that wastes time
            random_move = randomlyMove()
            updatePlayerPosition(random_move)
            moveHistory.append(random_move)
            return random_move
    else:
        # the case of len(move_recommendation) > 0:

        # can probably take next line out? because only options are shooting/grabgold which don't need to be in this list
        # moveHistory.append(move_recommendation)

        updatePlayerPosition(move_recommendation)
        return move_recommendation

def randomlyMove():
    # even in a random movement -- to optimize our chance of LIFE we want to go to squares that have only one possible
    # danger over squares with two possible dangers (ignoring the fact that only one B would be reported for two pits
    # if that's the case then we die oh well -- we'd rather randomly choose a spot with only a possible pit than with
    # a possible pit AND a possible wumpus -- gotta maximize those odds
    random_move = ''  # variable that will be assigned with the final random move

    # if stationary wumpi - want to prioritize spots with only one danger as opposed to two, if there's moving
    # wumpi this doesn't matter because we have no idea where the wumpi are so all squares are essentially same danger
    if gametype == 1:
        # list of all spots immediately around you -- aka your moving options
        oneDanger = []
        involvedSpots = [[playerx + 1, playery], [playerx - 1, playery], [playerx, playery + 1], [playerx, playery - 1]]
        for i in involvedSpots:
            if isInBounds(i[0], i[1]): # only want to consider spots that are in bounds
                pointInfo = knownInfo.get((i[0], i[1]))
                if pointInfo[2] == 1:
                    oneDanger.append([i[0], i[1]])  # it's listed as a dangerValue one -- add to that array

        if len(oneDanger) > 0:
            print("choosing less dangerous spot")
            choice_index = random.randint(0, len(oneDanger)-1)
            choice_spot = oneDanger[choice_index]
            if choice_spot[0] == playerx and choice_spot[1] == playery - 1:
                random_move = movedown
            if choice_spot[0] == playerx and choice_spot[1] == playery + 1:
                random_move = moveup
            if choice_spot[0] == playerx + 1 and choice_spot[1] == playery:
                random_move = moveright
            if choice_spot[0] == playerx - 1 and choice_spot[1] == playery:
                random_move = moveleft
        else:
            print("literally randomly choosing")
            random_move = chooseRandomMove()
    else:
        random_move = chooseRandomMove()

    return random_move

def chooseRandomMove():
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
        return chooseRandomMove()


def checkPerceptAndUpdateDict(percept):
    global foundgold
    global playerx
    global playery
    global knownInfo
    global safeUnvisited
    global numarrows
    global numwumpi
    breeze = False
    stench = False
    glitter = False
    scream = False
    dangerlevel = 0
    nextmove = ""

    if "B" in percept:
        # increase the dangerlevel by 1
        breeze = True
        dangerlevel += 1
    if "S" in percept:
        stench = True
        dangerlevel += 1
    if "G" in percept:
        glitter = True
    if "C" in percept:
        scream = True

    # now all boolean values accurately reflect whether or not the percept was involved
    # much easier to see what's happening now

    # if in square with gold -- grab it, don't look at anything else!
    if glitter is True:
        print("FOUND GOLD")
        foundgold = True
        return grabgold

    # if scream, we know wumpus is dead and we may decrease our internal wumpus count
    # by 1 -- other than that this doesn't really make a difference because still need to move and find gold
    if scream is True:
        print("killed wumpi")
        numwumpi -= 1  # we don't really do much with this :/

    # update the dictionary and safeUnexplored with the percept information
    updateDict(playerx, playery, breeze, stench, dangerlevel)

    if stench is True and gametype == 1:
        if numarrows > 0:  # only can do this if have arrows
            involvedSpots = [[playerx + 1, playery], [playerx - 1, playery], [playerx, playery + 1], [playerx, playery - 1]]
            maybeWumpi = []
            for i in involvedSpots:
                if isInBounds(i[0], i[1]):
                    point_info = knownInfo.get((i[0], i[1]))
                    if point_info[1] is True:  # if the dictionary has True in place for wumpi - it might be there so add point
                        maybeWumpi.append(i)
            if len(maybeWumpi) == 1:  # if only one possible spot, shoot an arrow that direction
                if maybeWumpi[0][0] == playerx + 1:
                    nextmove = shootright
                if maybeWumpi[0][0] == playerx - 1:
                    nextmove = shootleft
                if maybeWumpi[0][1] == playery + 1:
                    nextmove = shootup
                if maybeWumpi[0][1] == playery - 1:
                    nextmove = shootdown
                numarrows -= 1  # decrease the number of arrows because we just shot one

    return nextmove


def checkBump(percept):
    if "U" in percept:
        last_move = moveHistory.pop()
        pastLocations.pop()  # remove the last location from this list since past wall
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
    print('Max x', maxxpos, ' Max y', maxypos, 'Min x', minxpos, 'Min y', minypos)

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


def isInBounds(x, y):
    if x not in range(minxpos, maxxpos + 1):
        return False
    if y not in range(minypos, maxypos):
        return False
    return True


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

    if potential_x not in range(minxpos, maxxpos + 1):
        return False
    if potential_y not in range(minypos, maxypos + 1):
        return False
    return True

# add function on trying to kill wumpi!!!!! (maybe if gametype == 1 then if thing has stench, check the squares around
# to see if all but 1 of them already has False marked for stench in the dictionary -- then we know where it is and can
# shoot an arrow in that direction!  Not sure how to do it for moving wumpi version because they could be adjacent
# without us knowing :/ -- add this in the checkPerceptAndUpdateDict method first because then it can recommend shooting
# as a move -- and


def updateDict(x, y, breeze, stench, dangerlevel):
    # add somewhere in here if gametype == 1 then do the things involving the wumpi, but if game ==2 -- not worth
    # saving the different values of things because they're gonna move
    global safeUnvisited
    global pastLocations
    global knownInfo
    # call this function to update/add things to the dictionary of knownInformation everytime
    # you receive a percept

    # this should be the general style of dictionary --  [x,y] : [boolBreeze, boolStench, dangerValue]
    involvedSpots = [[x + 1, y], [x - 1, y], [x, y + 1], [x, y - 1]]
    for point in involvedSpots:
        point_x = point[0]
        point_y = point[1]
        # first check and see if the spot is even in bounds -- if not ignore it :)
        if isInBounds(point_x, point_y):
            # if the danger level is 0, we want to add it to safeUnvisited if applicable
            if dangerlevel == 0:
                if [point_x, point_y] not in safeUnvisited:
                    if [point_x, point_y] not in pastLocations:
                        safeUnvisited.append([point_x, point_y])

            # add the points to the dictionary regardless of values
            if (point_x, point_y) in knownInfo:  # if it's already in the dictionary - update the information
                already_stored = knownInfo.get((point_x, point_y))
                # if it's marked to false, then don't change it because we definitively know that the pit/wumpus is
                # not there -- some other percept has shown that it can't be there
                # if they're marked to True, change those if need be, because percepts are only possibilities
                if already_stored[0] is True:
                    already_stored[0] = breeze
                if already_stored[1] is True:
                    already_stored[1] = stench
                # now calculate the dangerValue of this square -- 0 if both false, 1 if one true, 2 if two true
                if (already_stored[0] is True and already_stored[1] is False) or (already_stored[0] is False and already_stored[1] is True):
                    already_stored[2] = 1
                if already_stored[0] is True and already_stored[1] is True:
                    already_stored[2] = 2
                if already_stored[0] is False and already_stored[1] is False:
                    already_stored[2] = 0
                    # this means that we have ruled out the possibility of it being a pit or a wumpis
                    # check and see if it's in the safeUnvisited -- if not, add it bc now know its safe!
                    if [point_x, point_y] not in safeUnvisited:
                        if [point_x, point_y] not in pastLocations:
                            safeUnvisited.append([point_x, point_y])
                new_info = {(point_x, point_y): already_stored}

                # now after all updates have been made to the already_stored array, officially update dictionary
                knownInfo.update(new_info)
            else:
                # if there's no record of this point, add one!
                dangerValue = 0
                if breeze is True:
                    dangerValue += 1
                if stench is True:
                    dangerValue += 1
                knownInfo[(point_x, point_y)] = [breeze, stench, dangerValue]
