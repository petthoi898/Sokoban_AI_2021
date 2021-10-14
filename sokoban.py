# import library
import sys
import numpy as np
import collections
import time
import pygame
from game import game


def getPosOfPlayer(gameState):
    """Get position of Player"""
    return tuple(np.argwhere(gameState == 2)[0])
def getPosOfBox(gameState):
    """Get position of Box"""
    return tuple(tuple(x) for x in (np.argwhere( (gameState == 3) | (gameState == 5) )))
def getPosOfWall(gameState):
    """Get position of Wall"""
    return tuple(tuple(x) for x in (np.argwhere( gameState == 1)))
def getPosOfGoal(gameState):
    """Get position of Goals"""
    return tuple(tuple(x) for x in (np.argwhere( (gameState == 4) | (gameState == 5) )))
def isEndState(posBox):
    """ Check EndState
        return true if posBox == posGoals 
    """
    return sorted(posBox) == sorted(posGoals)

def convertToGameState(layout):
    """Transfer the layout of initial puzzle"""
    layout = [x.replace('\n','') for x in layout] # remove \n
    layout = [','.join(layout[i]) for i in range(len(layout))] # cat
    layout = [x.split(',') for x in layout] 
    maxColsNum = max([len(x) for x in layout]) # if there are no character enough for 1 row auto implement wall
    for num_row in range(len(layout)):
        for num_col in range(len(layout[num_row])):
            if layout[num_row][num_col] == ' ': layout[num_row][num_col] = 0   # free space
            elif layout[num_row][num_col] == '#': layout[num_row][num_col] = 1 # wall
            elif layout[num_row][num_col] == '&': layout[num_row][num_col] = 2 # player
            elif layout[num_row][num_col] == 'B': layout[num_row][num_col] = 3 # box
            elif layout[num_row][num_col] == '.': layout[num_row][num_col] = 4 # goal
            elif layout[num_row][num_col] == 'X': layout[num_row][num_col] = 5 # box on goal
        colsNum = len(layout[num_row])
        if colsNum < maxColsNum:
            layout[num_row].extend([1 for _ in range(maxColsNum-colsNum)])  # implement wall in index doesnt have character
    return np.array(layout) # init a array
"""Read command"""
def readCommand(argv):
    from optparse import OptionParser
    
    parser = OptionParser()
    parser.add_option('-l', '--level', dest='levels',
                      help='level of game to play', default='level1.txt')
    parser.add_option('-m', '--method', dest='agentMethod',
                      help='research method', default='bfs')
    args = dict()
    options, _ = parser.parse_args(argv)
    with open('levels/'+options.levels,"r") as f: 
        layout = f.readlines()
    args['layout'] = layout
    args['method'] = options.agentMethod
    args['level'] = options.levels
    return args

def isValidAction(action, posOfPlayer, posOfBox):
    """Check action of current player is valid or not? 
    """
    xPlayer, yPlayer = posOfPlayer

    if action[-1].isupper(): # push a box
        xAction, yAction = xPlayer + 2 * action[0], yPlayer + 2 * action[1]
    else:
        xAction, yAction = xPlayer + action[0], yPlayer + action[1]
    #print("xA, yA: " +str((xAction, yAction)) )
    if ((xAction, yAction) in posOfBox + posWalls): return False
    return True
    #return (xAction, yAction) not in posOfBox + posWalls # check if there are two box or next box is a wall


def validAction(posOfPlayer, posOfBox):
    """Check action of current player is valid or not? and return all actions valid """

    allActions = [[-1,0,'u','U'], [1,0,'d','D'],[0,-1,'l','L'],[0,1,'r', 'R']]
    xPlayer, yPlayer = posOfPlayer
    legalActions = []
    for action in allActions:
        xAction, yAction = xPlayer + action[0], yPlayer + action[1]
        if (xAction, yAction) in posOfBox: # push a box
            action.pop(2)
        else:
            action.pop(3)
        if isValidAction(action, posOfPlayer, posOfBox):
            legalActions.append(action)
        else: continue
    return tuple(tuple(x) for x in legalActions) # ((-1,0,'u'), (1,0,'D',))

def updateState(action, posOfPlayer, posOfBox):
    xPlayer, yPlayer = posOfPlayer
    #print("previous: " + str(posOfPlayer))
    newPosOfPlayer = [xPlayer + action[0], yPlayer + action[1]]
    posOfBox = [list(x) for x in posOfBox]
    if action[-1].isupper(): # if push a box, box will be change then remove old pos and append new pos, new pos = newposplayer + action
        posOfBox.remove(newPosOfPlayer)
        posOfBox.append([xPlayer + 2*action[0], yPlayer + 2*action[1]])
    posOfBox = tuple(tuple(x) for x in posOfBox)
    newPosOfPlayer = tuple(newPosOfPlayer)
    return newPosOfPlayer, posOfBox # (),()

