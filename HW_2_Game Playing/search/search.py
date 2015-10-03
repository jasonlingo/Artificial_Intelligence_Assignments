# search.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""

import util
import sys


class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return  [s, s, w, s, w, w, s, w]

def depthFirstSearch(problem):
    """
    Search the deepest nodes in the search tree first.

    Your search algorithm needs to return a list of actions that reaches the
    goal. Make sure to implement a graph search algorithm.

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print "Start:", problem.getStartState()
    print "Is the start a goal?", problem.isGoalState(problem.getStartState())
    print "Start's successors:", problem.getSuccessors(problem.getStartState())
    """
    "*** YOUR CODE HERE ***"
    # Search actions
    fringe = util.Stack()
    # visited state
    visited = []
    # Initial action

    curState = problem.getStartState()
    visited.append(curState)
    fringe.push((curState, [], 0))

    while not fringe.isEmpty():
        curState, actions, totalCost = fringe.pop()
        if problem.isGoalState(curState):
            return actions
        successors = problem.getSuccessors(curState)
        for nextState, action, cost in successors:
            if nextState not in visited:
                visited.append(nextState)
                fringe.push((nextState, actions + [action], totalCost + cost))

    print "Error: Cannot find a path using DSF!!"
    return []


def breadthFirstSearch(problem):
    """Search the shallowest nodes in the search tree first."""
    "*** YOUR CODE HERE ***"
    # Search actions
    fringe = util.Queue()
    # visited state
    visited = []
    # Initial action

    curState = problem.getStartState()
    visited.append(curState)
    fringe.push((curState, [], 0))

    while not fringe.isEmpty():
        curState, actions, totalCost = fringe.pop()
        if problem.isGoalState(curState):
            return actions
        successors = problem.getSuccessors(curState)
        for nextState, action, cost in successors:
            if nextState not in visited:
                visited.append(nextState)
                fringe.push((nextState, actions + [action], totalCost + cost))

    print "Error: Cannot find a path using BSF!!"
    return []


def IterativeDeepingSearch(problem):
    """
    Search the graph using depth first search but with different depth
    in each iteration
    """
    # Check current state is the goal state or not.
    if problem.isGoalState(problem.getStartState()):
        return []

    depth = 0 # depth starting from 0
    while not problem.isGoalState(problem.getStartState()):
        actions = DepthLimitedSearch(problem, depth)
        if actions != []:
            return actions
        depth += 1


def DepthLimitedSearch(problem, limit):
    """
    Recursive search the graph.
    Args:
      (int) limit: the depth limit.
    """
    # Search actions
    fringe = util.Stack()
    # visited state
    visited = []
    # Initial action

    curState = problem.getStartState()
    # Push the first not into the stack
    visited.append(curState)
    fringe.push((curState, [], 0))

    while not fringe.isEmpty():
        curState, actions, height = fringe.pop()
        if problem.isGoalState(curState):
            return actions
        if height < limit:      
            successors = problem.getSuccessors(curState)
            for nextState, action, _ in successors:
                if nextState not in visited:
                    visited.append(nextState)
                    fringe.push((nextState, actions + [action], height + 1))

    return []


def uniformCostSearch(problem):
    """Search the node of least total cost first."""
    "*** YOUR CODE HERE ***"
    # Search actions
    fringe = util.PriorityQueue()
    # visited state
    visited = {}

    curState = problem.getStartState()
    # Need to record cost for updating path with lowest actions.
    visited[str(curState)] = 0
    fringe.push((curState, [], 0), 0)

    while not fringe.isEmpty():
        curState, actions, totalCost = fringe.pop()
        if problem.isGoalState(curState):
            return actions
    
        successors = problem.getSuccessors(curState)
        for nextState, action, cost in successors:
            # Get the cost if we reach the successor by the current actions.
            newCost = problem.getCostOfActions(actions + [action])
            if str(nextState) not in visited or visited[str(nextState)] > newCost:
                visited[str(nextState)] = newCost
                fringe.push((nextState, actions + [action], newCost), newCost)

    print "Error: Cannot find a path using uniformCostSearch!!"
    return []

