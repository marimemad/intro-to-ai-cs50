"""
Tic Tac Toe Player
"""

import math
from copy import deepcopy
from random import randint

X = "X"
O = "O"
EMPTY = None

def Max(v1,v2):
    #print(v1[0], v2)
    try:
        if v1[0]>v2[0]:
            return v1
        return v2
    except:
        if v1[0]>v2[0][0]:
            return v1
        return (v2[0][0], v2[1])



def Min(v1,v2):
    #print(v1[0], v2)
    try:
        if v1[0]<v2[0]:
            return v1
        return v2
    except:
        if v1[0]<v2[0][0]:
            return v1
        return (v2[0][0], v2[1])

def MAX_VALUE(state):
    if terminal(state):
        return utility(state)

    v = -math.inf
    aaction=None
    for action in actions(state):
        v,aaction = Max((v,aaction),(MIN_VALUE(result(state, action)),action))
    return v,aaction

def MIN_VALUE(state):
    if terminal(state):
        return utility(state)

    v = math.inf
    aaction=None
    for action in actions(state):
        v,aaction = Min((v,aaction), (MAX_VALUE(result(state, action)),action))
    return v,aaction


def count(board):
    c={'X':0, 'O':0, None:0}
    for row in board:
        for col in row:
            c[col]+=1
    return c


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    #check if game is over
    if terminal(board):
         return('game is over')

    #count number of X, O, None in board
    c=count(board)
    #check player’s turn
    if c[None]==9:
        return('X')
    elif c['X']>c['O']:
        return('O')
    else:
        return('X')


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    #check if game is over
    if terminal(board):
         return('game is over')

    #check possible actions
    actions=[]
    for row in range(3):
        for col in range(3):
            if board[row][col] == None:
                actions.append((row,col))

    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    copied_board=deepcopy(board)
    play=player(board)
    copied_board[action[0]][action[1]]=play

    return(copied_board)


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for r in range(3):
        row=set()
        col=set()
        for c in range(3):
            row.add(board[r][c])
            col.add(board[c][r])

        row=list(row)
        col=list(col)

        if len(row)==1:
            return(row[0])
        elif len(col)==1:
            return(col[0])

    diagonal1={board[0][2],board[1][1],board[2][0]}
    diagonal2={board[0][0],board[1][1],board[2][2]}

    diagonal1=list(diagonal1)
    diagonal2=list(diagonal2)

    if len(diagonal1)==1:
        return (diagonal1[0])

    if len(diagonal2)==1:
        return (diagonal2[0])


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board):
        return(True)

    for row in range(3):
        for col in range(3):
            if board[row][col] == None:
                return(False)

    return(True)


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if terminal(board):
        score={'X':1,'O':-1, None:0}
        return (score[winner(board)])



def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    play=player(board)
    if play==O:
        return(MIN_VALUE(board)[1])
    if play==X:
        c=count(board)
        if c[None]==9:
            return((randint(0, 2),randint(0, 2)))

        return(MAX_VALUE(board)[1])