def isFailed(posBox): 
    """Check if the box in special case to can not solve
    we can show 5 case to terminate of searching:
    case 1:     case 3:         case 5:
        X           BX              BX
        BX          BB             XB
    case 2:     case 4:             BX
        BX          BB
        BX          BB  
        B: box
        X: wall
    when one of 5 case occur return true because it can not be solve
    """
    allPattern = [[0,1,2,3,4,5,6,7,8],          # 0 1 2
                  [2,5,8,1,4,7,0,3,6],          # 3 4 5 
                  [2,1,0,5,4,3,8,7,6],          # 6 7 8
                  [0,3,6,1,4,7,2,5,8],
                  [0,1,2,3,4,5,6,7,8][::-1],
                  [2,5,8,1,4,7,0,3,6][::-1],
                  [2,1,0,5,4,3,8,7,6][::-1],
                  [0,3,6,1,4,7,2,5,8][::-1]]# 4 (center) is the position of box   and 0 1 2 3 5 6 7 8 rotate
    for box in posBox:
        if box not in posGoals:
            board = [(box[0] - 1, box[1] - 1), (box[0] - 1, box[1]), (box[0] - 1, box[1] + 1), 
                    (box[0], box[1] - 1), (box[0], box[1]), (box[0], box[1] + 1), 
                    (box[0] + 1, box[1] - 1), (box[0] + 1, box[1]), (box[0] + 1, box[1] + 1)] # 9 sqare around 
            for pattern in allPattern:
                newBoard = [board[i] for i in pattern]
                if newBoard[1] in posWalls and newBoard[5] in posWalls: return True #case 1
                elif newBoard[1] in posBox and newBoard[2] in posWalls and newBoard[5] in posWalls: return True #case2
                elif newBoard[1] in posBox and newBoard[2] in posWalls and newBoard[5] in posBox: return True #case3
                elif newBoard[1] in posBox and newBoard[2] in posBox and newBoard[5] in posBox: return True#case4
                #case5
                elif newBoard[1] in posBox and newBoard[6] in posBox and newBoard[2] in posWalls and newBoard[3] in posWalls and newBoard[8] in posWalls: return True
    return False

def dfs():
    """Algorithm of DFS"""
    beginBox =  getPosOfBox(gameState)
    beginPlayer = getPosOfPlayer(gameState)
    startState = (beginPlayer, beginBox) # ((2,1), ((4,3), (5,2)))
    front = collections.deque([[startState]])
    actions = [[0]]
    visitedSet = set()
    result = []
    while front:
        node = front.pop() # [...,((2,1), ((4,2), (4,1), (5,3)))]
        nodeToAction = actions.pop()
        if isEndState(node[-1][-1]):
            result.append((','.join(nodeToAction[1:]).replace(',','')))
            break
        if node[-1] not in visitedSet:
            #print(node[-1])
            visitedSet.add(node[-1]) # node[-1] is a tuple of posPlayer, posBoxs
            #print(validAction(node[-1][0], node[-1][-1]))
            for action in validAction(node[-1][0], node[-1][1]):
                newPosOfPlayer, newPosOfBox = updateState(action, node[-1][0], node[-1][1])
                # print(newPosOfPlayer)
                # print(newPosOfBox)
                if isFailed(newPosOfBox): # checking special case
                    continue
                front.append(node + [(newPosOfPlayer, newPosOfBox)])
                actions.append(nodeToAction + [action[-1]])
    return result



# Init Game

def print_game(matrix,screen):
    screen.fill(background)
    x = 0
    y = 0
    for row in matrix:
        for char in row:
            if char == ' ': #floor
                screen.blit(floor,(x,y))
            elif char == '#': #wall
                screen.blit(wall,(x,y))
            elif char == '&': #worker on floor
                screen.blit(worker,(x,y))
            elif char == '.': #dock
                screen.blit(docker,(x,y))
            elif char == 'X': #box on dock
                screen.blit(box_docked,(x,y))
            elif char == 'B': #box
                screen.blit(box,(x,y))
            elif char == '+': #worker on dock
                screen.blit(worker_docked,(x,y))
            x = x + 32
        x = 0
        y = y + 32


