import numpy as np
import chess
import time
import chess.pgn

# A Collection of helper functions for various tasks
def square_to_int(square):
    """
    Translates standard chess square notation (e.g. e3,a8,h1...) into an integer
    Top-down left-right from white's perspective
    ------------------
    Inputs:
    square = a square in standard notation 

    --------
    Outputs:
    sqint = an integer representing that square

    """
    #I could do this with unicode or something but it's honestly just easier this way
    #sqint = 0
    #strinds = "abcdefgh"
    #sqint += 8*(8-int(square[1]))
    #sqint += strinds.find(square[0])+1

    #there was an easier way
    #chess.SQUARES = list of square objects, in order
    #chess.SQUARE_NAMES = list of names of squares in chess standard, in order
    #int to get the standard number (from the order), +1 to make it my standard
    sqint = int(chess.SQUARES[chess.SQUARE_NAMES.index(square)])+1
    return sqint

def int_to_square(sqint):
    """
    Inverse of the above
    Inputs:
    sqint = the sqint from above

    ------------
    Outputs:
    square = the square name we put in
    """
    return chess.SQUARE_NAMES[sqint-1]

def translate_board_to_array(board):
    """
    A function to take a chess board and put it into an array of ints
    ---------
    Inputs:
    board = A board from the chess module https://python-chess.readthedocs.io/en/latest/core.html#board

    ---------------
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
    piecestr = "RNBQKPrnbqkp" #ordered by their integer association
    board_walker = 0 #an integer to keep track our position on the board, t-d l-r from white's perspective
    for i in range(len(positions)):
        pos = positions[i]
        if pos.isnumeric(): # if it's an int then it has x blank spaces, so move the walker forward, these stay 0
            board_walker += int(pos)
        else:# this square has a piece, associate it with an integer and move one square over
            board_array[8+board_walker] = piecestr.find(pos)+1
            board_walker += 1
    board_array = board_array.astype(int)
    return board_array

def translate_array_to_board(board_array):
    """
    The inverse function of translate_board_to_array
    --------------
    Inputs:
    board_array = a board array

    --------
    Outputs:
    board = a chess.board
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
    fen_pos_str="" #the position part of the fen string
    piecestr="RNBQKPrnbqkp" #associating ints to strings
    blankcount=0 #counter for number of blank spaces
    for i in range(8,72): #the relevant elements of the array
        if i%8 ==0 and i!=8: # all mod 8 elements except the first are line breaks e.g. row 1 --> row 2, so they get a /
            if blankcount >0: # if there has been a count of blank spaces it's time to write that out and reset the count
                fen_pos_str+= str(blankcount)
                blankcount=0
            fen_pos_str += "/"
        if board_array[i] > 0: #if it's a piece, 
            if blankcount >0: #if there is a blank count, write and reset it
                fen_pos_str+= str(blankcount)
                blankcount=0
            fen_pos_str += piecestr[board_array[i]-1] #write out the piece
        else:
            blankcount += 1 # if it's blank increment the blank count
    fen_pos_str += f" {'wb'[board_array[0]]} " #the value is the appropriate index of this string
    castlestr = " KQkq" #int to str with convenience char
    for i in range(1,5): 
        if bool(board_array[i]): #1 --> castle available
            fen_pos_str+=castlestr[i]
    if fen_pos_str[-1] != " ": #if we've added castle terms, write an extra space; if not we don't want it
        fen_pos_str += " "
    if not bool(board_array[5]): #conditional occurs if this is 0
        fen_pos_str += "- "
    else: #otherwise, use inverse function
        fen_pos_str += str(int_to_square(board_array[5])) + " "
    fen_pos_str += " ".join([str(board_array[6]),str(board_array[7])])
    return chess.Board(fen=fen_pos_str)

