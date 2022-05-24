from mcts import MCTS
from breakthrough import BreakThrough, move_string_to_number, move_number_to_string, IllegalMoveError
import sys

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
            for _ in range(500):
                tree.do_rollout(board)

        else:
            for _ in range(100):
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
