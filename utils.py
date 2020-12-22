import numpy as np
import chess

# A Collection of helper functions for various tasks
def square_to_int(square):
    """
    Translates standard chess square notation (e.g. e3,a8,h1...) into an integer
    Top-down left-right from white's perspective
    Inputs:
    square = a square in standard notation 

    --------
    Outputs:
    sqint = an integer representing that square

    """
    #I could do this with unicode or something but it's honestly just easier this way
    sqint = 0
    strinds = "abcdefgh"
    sqint += 8*(8-int(square[1]))
    sqint += strinds.find(square[0])+1
    return sqint


def translate_board_to_array(board):
    """
    Inputs:
    board = A board from the chess module https://python-chess.readthedocs.io/en/latest/core.html#board

    Outputs:
    board_array = An 72 element array containing equivalent information, written as integers
    """
    #There are 72 elements of information in FEN notation https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation
    # [0] = 0 or 1, white or black to play respectively
    # [1:5] = 0 or 1, availability of kingside/queenside castle for white/black respectively ---> 1 = available
    # [5] = 0-64, a square that can be targeted by en passant, from a8,b8,...h8,a7,b7...h1 (left-right top-down white perspective)
    # this is 0 if no targetable square exists
    # (in reality a substantial fraction of these never get used, but there's no point in making that reduction in complexity)
    # [6] = half-move timer since last pawn advance or cap, for 50 turn rule, so an int from 0 to 50
    # [7] = The total number of turns elapsed (increments after each black move)
    # [8:] = each square on the board, takes on values 0-12:
    # 0 = empty
    # 1-6 = white pieces: rook, knight, bishop, queen, king, pawn (RNBQKP)
    # 7-12 = black pieces: rook, knight, bishop, queen, king, pawn (rnbqkp)
    board_array = np.zeros((72,))
    #get fen format, mess with it
    fen_format = board.fen()
    fen_format = fen_format.split()
    print(fen_format)
    #two strings in this split have more than 1 element's worth of info, so treat them separately
    positions = fen_format[0]
    positions = positions.split("/")
    positions = "".join(positions)
    castling = fen_format[2]
    #straightforward definition conditionals
    #default values are 0, so we only define changes from that 
    if fen_format[1] == "b":
        board_array[0] = 1
    if "K" in castling:
        board_array[1] = 1
    if "Q" in castling:
        board_array[2] = 1
    if "k" in castling:
        board_array[3] = 1
    if "q" in castling:
        board_array[4] = 1
    if fen_format[3] != "-":
        #if this is "-" no en passant is available, so it stays 0
        #else, we convert the available square into an integer
        board_array[5] = square_to_int(fen_format[3])
    board_array[6] = fen_format[4]
    board_array[7] = fen_format[5]
    piecestr = "RNBQKPrnbqkp"
    board_walker = 0 #an integer to keep track our position on the board, t-d l-r from white's perspective
    for i in range(len(positions)):
        pos = positions[i]
        print(positions)
        print(pos)
        if pos.isnumeric(): # if it's an int then it has x blank spaces, so move the walker forward, these stay 0
            board_walker += int(pos)
        else:
            board_array[8+board_walker] = piecestr.find(pos)+1
            board_walker += 1
        print(board_walker)


    print(board_array)


test_board = chess.Board()
translate_board_to_array(test_board)