class Bots_Board:
    def __init__(self,start_fen=None,training_read=False):
        if start_fen: #if given a starting position, initialize the board with that
            self.board = chess.Board(fen=start_fen)
        else: #else make it the default board
            self.board = chess.Board()
        self.board_array=translate_board_to_array(self.board)
        self.record = np.expand_dims(self.board_array,1)
    
    def evolve_board(self,move,move_type="uci"):
        """
        A helper function to evolve the board without the baggage in chessbattle, for use when constructing decision trees
        -----------------
        Inputs:
        board_array - a board_array
        move - the chosen move in uci

        --------
        Outputs:
        updates self.board and self.board_array with this move
        """
        if move_type == "uci":
            if chess.Move.from_uci(move) in self.board.legal_moves: #best hope it's a legal move or this gets screwy
                self.board.push(chess.Move.from_uci(move)) 
            else:
                return False
            self.board_array = translate_board_to_array(self.board)
            return True
        elif move_type == "std":
            if move in self.board.legal_moves:
                self.board.push(move)
            else:
                return False
        else:
            return False
    
    def read_game_competition(self,game_file,delay=0,print_for_human=False):
        """ 
        for reading a game file of the type Nicholas provided (see chessbattle/stockfish_v_stockfish.txt)
        TODO adapt as well for other file types
        TODO build an array of the board states with associated win/draw/loss value
        TODO include info about time controls as well
        --------------
        Inputs:
        gamefile = a file with the progression of a game in it
        delay = delay in evolving and printing, to make it watchable for a human; int of seconds to delay
        print_for_human = if true, print the board for human use

        -------------
        Outputs:
        evolves self.board
        if print_for_human it shows these evolutions
        """
        with open(game_file,'r') as f:
            game_file_lines = f.readlines()
        for line in game_file_lines:
            if "| move" in line:
                move = line.split(" ")[-1].split(":")[-1].strip()
            else:
                continue
            self.evolve_board(move)
            if print_for_human:
                print(self.board)
                print("\n")
            if delay:
                time.sleep(delay)
            self.record = np.concatenate((self.record, np.expand_dims(self.board_array,1)),axis=1)
        self.evaluate_victory()
    
    def evolve_from_pgn(self,pgndata,print_for_human=False,delay=0):
        """
        Evolves the board over the pgn (takes output of pgn.read_game(), this should be passed elsewhere),
        accordingly storing all of the game states 
        ----------
        Inputs:
        pgndata = an output of pgn.read_game()

        -------------
        Outputs:
        self.board, self.board_array, and self.record are appropriately updated to reflect the development of this game
        """
        for move in pgndata.mainline_moves():
            self.evolve_board(move,move_type="std")
            self.record = np.concatenate((self.record, np.expand_dims(self.board_array,1)),axis=1)
            if print_for_human:
                print(self.board)
                print("\n")
            if delay:
                time.sleep(delay)
        self.evaluate_victory(victory_str=pgndata.headers["Result"])
    
    def evaluate_victory(self,victory_str=None):
        """
        Assigns a victory value
        ------------
        Inputs:
        An evolved self.board OR victory_str, which is the result string from a pgn

        --------------
        Outputs:
        self.victory = 1 if white wins, -1 if black wins, 0 if draw


        """
        if victory_str:
            result_str = victory_str
        else:
            result_str = self.board.result()
        if result_str == "1-0":
            self.victory = 1
        elif result_str == "0-1":
            self.victory = -1
        elif result_str == "1/2-1/2":
            self.victory = 0
        else:
            print("Failed to correctly evaluate victory condition")
            print(result_str)

#class 





    


#Test Cases
"""
print(square_to_int("a8"))
print(square_to_int("h8"))
print(square_to_int("e3"))
print(square_to_int("h3"))
print(square_to_int("a1"))
print(square_to_int("h1"))
"""
#test_board = chess.Board()
#test = translate_board_to_array(test_board)
#print(translate_array_to_board(test))
#test_array = evolve_board(test,"e2e4")
#print(test_array)
#test = translate_array_to_board(test_array)
#print(test)
#print(test.fen)
test = Bots_Board()
test.read_game_competition("stockfish_v_stockfish.txt",print_for_human=False,delay=0)
#print(test.board)
#print(test.victory)
with open("2005-12.bare.[534].pgn","r") as f:
    test_pgn_1 = chess.pgn.read_game(f)
    test_pgn_2 = chess.pgn.read_game(f)
test_pgn_1_board = Bots_Board()
test_pgn_2_board = Bots_Board()
test_pgn_1_board.evolve_from_pgn(test_pgn_1,print_for_human=True,delay=0)
print(test_pgn_1_board.victory)
test_pgn_2_board.evolve_from_pgn(test_pgn_2,print_for_human=True,delay=0)
print(test_pgn_2_board.victory)
