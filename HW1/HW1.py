
# coding: utf-8

# In[20]:

#Description: Loads the traffic graph from file handle into a dictionary 
#Input: Number of continuous lines to in file containing traffic graph information
#Output: Dictionary storing the traffic graph with the following mapping:
#        source state -> [(destination state1, step cost1), (destination state2, step cost2), ...]
def GenerateTrafficGraph(aNumOfLines):
    graph = {}
    while aNumOfLines > 0:
        tmp = f.readline().strip().split()
        src, dest, cost = tmp[0], tmp[1], int(tmp[2])
        if not graph.has_key(src):
            graph[src] = []
        graph[src].append((dest, cost))
        aNumOfLines -= 1
    return graph

#Description: Loads the Sunday traffic estimate from file handle into a list
#Input: Number of continuous lines to in file containing traffic graph information
#Output: Array storing the Sunday traffic estimate with each element in the following format:
#        <source state> <estimated path cost to goal state>
def LoadSundayEstimate(aNumOfLines):
    table = {}
    while aNumOfLines > 0:
        tmp = f.readline().strip().split()
        src, cost = tmp[0], int(tmp[1])
        table[src] = cost
        aNumOfLines -= 1
    return table

#Description: Insert a list of nodes into a queue, based on DFS exploration pattern
#Input: List of nodes to be inserted and queue to contain these nodes
#Output: New queue with the nodes inserted
def DFS_InsertNodes(aNewNodes, aQueue):
    lastInsertionIdx = 0
    
    for node in aNewNodes:
        aQueue.insert(lastInsertionIdx, node)
        lastInsertionIdx += 1

#Description: Insert a list of nodes into a queue, based on BFS exploration pattern
#Input: List of nodes to be inserted and queue to contain these nodes
#Output: New queue with the nodes inserted
def BFS_InsertNodes(aNewNodes, aQueue):
    for node in aNewNodes:
        aQueue.append(node)

#Description: Insert a list of nodes into a queue, based on UCS exploration pattern
#Input: List of nodes to be inserted and queue to contain these nodes
#Output: New queue with the nodes inserted
def UCS_InsertNodes(aNewNodes, aQueue):
    #Find right-most insertion point in aQueue such that aNode's path cost from initial state is larger than everything to it's left
    def FindInsertionPoint(aNode):
        l = 0
        r = len(aQueue) - 1
        insertionPoint = -1       
        while l <= r:
            mid = (l + r) / 2           
            if aQueue[mid][3] > aNode[3]:
                insertionPoint = mid
                r = mid - 1  
            else:
                l = mid + 1
        return insertionPoint
    
    #for i in xrange(len(aNewNodes) - 1, -1, -1):
        #node = aNewNodes[i]
    for node in aNewNodes:
        insertPt = FindInsertionPoint(node)
        if insertPt == -1:
            aQueue.append(node)
        else:
            aQueue.insert(insertPt, node)         
    
#Description: Insert a list of nodes into a queue, based on A* exploration pattern
#Input: List of nodes to be inserted and queue to contain these nodes
#Output: New queue with the nodes inserted
def AStar_InsertNodes(aNewNodes, aQueue, aHeuristic):
    #Find right-most insertion point in aQueue such that aNode's (path cost from initial state + heuristic cost) is larger than everything to it's left
    def FindInsertionPoint(aNode):
        l = 0
        r = len(aQueue) - 1
        insertionPoint = -1      
        while l <= r:
            mid = (l + r) / 2    
            if (aQueue[mid][3] + aHeuristic[aQueue[mid][1]]) > (aNode[3] + aHeuristic[aNode[1]]):
                insertionPoint = mid
                r = mid - 1  
            else:
                l = mid + 1              
        return insertionPoint
    
    for node in aNewNodes:
        insertPt = FindInsertionPoint(node)
        if insertPt == -1:
            aQueue.append(node)
        else:
            aQueue.insert(insertPt, node)