def uniformCostSearchNewCostFunc(problem):
    """Search the node of least total cost first."""
    "*** YOUR CODE HERE ***"
    # Search actions
    fringe = util.PriorityQueue()
    # visited state
    visited = {}

    curState = problem.getStartState()
    # Need to record cost for updating path with lowest actions.
    visited[str(curState)] = 0
    fringe.push((curState, [], 0), 0)
    # The position of ghost and food
    ghost = problem.gameState.getGhostPositions()
    food = problem.gameState.getFood().asList() 
    walls = problem.walls.asList()
    
    # Find lenth and width of this maze.
    maxX = 0
    maxY = 0
    for wall in walls:
        if wall[0] > maxX:
            maxX = wall[0]
        if wall[1] > maxY:
            maxY = wall[1]
    
    while not fringe.isEmpty():
        curState, actions, totalCost = fringe.pop()
        if problem.isGoalState(curState):
            return actions

        successors = problem.getSuccessors(curState)
        for nextState, action, _ in successors:
            cost = newCostFunc(nextState, food, ghost, maxX, maxY)
            # Get the cost if we reach the successor by the current actions.
            newCost = totalCost + cost + 1 # 1 is for going to its successor

            if str(nextState) not in visited or visited[str(nextState)] > newCost:
                visited[str(nextState)] = newCost
                fringe.push((nextState, actions + [action], newCost), newCost)

    print "Error: Cannot find a path using uniformCostSearch!!"
    return []    

def newCostFunc(pos, food, ghost, maxX, maxY):
    """New cost function for UCS algorithm"""
    # Calculate the cost for food (it is also the distance from the current position)
    foodCost = 0
    if len(food) > 0:    
        foodCost = util.manhattanDistance(pos, food[0])
        for f in food:
            dist = util.manhattanDistance(pos, f)
            if dist < foodCost:
                foodCost = dist

    # Calculate the cost for ghost
    ghostCost = 0
    nearestGhostDist = sys.maxint
    if len(ghost) > 0:
        northNearest = 0
        southNearest = 0
        westNearest = 0
        eastNearest = 0
        for g in ghost:
            dist = util.manhattanDistance(pos, g)
            if dist < nearestGhostDist:
                nearestGhostDist = dist

            if g[0] > pos[0]: # The ghost is at the east side of current position
                if maxX + maxY - (g[0] - pos[0]) > eastNearest:
                    eastNearest = maxX + maxY - (g[0] - pos[0])
            elif g[0] < pos[0]: # The ghost is at the west side of current position
                if maxX + maxY - (g[0] - pos[0]) > westNearest:
                    westNearest = maxX + maxY - (pos[0] - g[0])                
            if g[1] >= pos[1]: # The ghost is at the north of side current position
                if maxX + maxY - (g[1] - pos[1]) > northNearest:
                    northNearest = maxX + maxY - (g[1] - pos[1])                
            elif g[1] < pos[1]: # The ghost is at the south side of current position
                if maxX + maxY - (g[1] - pos[1]) > southNearest:
                    southNearest = maxX + maxY - (pos[1] - g[1])                
        
        # Find which side has the nearest ghost. 
        mostGhost = max(northNearest, southNearest, westNearest, eastNearest)
        if northNearest == mostGhost or southNearest == mostGhost: # should go south or north
            ghostCost += pos[1] * northNearest / (southNearest + 1.0) # add 1 in order to prevent it from dividing by zero
        if westNearest == mostGhost or eastNearest == mostGhost: # should go east or west
            ghostCost += pos[0] * eastNearest / (westNearest + 1.0) 

    # Decide the final cost by the nearest distance of ghost and food.
    # If a food is closer than all other ghosts, then return the food cost, else return the ghost cost.       
    finalCost = ghostCost if nearestGhostDist <= foodCost else foodCost
    return finalCost

def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

def aStarSearch(problem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    "*** YOUR CODE HERE ***"
    # Search actions
    fringe = util.PriorityQueue()
    # visited state
    visited = []

    curState = problem.getStartState()
    # Need to record cost for updating path with lowest actions.
    visited.append((curState, 0))
    fringe.push((curState, [], 0), 0)

    while not fringe.isEmpty():
        curState, actions, totalCost = fringe.pop()
        if problem.isGoalState(curState):
            return actions

        successors = problem.getSuccessors(curState)
        for nextState, action, cost in successors:
            # Get the cost if we reach the successor by the current actions.
            newCost = problem.getCostOfActions(actions + [action])
            # Check whether the newsState is visited or has lower cost 
            visitedState = False
            for i in xrange(len(visited)):
                tempState, tempCost = visited[i]
                if tempState == nextState and tempCost <= newCost:
                    visitedState = True
                    break
            # Update actions
            if not visitedState:    
                costToGoal = heuristic(nextState, problem)
                visited.append((nextState, newCost))
                fringe.push((nextState, actions + [action], newCost), newCost + costToGoal)

    print "Error: Cannot find a path using aStarSearch!!"
    return []

    
#====================================================
# Helper classes and functions
#====================================================

# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
ids = IterativeDeepingSearch
ucsnc = uniformCostSearchNewCostFunc