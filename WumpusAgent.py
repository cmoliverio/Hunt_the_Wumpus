# Hannah Gorel, William Capon, Christian Oliverio, Liam Pratt
# WumpusAgent.py
# Latest Revision: 2/18/2021
# Assignment:Project 1: Hunt the Wumpus
# Description: Intelligent agent designed to retrieve the gold from the cave
# while avoiding pits and the wumpus, kill the wumpus when possible, and then escape alive! Slight acknowledgement
# in order to speed up time by a lot, I truncated lists in searches, however about 1/800 or 1/1000 times
# this list truncation results in a time out, without truncating lists, it was much slower but never timed out

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
num_moves = 0

move_recommendation = ""

# resets all the global variables to the default or parameter settings - also handles
# all possible input errors that the agent class requires.  It defaults them to the
# 1 1 1 settings recommended by the project
def setParams(type, arrows, wumpi):
    # all the global variables we need to reset
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
    global num_moves
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
    num_moves = 0

# updates the internal playerx and playery variables that keep track of the agent's position in the map
# based on the move that is passed.  Then checks the pastLocations list and adds it in if not recently
# visited, and takes the location out of the safeUnvisited
def updatePlayerPosition(move):
    # all the global variables we need/might update
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

    # these lists have been truncated to allow for better speed through games
    # add the place to pastLocations if not already in the last 400
    if [playerx, playery] not in pastLocations[-400:]:
        pastLocations.append([playerx, playery])
    # remove the place from safeUnvisited list
    if [playerx, playery] in safeUnvisited[-400:]:
        safeUnvisited.remove([playerx, playery])

# function that returns the move to the driver function.  First checks to see if the gold has been found, if yes
# then just backtrack and don't worry about further exploration.  If gold hasn't been found, the program
# goes through the different priorities in our semi-random exploration to return the correct move choice. First
# priority is safe unexplored places, then backtracking if there are known unexplored safe spaces, then randomly
# choosing a less dangerous spot, then randomly choosing any spot.
def getMove(percept):
    # all the global variables we need/might update
    global playerx
    global playery
    global moveHistory
    global safeUnvisited
    global move_recommendation
    global num_moves

    num_moves +=1  # increment the number of moves counter to help trigger remove duplicates in long games

    move_recommendation = ''  # reset the move recommendation string

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

    # every 100,000 moves, go through the safeUnvisited list and make sure there's no duplicates/already traveled spots
    # in a long game, this will hopefully prevent long loops of unknowingly re-exploring the same spots over and over
    if num_moves % 100000 == 0:
        safeUnvisited = removeDuplicatesAndAlreadyTravelledLocations()

    checkBump(percept)  # check to see if you're at an edge already... deal w/ this first

    move_recommendation = checkPerceptAndUpdateDict(percept)  # returns instant recommendation of shooting/grabbinggold

    # the checkPerceptAndUpdateDict function only returns a move recommendation in very specific cases, so if it doesn't
    # recommend one, best to see if any of the spaces around you are safe and unexplored, because it's much better
    # to pursue one of those routes than one that is potentially risky

    if len(move_recommendation) <= 0:  # if there is no recommended move, execute semi-random exploration
        if len(safeUnvisited) > 0:  # if there are known safe spots we have yet to explore
            safe_spots = []
            # check if the spots immediately around you are safe and unexplored, add them to list
            for i in safeUnvisited[-400:]:
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
                move = safe_spots[move_index]  # move there
                updatePlayerPosition(move)  # update internal x and y values
                moveHistory.append(move)  # add the move to list of all moves
                return move
            else:
                # check and see if any of the spots around us have been traveled before -- those should be our next
                # preferred move because we KNOW they're not instant death so backtrack until last safeUnexplored spot
                if len(moveHistory) > 0:
                    prev_move = moveHistory.pop()  # save last move and remove it from list
                    move = invertMove(prev_move)  # invert it
                    updatePlayerPosition(move)  # update move count but don't add to moveHistory so no loop :)
                    return move
                else:
                    # if no moves left to reverse -- gotta pick randomly to prevent infinite loops, usually only
                    # getting here in infinite loops, so I'll say to run the checkDuplicates here to make sure we're not
                    # getting in one of those -- could pose a potential problem w time, but only rarely
                    safeUnvisited = removeDuplicatesAndAlreadyTravelledLocations()
                    print("randomly moving in else statement")
                    print("position: ", playerx, playery)
                    print(safeUnvisited)
                    random_move = randomlyMove()
                    updatePlayerPosition(random_move)
                    moveHistory.append(random_move)
                    return random_move
        else:
            # if there's no safe unexplored spots, you want to make a random move to hopefully find one -- no use
            # in backtracking or anything because that wastes time
            print("randomly moving bc no safe moves left")
            random_move = randomlyMove()
            updatePlayerPosition(random_move)
            moveHistory.append(random_move)
            return random_move
    else:
        # if there was a move recommended by the first function, execute it (only shooting/grabbing gold/inverting so no
        # need to update the moveHistory bc doesn't need to be inverted to backtrack)
        updatePlayerPosition(move_recommendation)
        return move_recommendation

# function that selects the random movement -
# even in a random movement -- to optimize our chance of LIFE we want to go to squares that have only one possible
# danger over squares with two possible dangers (ignoring the fact that only one B would be reported for two pits
# if that's the case then we die oh well -- we'd rather randomly choose a spot with only a possible pit than with
# a possible pit AND a possible wumpus -- gotta maximize those odds
def randomlyMove():
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
            random_move = chooseRandomMove()
    else:  # if there are moving wumpi, they won't stay in the square we first detected them in, so only one danger
        # we can officially track -- pits so just move randomly
        random_move = chooseRandomMove()

    return random_move

# chooses a literally random move, just 0-3 random integer corresponding to a certain movement
def chooseRandomMove():
    # select random integer 0-3 and execute that move
    rand_index = random.randint(0, 3)
    if rand_index == 0:
        rand_move = movedown
    if rand_index == 1:
        rand_move = moveup
    if rand_index == 2:
        rand_move = moveright
    if rand_index == 3:
        rand_move = moveleft

    if isValidMove(rand_move):  # check to make sure that the move keeps the agent in bounds
        return rand_move
    else:  # if not just choose another random move until you get a valid one
        return chooseRandomMove()

# Goes through the perception string and updates the agent's knowledge of the world around them in order to
# allow smarter decisions to be made.  It will add things to the safeUnvisited list to explore if we learn that
# they're safe.  Additionally, it will make educated attempts to kill the wumpi in both stationary and moving gametypes
# however, it's much better at killing stationary wumpi.
def checkPerceptAndUpdateDict(percept):
    # all the global variables we need/might update
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

    # go through the different percepts and set the boolean values to reflect if they were in percept string
    if "B" in percept:
        breeze = True
        dangerlevel += 1  # increase the dangerlevel by 1
    if "S" in percept:
        stench = True
        dangerlevel += 1  # increase the dangerlevel by 1
    if "G" in percept:
        glitter = True
    if "C" in percept:
        scream = True

    # if in square with gold -- grab it, don't look at anything else!
    if glitter is True:
        print("FOUND GOLD")
        foundgold = True
        return grabgold

    # if scream, we know wumpus is dead and we may decrease our internal wumpus count
    # by 1 -- other than that this doesn't really make a difference because still need to move and find gold
    if scream is True:
        numwumpi -= 1

    # update the dictionary and safeUnexplored with the percept information
    if gametype == 1:
        updateDict(playerx, playery, breeze, stench, dangerlevel)
    else:
        # if the game has moving wumpi, no need to keep track of where they've been so set stench to False in dictionary
        updateDict(playerx, playery, breeze, False, dangerlevel)

    # how to kill wumpi if they are stationary and you smell a stench
    if stench is True and gametype == 1:
        if numarrows > 0 and numwumpi > 0:  # only can do this if have arrows and wumpi to kill
            involvedSpots = [[playerx + 1, playery], [playerx - 1, playery], [playerx, playery + 1], [playerx, playery - 1]]
            maybeWumpi = []
            for i in involvedSpots:
                if isInBounds(i[0], i[1]):
                    point_info = knownInfo.get((i[0], i[1]))
                    if point_info[1] is True:  # if the dictionary has True for wumpi-it might be there so add point
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
                point_info = knownInfo.get((maybeWumpi[0][0], maybeWumpi[0][1]))  # get the dictionary information
                point_info[1] = False  # update the wumpus portion to false (either no wumpus there or killed it)
                if point_info[0] is False and point_info[1] is False: # if that space is now clear add it!
                    safeUnvisited.append([maybeWumpi[0][0], maybeWumpi[0][1]])
                new_info = {(maybeWumpi[0][0], maybeWumpi[0][1]): point_info}
                knownInfo.update(new_info)  # update the dictionary with no wumpus there
                numarrows -= 1  # decrease the number of arrows because we just shot one

    # how to kill a moving wumpus when both stench and breeze are true -- without having a breeze it would be very hard
    # to narrow down where the wumpus might be, so we will be ignoring those cases and hoping we do not encounter the
    # wumpus -- because without having a breeze to narrow down options, it would be a random 1-4 choice every stench
    if stench is True and gametype == 2:
        if breeze is True:
            if numarrows > 0 and numwumpi > 0:  # only want to go through this if actually have arrows to shoot
                involvedSpots = [[playerx + 1, playery], [playerx - 1, playery], [playerx, playery + 1],
                                 [playerx, playery - 1]]
                maybeWumpi = []
                maybePit = []
                for i in involvedSpots:
                    if isInBounds(i[0], i[1]):  # only go through them if they're in bounds
                        point_info = knownInfo.get((i[0], i[1]))
                        if point_info[0] is True:  # if the dictionary has True for pit, add it to maybePit
                            maybePit.append(i)
                        else:  # if the dictionary knows there's not a pit there -- could be a wumpus
                            maybeWumpi.append(i)
                if len(maybePit) == 1:  # then we know the pit is there and can assume that the wumpus is not there
                    lastMove = moveHistory[-1]  # rule out the space we came from and hope it didn't come from there
                    if lastMove == moveup:
                        if [playerx, playery - 1] in maybeWumpi:
                            maybeWumpi.remove([playerx, playery - 1])
                    if lastMove == movedown:
                        if [playerx, playery + 1] in maybeWumpi:
                            maybeWumpi.remove([playerx, playery + 1])
                    if lastMove == moveright:
                        if [playerx - 1, playery] in maybeWumpi:
                            maybeWumpi.remove([playerx - 1, playery])
                    if lastMove == moveleft:
                        if [playerx + 1, playery] in maybeWumpi:
                            maybeWumpi.remove([playerx + 1, playery])

                    random_int = random.randint(0, len(maybeWumpi) - 1)  # pick one of the places left in maybeWumpi
                    shoot_at = maybeWumpi[random_int]
                    # go through and return shooting in whatever direction that space was
                    if shoot_at[0] == playerx:
                        if shoot_at[1] == playery + 1:
                            nextmove = shootup
                        if shoot_at[1] == playery - 1:
                            nextmove = shootdown
                    if shoot_at[1] == playery:
                        if shoot_at[0] == playerx + 1:
                            nextmove = shootright
                        if shoot_at[0] == playerx - 1:
                            nextmove = shootleft
                    print("shooting")
                    numarrows -= 1
        else:  # if there's not a pit, then we really have no idea where the wumpus is... so best move is to just go
            # backwards and try to hope it didn't follow/come from that way
            if len(moveHistory) > 0:
                prev_move = moveHistory.pop()  # save last move and remove it from list
                nextmove = invertMove(prev_move)  # invert it

    return nextmove