#Description: Conducts a tree search and returns the search tree
#Input: Traffic graph, start state, goal state and algorithm to be used
#Output: Data structure representing the search tree, 
#       it will be a dictionary that maps a state to it's predecessor in the search path, with the following mapping:
#       destination state -> (source state, depth, path cost)
def TreeSearch(aGraph, aHeuristic, aStart, aGoal, aAlgo):
    #Queue consists of nodes of following tuple structure: 
    #(parent state, current state, depth, path cost)
    q = [(None, aStart, 0, 0)]
    
    searchTree = {}
    
    while len(q) > 0:
        #dequeue
        currNode = q.pop(0)
        
        #if not in searchTree
        if not searchTree.has_key(currNode[1]):   
            searchTree[currNode[1]] = (currNode[0], currNode[2], currNode[3])
                
            #return if currNode's state is goal state
            if currNode[1] == aGoal:
                return searchTree
                
            expandedNodes = []
            
            if aGraph.has_key(currNode[1]):
                for child in aGraph[currNode[1]]:                         
                    expandedNodes.append((currNode[1], child[0], currNode[2] + 1, currNode[3] + child[1]))
                    
            if aAlgo == 'BFS':
                BFS_InsertNodes(expandedNodes, q)
            elif aAlgo == 'DFS':
                DFS_InsertNodes(expandedNodes, q)
            elif aAlgo == 'UCS':
                UCS_InsertNodes(expandedNodes, q)
            elif aAlgo == 'A*':
                AStar_InsertNodes(expandedNodes, q, aHeuristic)
            
        #print currNode, q
    return searchTree

# def DFS2(aTraffic, aStart, aGoal):
#     q = [(None, aStart, 0, 0)]
#     visited = {}
#     searchTree = []
    
#     while len(q) > 0:
#         #dequeue
#         currNode = q.pop(0)
        
#         while len(searchTree) > 0 and searchTree[-1][0] != currNode[0]:
#             searchTree.pop()
            
#         searchTree.append((currNode[1], currNode[2], currNode[3]))
#         visited[currNode[1]] = True        
        
#         #return if currNode's state is goal state
#         if currNode[1] == aGoal:
#             return searchTree
        
#         if aTraffic.has_key(currNode[1]):
#             lastInsertIdx = 0

#             for child in aTraffic[currNode[1]]:
#                 #if not in visited set
#                 if not visited.has_key(child[0]):
#                     q.insert(lastInsertIdx, (currNode[1], child[0], currNode[2] + 1, currNode[3] + child[1]))
#                     lastInsertIdx += 1

# def BFS(aTraffic, aStart, aGoal):
#     q = [(None, aStart, 0)]
#     visited = {}
    
#     while len(q) > 0:
#         #dequeue
#         currNode = q.pop(0)
#         visited[currNode[1]] = (currNode[0], currNode[2])
        
#         #return if currNode's state is goal state
#         if currNode[1] == aGoal:
#             return visited

#         for child in aTraffic[currNode[1]]:
#             #if not in visited set
#             if not visited.has_key(child[0]):
#                 flag = False
#                 for i in xrange(len(q)):
#                     if q[i][1] == child[0]:
#                         flag = True
#                         break
#                 #if not in frontier
#                 if not flag:    
#                     q.append((currNode[1], child[0], currNode[2] + 1))

#Description: Extracts a solution from a search tree, solution will be in the form of a string.
#Input: Search tee, goal state and algorithm (BFS and DFS will trigger printing of depth while UCS and A* will trigger printing of path cost)
#Output: A string representing the solution, with the following format:
#             <Start state>, 0
#             <intermediate state1>, <path cost from start state to intermediate state1 | depth from start state to intermediate state1>
#             <intermediate state2>, <path cost from start state to intermediate state1 | depth from start state to intermediate state1>
#             <intermediate state3>, <path cost from start state to intermediate state1 | depth from start state to intermediate state1>
#             <end state>, <path cost from start state to end state | depth from start state to intermediate state1>
def ExtractSoln(aSearchTree, aGoal, aAlgo):
    output = ''
    
    #If goal is reachable
    if aSearchTree.has_key(aGoal):
        while aSearchTree[aGoal][0] != None:
            output = aGoal + ' ' + str(aSearchTree[aGoal][1 if aAlgo == 'BFS' or aAlgo == 'DFS' else 2]) + '\n' + output
            aGoal = aSearchTree[aGoal][0]
        output = (aGoal + ' ' + str(aSearchTree[aGoal][1]) + '\n' + output).strip()
         
    return output

f = open('NewTree.txt', 'r')
algo = f.readline().strip()
initState = f.readline().strip()
goalState = f.readline().strip()
trafficGraph = GenerateTrafficGraph(int(f.readline()))
sundayEstimate = LoadSundayEstimate(int(f.readline()))
f.close()
#print trafficGraph
#print DFS2(trafficGraph, initState, goalState)
visited = TreeSearch(trafficGraph, sundayEstimate, initState, goalState, algo)
sol = ExtractSoln(visited, goalState, algo)
f = open('NewTreeOutput.txt', 'w')
f.write(sol)
#print sol
#print sundayEstimate
f.close()


# In[ ]:



