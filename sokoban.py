# import library
import sys
import numpy as np
import collections
import time
import pygame
from game import game


robot=[]
walls=[]#tuong
storage=[]#kho
box=[]#hop
directions={}
directions['U']=[0,-1]#len
directions['R']=[1,0]#phai
directions['L']=[-1,0]#trai
directions['D']=[0,1]#xuong


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
    args['layout'] = layout # using to init gameState
    args['method'] = options.agentMethod #using for method to run
    args['level'] = options.levels # using for init game
    return args # 

def isValidAction(action, posOfPlayer, posOfBox):
    """Check action of current player is valid or not? 
    """
    xPlayer, yPlayer = posOfPlayer

    if action[-1].isupper(): # push a box
        xAction, yAction = xPlayer + 2 * action[0], yPlayer + 2 * action[1] # when push a box, it have to check the next of next action is a wall( or box ) or not ?
    else:
        xAction, yAction = xPlayer + action[0], yPlayer + action[1] # when player dosent push a box, just check the next of action is ?
    #print("xA, yA: " +str((xAction, yAction)) )

    return (xAction, yAction) not in posOfBox + posWalls # return position of next action not in (posBox + posWalls)


def validAction(posOfPlayer, posOfBox): 
    """Check action of current player is valid or not? and return all actions valid """

    allActions = [[-1,0,'u','U'], [1,0,'d','D'],[0,-1,'l','L'],[0,1,'r', 'R']] # all actions can be run
    xPlayer, yPlayer = posOfPlayer
    legalActions = []
    for action in allActions:
        xAction, yAction = xPlayer + action[0], yPlayer + action[1] #  position of player after action
        if (xAction, yAction) in posOfBox: # push a box
            action.pop(2) # drop lowwer letter
        else:
            action.pop(3) # drop upper letter
        if isValidAction(action, posOfPlayer, posOfBox):
            legalActions.append(action)
        else: continue
    return tuple(tuple(x) for x in legalActions) # ((-1,0,'u'), (1,0,'D',))

def updateState(action, posOfPlayer, posOfBox):
    """this function update state of player after run action"""
    xPlayer, yPlayer = posOfPlayer # previous position of player
    #print("previous: " + str(posOfPlayer))
    newPosOfPlayer = [xPlayer + action[0], yPlayer + action[1]] # new position of player
    posOfBox = [list(x) for x in posOfBox]
    if action[-1].isupper(): # if push a box, box will be change then remove old pos and append new pos, new pos = newposplayer + action
        posOfBox.remove(newPosOfPlayer) # remove old pos of box
        posOfBox.append([xPlayer + 2*action[0], yPlayer + 2*action[1]]) # add new pos of Box
    posOfBox = tuple(tuple(x) for x in posOfBox) # overloading to tuple to "dong bo"
    newPosOfPlayer = tuple(newPosOfPlayer) # tra ve tuple de dong bo
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
    front = collections.deque([[startState]]) # queue
    actions = [[0]]
    visitedSet = set()
    result = []
    maxSize = sys.getsizeof([startState]) # to find maxSize
    while front:
        node = front.pop() # [...,((2,1), ((4,2), (4,1), (5,3)))]
        nodeToAction = actions.pop() # get action
        if isEndState(node[-1][-1]):  # if return true it is completed and break 
            result.append((','.join(nodeToAction[1:]).replace(',','')))
            break
        if node[-1] not in visitedSet: # node[-1] current position of box, if this state is not in visitedSet add them to visitedSet
            visitedSet.add(node[-1]) # node[-1] is a tuple of posPlayer, posBoxs
            #print(validAction(node[-1][0], node[-1][-1]))
            for action in validAction(node[-1][0], node[-1][1]):
                newPosOfPlayer, newPosOfBox = updateState(action, node[-1][0], node[-1][1])
                # print(newPosOfPlayer)
                # print(newPosOfBox)
                if isFailed(newPosOfBox): # checking special case
                    continue
                front.append(node + [(newPosOfPlayer, newPosOfBox)]) # append new state
                maxSize = max(sys.getsizeof(node + [(newPosOfPlayer, newPosOfBox)]), maxSize)
                actions.append(nodeToAction + [action[-1]])  #add actions
    return (result, maxSize)





# Hàm khoảng cách giữa box và storage
def heuristic(box_ls,storage_ls):
	distance=[]#lưu khoảng cách giữa box và storage
	for h in box_ls:
		dis_temp=[]
		for s in storage_ls:
			a=sum(abs(np.subtract(h,s)))#
			dis_temp.append(a)
		distance.append(min(dis_temp))
	dis_value=sum(distance)
	return dis_value
#Hàm đọc file test
def print_char(filename):
	f = open(filename, 'r')
	i=0
	j=0
	while True:
		char=f.read(1)
		temp=[]
		if char: 
			temp.append(i)
			temp.append(j)
			if char == "#":
				walls.append(temp)
			if char == "&":
				robot.append(temp)
			if char == ".":
				storage.append(temp)
			if char == "B":
				box.append(temp)
			if char == "X":
				box.append(temp)
				storage.append(temp)
			if char == "$":
				robot.append(temp)
				storage.append(temp)
			if char == "\n":
				i=0
				j=j+1
			else:
				i=i+1
		else:
			break


#Hàm thuc hiên di chuyển các box

def move(point,dir,path,temp_box_list,sizeo):
	box_list=[]
	box_list=temp_box_list[:]
	temp_append=[]
	cur_path=[]
	cur_path=path[:]
	cur_path.append(dir)
	if point not in walls:
		if point in box_list:
			ind=box_list.index(point)
			temp_box=[x + y for x, y in zip(point, directions[dir])]
			if temp_box not in box_list and temp_box not in walls:
				box_list[ind]=[x + y for x, y in zip(point, directions[dir])]
				temp_append.append(point)
				for i in box_list:
					temp_append.append(i)
				if temp_append not in visited:
					counter=0
					popped_robot=temp_append[0]
					for k in visited:
						k_temp_visited=k[:]
						
						k_robot=k_temp_visited.pop(0)
						temporary=[]
						if k_robot==popped_robot:
							count_list=0
							temporary=temp_append[1:]
							for m in k_temp_visited:
								if m in temporary:
									count_list=count_list+1
							if count_list==len(temporary):
								counter=counter+1
					if counter==0:
						
						temp_append.append(cur_path)
						dis_append=heuristic(box_list,storage)
						temp_append.append(dis_append)
						queue.append(temp_append)
				if set(map(tuple,box_list))==set(map(tuple,storage)):
					#stop = timeit.default_timer()
					#total_time=stop-start_time
					# print("Ket qua: ")
					# #print(cur_path)
					# print("Tong thoi gian thuc hien: ")
					# print(total_time)
					# print("Tong so buoc :")
					# print(len(cur_path))
					# print("Maxsize =",sizeo,"byte")
					return [cur_path, sizeo]
		else:
			temp_append.append(point)
			for i in box_list:
				temp_append.append(i)
			if temp_append not in visited:
				counter=0
				popped_robot=temp_append[0]
				for k in visited:
					k_temp_visited=k[:]
					count_list=0
					k_robot=k_temp_visited.pop(0)
					temporary=[]
					if k_robot==popped_robot:
						temporary=temp_append[1:]
						for m in k_temp_visited:
							if m in temporary:
								count_list=count_list+1
						if count_list==len(temporary):
							counter=counter+1
				if counter==0:
					dis_append=heuristic(box_list,storage)
					temp_append.append(cur_path)
					temp_append.append(dis_append)
					
					queue.append(temp_append)
			if set(map(tuple,box_list))==set(map(tuple,storage)):
				# stop = timeit.default_timer()
				# total_time=stop-start_time
				# print("Ket qua: ")
				# print(cur_path)
				# print("none")
				# print("Tong thoi gian thuc hien: ")
				# print(total_time)
				# print("Tong so buoc :")
				# print(len(cur_path))
				# print("Maxsize =",sizeo,"byte")
				return [cur_path, sizeo]
	return []

#Hàm hiện thực giải thuât greedy
def greedy():
	maxsize=0
	temp_queue=[]
	initial=robot[0]
	temp_queue.append(initial)
	
	for i in box:#chua list toa do box
		temp_queue.append(i)
	path=[]
	temp_queue.append(path)
	temp_queue.append(0)
	
	queue.append(temp_queue)
	count=0
	while queue:
		temp_box_list=[]
		visited_adding=[]
		queue.sort(key=lambda x: x[-1])
		robot_position_list=queue.pop(0)
		
		robot_position=robot_position_list[0]
		visited_adding=robot_position_list[:-2]
		if visited_adding not in visited:
			visited.append(visited_adding)
		temp_path=robot_position_list[-2][:]
		temp_box_list=robot_position_list[1:-2]
		N=[x + y for x, y in zip(robot_position, directions['U'])]
		S=[x + y for x, y in zip(robot_position, directions['D'])]
		E=[x + y for x, y in zip(robot_position, directions['R'])]
		W=[x + y for x, y in zip(robot_position, directions['L'])]
		maxsize = max(sys.getsizeof(queue),maxsize)
		m1 = move(N,dir_N,temp_path,temp_box_list,maxsize)
		if len(m1) != 0:
			return m1
		m2 = move(S,dir_S,temp_path,temp_box_list,maxsize)
		if len(m2) != 0:
			return m2
		m3 = move(E,dir_E,temp_path,temp_box_list,maxsize)
		if len(m3) != 0:
			return m3
		m4 = move(W,dir_W,temp_path,temp_box_list,maxsize)
		if len(m4) != 0:
			return m4
		count=count+1
		if not queue:
			print("solution not found")
			exit()



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

def catString(res):
    result = ''
    for a in res:
        result+=a
    return result

if __name__ == '__main__':
    layout, method, levels = readCommand(sys.argv[1:]).values()
    startTime = time.time()
    gameState = convertToGameState(layout)
    # print(gameState)
    posGoals = getPosOfGoal(gameState)
    posWalls = getPosOfWall(gameState)
    # print(posGoals)
    # print(posWalls)
    if method == 'dfs':
        result = dfs()
        print(result[0])
    elif method == 'greedy':
        visited=[]
        queue=[]
        print_char('levels/'+levels)
        dir_N='U'
        dir_S='D'
        dir_E='R'
        dir_W='L'
        result = greedy()
        ret = catString(result[0])
        result[0] = [ret]
        print(result[0])
    endTime = time.time()
    print("runtime of %s: %.2f second." %(method, endTime - startTime))
    print("maxSize: %.2f" %(result[1]))
    print("How it work !? Waiting for the game finish")
    # for init game scene
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
        pygame.time.delay(1000)
        for event in result[0][0]: #pygame.event.get()
            
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