def get_key():
  while 1:
    event = pygame.event.poll()
    if event.type == pygame.KEYDOWN:
      return event.key
    else:
      pass

def display_box(screen, message):
  "Print a message in a box in the middle of the screen"
  fontobject = pygame.font.Font(None,18)
  pygame.draw.rect(screen, (0,0,0),
                   ((screen.get_width() / 2) - 100,
                    (screen.get_height() / 2) - 10,
                    200,20), 0)
  pygame.draw.rect(screen, (255,255,255),
                   ((screen.get_width() / 2) - 102,
                    (screen.get_height() / 2) - 12,
                    204,24), 1)
  if len(message) != 0:
    screen.blit(fontobject.render(message, 1, (255,255,255)),
                ((screen.get_width() / 2) - 100, (screen.get_height() / 2) - 10))
  pygame.display.flip()

def display_end(screen):
    message = "Level Completed"
    fontobject = pygame.font.Font(None,18)
    pygame.draw.rect(screen, (0,0,0),
                   ((screen.get_width() / 2) - 100,
                    (screen.get_height() / 2) - 10,
                    200,20), 0)
    pygame.draw.rect(screen, (255,255,255),
                   ((screen.get_width() / 2) - 102,
                    (screen.get_height() / 2) - 12,
                    204,24), 1)
    screen.blit(fontobject.render(message, 1, (255,255,255)),
                ((screen.get_width() / 2) - 100, (screen.get_height() / 2) - 10))
    pygame.display.flip()


def ask(screen, question):
  "ask(screen, question) -> answer"
  pygame.font.init()
  current_string = []
  display_box(screen, question + ": " + "".join(current_string))
  while 1:
    inkey = get_key()
    if inkey == pygame.K_BACKSPACE:
      current_string = current_string[0:-1]
    elif inkey == pygame.K_RETURN:
      break
    elif inkey == pygame.K_MINUS:
      current_string.append("_")
    elif inkey <= 127:
      current_string.append(chr(inkey))
    display_box(screen, question + ": " + "".join(current_string))
  return "".join(current_string)

def start_game():
    start = pygame.display.set_mode((320,240))
    level = int(ask(start,"Select Level"))
    if level > 0:
        return level
    else:
        print ("ERROR: Invalid Level: "+str(level))
        sys.exit(2)




if __name__ == '__main__':
    layout, method, levels = readCommand(sys.argv[1:]).values()
    startTime = time.time()
    gameState = convertToGameState(layout)
    # print(gameState)
    posGoals = getPosOfGoal(gameState)
    posWalls = getPosOfWall(gameState)
    # print(posGoals)
    # print(posWalls)
    result = dfs()
    endTime = time.time()
    print(result)
    print("runtime of %s: %.2f second." %(method, endTime - startTime))

    wall = pygame.image.load('images/wall.png')
    floor = pygame.image.load('images/floor.png')
    box = pygame.image.load('images/box.png')
    box_docked = pygame.image.load('images/box_docked.png')
    worker = pygame.image.load('images/worker.png')
    worker_docked = pygame.image.load('images/worker_dock.png')
    docker = pygame.image.load('images/dock.png')
    background = 255, 226, 191
    pygame.init()

    #level = start_game()
    game = game('levels/' + levels,5)
    size = game.load_size()
    screen = pygame.display.set_mode(size)
    #front = collections.q

    while 1:
        if game.is_completed(): 
            display_end(screen)
            pygame.quit()
            sys.exit()
        print_game(game.get_matrix(),screen)
        for event in result[0]: #pygame.event.get()
            """
            if event.type == pygame.QUIT: sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: game.move(0,-1, True)
                elif event.key == pygame.K_DOWN: game.move(0,1, True)
                elif event.key == pygame.K_LEFT: game.move(-1,0, True)
                elif event.key == pygame.K_RIGHT: game.move(1,0, True)
                elif event.key == pygame.K_q: sys.exit(0)
                elif event.key == pygame.K_d: game.unmove()
            """
            #print(event)
            if event == 'u' or event == 'U': 
                game.move(0, -1, True)
                print_game(game.get_matrix(),screen)
                pygame.display.update()
            elif event == 'd' or event == 'D':
                game.move(0, 1, True)
                print_game(game.get_matrix(),screen)
                pygame.display.update()
            elif event == 'l' or event == 'L': 
                game.move(-1, 0, True)
                print_game(game.get_matrix(),screen)
                pygame.display.update()
            elif event == 'r' or event == 'R': 
                game.move(1, 0, True)
                print_game(game.get_matrix(),screen)
                pygame.display.update()
            pygame.time.delay(100)

