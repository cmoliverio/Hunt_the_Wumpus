
import math
import sys



sys.setrecursionlimit(10**5)
grid = []




actionSequence = []
coords = []
origin = [200,200]
gridSize = 400
haveGold = False
moving = 0
arrows = 0
wumpai = 0
state = ""

maxy = 400
miny = 0
maxx = 400
minx = 0

moveQueue = []
target = []
toVisit = []
lastMove = ""
currentDangerExp = 0
def setParams(gameType,numarrows,numwumpai):
    global coords, moving, arrows, wumpai, haveGold, state
    moving = gameType
    arrows = numarrows
    wumpai = numwumpai
    haveGold = False
    for i in range(0, gridSize + 1):
        grid.append([0] * (gridSize + 1))
    #print(grid)
    coords = [200, 200]
    state = "Exploring"
    for i in range(0,5):
        toVisit.append([])

def getMoveName(sx,sy,ex,ey):
    if ex > sx:
        return "E"
    if ex < sx:
        return "W"
    if ey > sy:
        return "S"
    if ey < sy:
        return "N"
    return "G"


def pathFind(startx,starty,tx,ty,maxDanger, covered = []):
    global grid
    covered.append([startx,starty])
    instructions = []
    if startx == tx and starty == ty:
        return ["G"]
    moves = []
    for xx in range(startx-1,startx+2):
        for yy in range(starty-1,starty+2):
            if xx == startx or yy == starty:
                if(xx in range(minx,maxx)) and (yy in range(miny,maxy)):
                    if [xx,yy] in covered or grid[xx][yy] > maxDanger:
                        continue
                    if len(moves) > 0:
                        if distance(xx,yy,tx,ty) < distance(moves[0][0],moves[0][1],tx,ty):
                            moves.insert(0,[xx,yy])
                        else:
                            moves.append([xx,yy])
                    else:
                        moves.append([xx,yy])
    for m in moves:
        path = pathFind(m[0],m[1],tx,ty,maxDanger,covered)
        if len(path) > 0:
            path.insert(0, getMoveName(startx,starty,m[0],m[1]))
            return path
    return []

def distance(x, y, tx, ty):
    return math.sqrt(((tx-x)**2+(ty-y)**2))


def getMove(percepts):
    print(percepts)
    global haveGold, moveQueue, target, toVisit, lastMove,maxx,minx,maxy,miny, currentDangerExp
    if "G" in percepts:
        haveGold = True
        moveQueue = [] #New target, reroute
        target = origin
        return "G"
    if haveGold and (coords == origin):
        return "C"


    if "U" in percepts:
        print("BUMP!")
        moveQueue = [] #force a reroute
        target = []
        if lastMove == "N":
            miny = coords[1]
            print(miny)
            coords[1] += 1
        if lastMove == "E":
            maxx = coords[0]
            print(maxx)
            coords[0] -= 1
        if lastMove == "S":
            maxy = coords[1]
            print(maxy)
            coords[1] -= 1
        if lastMove == "W":
            minx = coords[0]
            print(minx)
            coords[0] += 1

    grid[coords[0]][coords[1]] = -1
    danger = ("B" in percepts) + ("S" in percepts)
    if danger != 0:
        target = coords
    for sx in range(coords[0] - 1,coords[0] + 2):
        for sy in range(coords[1] - 1,coords[1] + 2):
            if ((sx == coords[0] or sy == coords[1])) and [sx, sy] != coords:
                if sx in range(0,gridSize+1) and sy in range(0,gridSize+1):
                    grid[sx][sy] = danger
                if grid[sx][sy] >= 0 and sx in range(minx,maxx) and sy in range(miny,maxy):
                    toVisit[grid[sx][sy]].insert(0,[sx,sy])
                    #print(grid[sx][sy])
                    #print("Added")



    #print("---")
    while coords == target or len(moveQueue) == 0:
        moveQueue = []

        #print(toVisit[currentDangerExp])
        while len(toVisit[currentDangerExp]) == 0:
            currentDangerExp += 1
        target = toVisit[currentDangerExp].pop(0)

        for i in range(0,5):
            print("Finding a path from x = {0} y = {1} to x = {2} y = {3}".format(coords[0],coords[1],target[0],target[1]))
            newPath = pathFind(coords[0],coords[1],target[0],target[1],i)
            if(len(newPath) > 0):
                moveQueue = newPath
                #print("Found a path")
                break
        if(len(moveQueue) == 0):
            target = coords
    print("Location: x = {0} y = {1}".format(coords[0], coords[1]))
    print("Target: x = {0} y = {1}".format(target[0], target[1]))
    for i in range(coords[1] - 5, coords[1] + 5):
        toPrint = ""
        for a in range(coords[0] - 5, coords[0] + 5):
            if [a, i] == coords:
                toPrint += "P"
            else:
                toPrint += str(grid[a][i])
        print(toPrint)
    move =  moveQueue.pop(0)
    if move == "N":
        coords[1] -= 1
    if move == "E":
        coords[0] += 1
    if move == "S":
        coords[1] += 1
    if move == "W":
        coords[0] -= 1
    lastMove = move
    return move

