import copy
from random import choice
from abc import abstractmethod, ABC
import math
import sys


class MCTS:
    def __init__(self):
        self.children = dict()

    def choose(self, node):
        if node.is_terminal():
            raise RuntimeError("Cannot choose from a terminal node")
        if node not in self.children:

            return node.find_random_child()

        def score(n):
            if n.visit == 0:
                return -math.inf
            return n.reward / n.visit

        return max(self.children[node], key=score)

    def select(self, node):
        path = []
        while(1):
            path.append(node)
            # print(self.children[node])
            if node not in self.children or not self.children[node]:
                return path
            unexplored = self.children[node] - self.children.keys()
            if unexplored:
                return path + [unexplored.pop()]
            node = self.uct_select(node)

    def do_rollout(self, node):
        "Make the tree one layer better. (Train for one iteration.)"
        path = self.select(node)
        leaf = path[-1]
        self.expand(leaf)
        reward = self.simulate(leaf)
        self.backpropagate(path, reward)

    def expand(self, node):
        if node in self.children:
            return
        self.children[node] = node.find_children()

    def simulate(self, node):
        invert_reward = True
        while True:
            # node.pretty_print()
            # print(node.turn)
            if node.is_terminal():
                reward = node.find_reward()
                return 1 - reward if invert_reward else reward
            node = node.find_random_child()
            invert_reward = not invert_reward

    def backpropagate(self, path, reward):
        for node in reversed(path):
            node.visit += 1
            node.reward += reward
            reward = 1 - reward  # for enemy and me

    def uct_select(self, node):
        maxScore = -math.inf
        bestChild = None
        for child in self.children[node]:
            try:
                if child.visit == 0:
                    continue
                ucb1 = child.reward / child.visit + \
                    math.sqrt(2 * math.log(node.visit)/child.visit)
                if ucb1 > maxScore:
                    maxScore = ucb1
                    bestChild = child
            except ZeroDivisionError:
                # TODO: Check the bug
                print(f"node.reward/node.visit: {node.reward}/{node.visit}")
                print(
                    f"child.reward/child.visit: {child.reward}/{child.visit}")
                node.pretty_print()
                child.pretty_print()
                raise ZeroDivisionError

        return bestChild


class Node(ABC):

    @abstractmethod
    def find_children(self):
        return set()

    @abstractmethod
    def find_random_child(self):
        return None

    @abstractmethod
    def is_terminal(self):
        return True

    @abstractmethod
    def find_reward(self):
        return 0

    @abstractmethod
    def __hash__(self):
        return 123456789

    @abstractmethod
    def __eq__(node1, node2):
        return True


# _TTTB = namedtuple("Breakthrough", "terminal board turn winner")


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
            raise RuntimeError(
                f"移動的旗子是不是自己的 Not a legal Move {move_number_to_string(location)}")
            return None
        # 檢查移動後的旗子是不是自己的
        if self.turn == self.board[new_loc]:
            raise RuntimeError(
                f"移動後的旗子是不是自己的Not a legal Move {move_number_to_string(location)}")
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
        raise RuntimeError(
            f"Not a legal Move{move_number_to_string(location)}")
        return None

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


if __name__ == '__main__':
    tree = MCTS()
    board_numeric = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                     0, -1, -1, -1, -1, -1, -1, -1, -1, 0,
                     0, -1, -1, -1, -1, -1, -1, -1, -1, 0,
                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                     0, 1, 1, 1, 1, 1, 1, 1, 1, 0,
                     0, 1, 1, 1, 1, 1, 1, 1, 1, 0,
                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                     ]
    default_node = BreakThrough(
        terminal=False, board=board_numeric, turn=1, winner=None)

    isFirst = True

    while True:
        if isFirst:
            isFirst = False
            opponent_move = input()  # last move played or "None"

            if opponent_move == "None":
                board = BreakThrough(board=board_numeric, turn=1,
                                     winner=None, terminal=False)
            else:
                board = BreakThrough(board=board_numeric, turn=-1,
                                     winner=None, terminal=False)
                board = board.make_move(move_string_to_number(opponent_move))
            for _ in range(107):
                tree.do_rollout(board)

        else:
            for _ in range(9):
                tree.do_rollout(board)

        legal_moves = int(input())  # number of legal moves
        for i in range(legal_moves):
            move_string = input()

        node = tree.choose(board)
        print(f"score: ({node.reward},{node.visit})",
              file=sys.stderr, flush=True)
        # move_number = find_move(board, node)
        move_number = node.parent_movement
        print(move_number_to_string(move_number), "My move")
        board = node

        opponent_move = input()  # last move played or "None"

        move_number = move_string_to_number(opponent_move)
        board = board.make_move(move_number)

        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr, flush=True)
