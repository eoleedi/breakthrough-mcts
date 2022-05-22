from abc import abstractmethod, ABC
import math

UCB_PARAM = 3


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
                    math.sqrt(UCB_PARAM * math.log(node.visit)/child.visit)
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