# this handles if there was a U in the percept -- called before anything except backtracking when we find the
# gold because theoretically this shouldn't matter then :)
def checkBump(percept):
    if "U" in percept:
        last_move = moveHistory.pop()  # pop the last move off the move history because we don't want to save it
        pastLocations.pop()  # remove the last location from this list since past wall
        dealWithWallHit(last_move)


# this sets the boundaries of the board by setting the maxxpos, maxypos, minxpos, minypos variables to reflect the
# edges of the board when we find them.  It also resets our personal tracking of our x and y coordinates depending on
# what the last move was so we know which edge we found.
def dealWithWallHit(previousMove):
    # global variables we need to modify/use
    global playerx
    global playery
    global minxpos
    global minypos
    global maxxpos
    global maxypos
    global safeUnvisited

    # go through the different options of last moves and set the variables accordingly
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

    # loop through safeUnvisited and make sure to remove all spots with boundaries outside that so we don't
    # try to go there ever!
    for i in safeUnvisited:
        if i[0] < minxpos or i[0] > maxxpos or i[1] < minypos or i[1] > maxypos:
            safeUnvisited.remove(i)


# This takes in a move and returns the inverse move.. helpful for when trying to backtrack out of the
# cave or backtrack to find the last safeUnvisited spots
def invertMove(move):
    if move == moveleft:
        return moveright
    if move == moveright:
        return moveleft
    if move == moveup:
        return movedown
    if move == movedown:
        return moveup


# This takes in an x and a y coordinate and returns a boolean value of whether or not that point is in the bounds
# of the board as far as we know
def isInBounds(x, y):
    if x not in range(minxpos, maxxpos + 1):
        return False
    if y not in range(minypos, maxypos + 1):
        return False
    return True


# This is similar to isInBounds, but instead checks if a move would take us out of bounds or if it would keep us in bounds
# not used much, but helpful
def isValidMove(move):
    potential_x = playerx
    potential_y = playery
    # set the potential x and y to what they would be if the move is taken
    if move == moveright:
        potential_x += 1
    if move == moveleft:
        potential_x -= 1
    if move == moveup:
        potential_y += 1
    if move == movedown:
        potential_y -= 1

    # then check and see if that's in bounds
    if potential_x not in range(minxpos, maxxpos + 1):
        return False
    if potential_y not in range(minypos, maxypos + 1):
        return False
    return True


# This function takes in the x and y coordinates, boolean values of whether or not a stench was percepted at the current
# as well as the danger level, and then updates the knownInfo dictionary of all that we know for things!
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
                if [point_x, point_y] not in safeUnvisited[-400:]:
                    if [point_x, point_y] not in pastLocations[-400:]:
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
                    if [point_x, point_y] not in safeUnvisited[-400:]:
                        if [point_x, point_y] not in pastLocations[-400:]:
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


# This is basically a check to make sure that if the moves are getting high enough, the duplicates are removed
# from the lists and then you can resume going with fast speeds still
def removeDuplicatesAndAlreadyTravelledLocations():
    global safeUnvisited
    global pastLocations

    new_safeUnvisited = []
    # this should remove the duplicates from safeUnvisited and not put any in that are in pastLocations either
    for i in safeUnvisited:
        if i not in new_safeUnvisited and i not in pastLocations:
            new_safeUnvisited.append(i)

    return new_safeUnvisited