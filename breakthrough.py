import copy
from mcts import Node
from random import choice


class IllegalMoveError(Exception):
    pass


class BreakThrough(Node):
    def __init__(self, terminal=False, board=None, turn=None, winner=None, parent_movement=None):
        self.visit = 0
        self.reward = 0
        self.board = board  # 8x8 board with 10x10 size
        self.terminal = terminal
        self.winner = winner
        self.turn = turn  # 1 for me, -1 for enemy
        self.parent_movement = parent_movement

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash(''.join(str(e) for e in self.board))

    def find_children(self):

        if self.is_terminal():
            return set()

        return set([self.make_move(location) for location in self.find_possible_moves()])

    def find_random_child(self):
        if self.terminal:
            return None
        move = choice(self.find_possible_moves())
        return self.make_move(move)

    def find_reward(self):
        if not self.terminal:
            raise RuntimeError(
                f"reward called on nonterminal board {self.board}")
        if self.winner is self.turn:
            # It's your turn and you've already won. Should be impossible.
            raise RuntimeError(
                f"reward called on unreachable board {self.board}")
        if self.turn is (self.winner * -1):
            return 0  # Your opponent has just won. Bad.

        # The winner is neither True, False, nor None
        raise RuntimeError(f"board has unknown winner type {self.winner}")

    def make_move(self, location):
        original_loc, new_loc = location
        # 檢查移動的旗子是不是自己的
        if self.turn != self.board[original_loc]:
            raise IllegalMoveError(
                f"移動的旗子不是自己的 Not a legal Move {move_number_to_string(location)}")
            return None
        # 檢查移動後的旗子是不是自己的
        if self.turn == self.board[new_loc]:
            raise IllegalMoveError(
                f"旗子移動後的格子是自己的旗子 Not a legal Move {move_number_to_string(location)}")
            return None

        if ((new_loc - original_loc) * self.turn == -10 and self.board[new_loc] == 0) or \
            ((new_loc - original_loc) * self.turn == -9) or \
                ((new_loc - original_loc) * self.turn == -11):
            board = copy.deepcopy(self.board)
            board[original_loc] = 0
            board[new_loc] = self.turn

            turn = -self.turn
            winner = find_winner(board)
            is_terminal = winner is not None

            return BreakThrough(terminal=is_terminal, board=board, turn=turn, winner=winner, parent_movement=(original_loc, new_loc))
        raise IllegalMoveError(
            f"Not a legal Move {move_number_to_string(location)}")

    def is_terminal(self):
        return self.terminal

    def find_possible_moves(self):
        possible_moves = []
        for i in range(11, 89):
            if self.turn != self.board[i]:
                continue
            if self.is_outbound(i):
                continue

            # forward
            if self.board[i-self.turn * 10] == 0 and self.is_outbound(i - self.turn * 10) and self.turn != self.board[i-self.turn * 10]:
                possible_moves.append((i, i-self.turn * 10))
            # side forward
            if not self.is_outbound(i - self.turn * 9) and self.turn != self.board[i-self.turn * 9]:
                possible_moves.append((i, i-self.turn * 9))
            # side forward
            if not self.is_outbound(i - self.turn * 11) and self.turn != self.board[i-self.turn * 11]:
                possible_moves.append((i, i-self.turn * 11))

        return possible_moves

    def is_outbound(self, loc):
        # loc <= 10 or loc >= 90 這幾個不用檢查因為不會走到
        return loc % 10 == 0 or loc % 10 == 9

    def pretty_print(self):
        for i in range(10):
            for j in range(10):
                print("{0: <3}".format(self.board[i * 10 + j]), end=" ")
            print()


def find_winner(board):
    for i in range(11, 19):
        if board[i] == 1:
            return 1
    for i in range(81, 89):
        if board[i] == -1:
            return -1
    return None


def move_string_to_number(string):
    original_loc = (8 - int(string[1]) + 1) * \
        10 + (ord(string[0]) - ord('a') + 1)
    new_loc = (8 - int(string[3]) + 1) * 10 + (ord(string[2]) - ord('a') + 1)
    return (original_loc, new_loc)


def move_number_to_string(number):
    original_loc, new_loc = number

    return "".join([chr(original_loc % 10 - 1 + ord('a')),
                    str(8 - original_loc // 10 + 1),
                    chr(new_loc % 10 - 1 + ord('a')),
                    str(8 - new_loc // 10 + 1)])


def find_move(old_node, new_node):
    points = [i for i in range(
        0, 100) if old_node.board[i] != new_node.board[i]]

    assert(len(points) == 2)

    for point in points:
        if new_node.board[point] == 0:
            original_loc = point
        else:
            new_loc = point
    return (original_loc, new_loc)
