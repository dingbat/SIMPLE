import random
import time
import math

TURTLES = [1,2,3,4,5,6,7,8,9]

POS_NEST = 8
POS_PLAYER_1 = 0
POS_PLAYER_2 = 9
POS_PLAYER = [POS_PLAYER_1, POS_PLAYER_2]
POS_SCORED = 17

HATCH_WEST = 6
HATCH_EAST = 7

NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3
DESCRIBE_DIR = ["up", "right", "down", "left"]

class TurtlesLogic():
  def __init__(self):
    self.reset()

  def reset():
    self.move_count = 0
    self.current_player = 0
    self.actions = 1
    self.scores = [0, 0]
    # here, negative = opponent turtle, positive = your turtle
    self.board = [
      [], [],
      [], [],
      [], [],
      [], [],
    ]
    self.nests = [
      [[], [], []],
      [[], [], []]
    ]
    # index = turtle number
    # value = position (0-7 is board square, 8-16 is nest, 17 is scored)
    self.turtle_pos = [[-1] * 10, [-1] * 10]

    # randomly assign nest
    p1_nest_order = TURTLES.copy()
    random.shuffle(p1_nest_order)
    for k, v in enumerate(p1_nest_order):
      nest_num = k // 3
      self.nests[0][nest_num].append(v)
      self.nests[1][nest_num].append(v)
      self.turtle_pos[0][v] = POS_NEST + nest_num * 3 + (k % 3)
      self.turtle_pos[1][v] = POS_NEST + nest_num * 3 + (k % 3)

  def invert_state(self):
    self.scores[0], self.scores[1] = self.scores[1], self.scores[0]
    self.nests[0], self.nests[1] = self.nests[1], self.nests[0]
    self.turtle_pos[0], self.turtle_pos[1] = self.turtle_pos[1], self.turtle_pos[0]
    new_board = []
    for idx, space in enumerate(self.board[::-1]):
      new_board.append(list(map(lambda x: -x, space)))
    self.board = new_board
    for idx, space in enumerate(new_board):
      for turtle in space:
        self.turtle_pos[0 if turtle > 0 else 1][abs(turtle)] = idx


  def move_length(self):
    # each turtle can move NESW (E/W is considered hatching for turtles in nest)
    return len(TURTLES) * 4

  def decode_move(self, move_number):
    turtle = (move_number // 4) + 1
    direction = move_number % 4
    return turtle, direction

  def can_hatch_from_nest(self, t, player, nest_idx):
    nest = self.nests[player][nest_idx]
    return len(nest) > 0 and nest[-1] == t

  def can_hatch(self, t, player):
    return (self.can_hatch_from_nest(t, player, 0) or
    self.can_hatch_from_nest(t, player, 1) or
    self.can_hatch_from_nest(t, player, 2))

  def can_move_to_position(self, turtle, to_position):
    occupying_stack = self.board[to_position]
    return self.get_push_index(turtle, occupying_stack) != None

  def move_result(self, turtle, player, direction):
    pos = self.turtle_pos[player][turtle]
    if(pos >= POS_NEST):
      return None

    if direction == EAST:
      if pos == 1 or pos == 3 or pos == 5 or pos == 7:
        return "fall_side"
      else:
        return pos + 1
    if direction == WEST:
      if pos == 0 or pos == 2 or pos == 4 or pos == 6:
        return "fall_side"
      else:
        return pos - 1
    if direction == NORTH:
      if pos == 0 or pos == 1:
        return "fall_top"
      else:
        return pos - 2
    if direction == SOUTH:
      if pos == 6 or pos == 7:
        return "fall_bottom"
      else:
        return pos + 2

  def can_move(self, turtle, direction, allow_fall = True):
    pos = self.move_result(turtle, 0, direction)
    if pos == None:
      return False
    if pos == "fall_top":
      return True
    if pos == "fall_side":
      return allow_fall
    if pos == "fall_bottom":
      return False
    return self.can_move_to_position(turtle, pos)

  def legal_moves(self):
    moves = [0] * self.move_length()
    for k,v in enumerate(moves):
      turtle, direction = self.decode_move(k)
      if(self.can_hatch(turtle, 0)):
        if(direction == WEST and self.can_move_to_position(turtle, HATCH_WEST)):
          moves[k] = 1
        if(direction == EAST and self.can_move_to_position(turtle, HATCH_EAST)):
          moves[k] = 1

      pos = self.turtle_pos[0][turtle]
      if pos < POS_NEST:
        stack = self.board[pos]
        opponent_in_stack = any(x < 0 for x in stack)
        if(self.can_move(turtle, direction, allow_fall = opponent_in_stack)):
          moves[k] = 1

    return moves

  def unstack(self, position, base_turtle, base_turtle_player):
    target = abs(base_turtle) * [1, -1][base_turtle_player]
    stack = self.board[position]
    index = stack.index(target)
    return stack[index:], stack[:index]

  def return_to_nest(self, turtle, player):
    nest = self.nests[player]
    pos = 0
    if len(nest[0]) < 3:
      pos = len(nest[0])
      nest[0].append(turtle)
    elif len(nest[1]) < 3:
      pos = len(nest[1]) + 3
      nest[1].append(turtle)
    elif len(nest[2]) < 3:
      pos = len(nest[2]) + 6
      nest[2].append(turtle)
    self.turtle_pos[player][turtle] = pos + POS_NEST

  def move(self, turtle, player, direction):
    current_pos = self.turtle_pos[player][turtle]
    stack, rem = self.unstack(current_pos, turtle, player)
    to_position = self.move_result(turtle, player, direction)
    self.place(stack, player, direction, to_position)
    self.board[current_pos] = rem

  def get_push_index(self, turtle, occupying_stack):
    if (len(occupying_stack) == 0 or abs(turtle) < abs(occupying_stack[-1])):
      return len(occupying_stack)

    sum = 0
    index = len(occupying_stack) - 1
    for t in occupying_stack[::-1]:
      sum += abs(t)
      if abs(turtle) > sum and (index == 0 or abs(turtle) < abs(occupying_stack[index - 1])):
        return index
      index -= 1

    return None

  def place(self, stack, player, direction, to_position):
    if to_position == None:
      raise Exception("invalid to_position")
    elif to_position == "fall_top":
      for t in stack:
        if t < 0:
          self.return_to_nest(-t, 1)
        else:
          self.scores[0] += 1
          self.turtle_pos[0][t] = POS_SCORED
    elif to_position == "fall_bottom":
      for t in stack:
        if t > 0:
          self.return_to_nest(t, 0)
        else:
          self.scores[1] += 1
          self.turtle_pos[1][-t] = POS_SCORED
    elif to_position == "fall_side":
      for t in stack:
        self.return_to_nest(abs(t), 0 if t > 0 else 1)
    else:
      occupying_stack = self.board[to_position]
      push_index = self.get_push_index(stack[0], occupying_stack)

      if (push_index == None):
        # piece was pushed to a spot it can't move to
        # remove the entire moving stack (pop)
        for t in stack:
          if t < 0:
            self.return_to_nest(-t, 1)
          else:
            self.return_to_nest(t, 0)
      else:
        # push...
        if (push_index < len(occupying_stack)):
          pushed_turtle = occupying_stack[push_index]
          self.move(abs(pushed_turtle), 0 if pushed_turtle > 0 else 1, direction)

        # climb...
        remaining_stack = occupying_stack[:push_index]

        # move
        self.board[to_position] = remaining_stack + stack
        for t in stack:
          self.turtle_pos[0 if t > 0 else 1][abs(t)] = to_position

  def step(self, move_id):
    # for player, nest in enumerate(self.nests):
    #   turts = [0]*9
    #   for row in nest:
    #     for turt in row:
    #       pos = self.turtle_pos[player][turt]
    #       if pos < POS_NEST:
    #         print("------------")
    #         self.print()
    #         raise Exception("turt", player, turt, " in nest has a position of ",pos)
    #       if turts[turt-1] == 1:
    #         print("------------")
    #         self.print()
    #         raise Exception("multple turts in the nest")
    #       turts[turt-1] = 1

    # for i, space in enumerate(self.board):
    #   for t in space:
    #     if self.turtle_pos[0 if t > 0 else 1][abs(t)] != i:
    #       raise Exception("turt_pos and board do not match", t)

    # print()
    # print("==========================")
    # print("==========================")
    # print()
    # self.print()
    # print()
    # print()
    # self.describe_move(move_id)
    # print()
    # print()

    self.move_count += 1
    turtle, direction = self.decode_move(move_id)
    if (self.can_hatch(turtle, 0)):
      nest = self.nests[0]
      if self.can_hatch_from_nest(turtle, 0, 0):
        nest[0].pop()
      if self.can_hatch_from_nest(turtle, 0, 1):
        nest[1].pop()
      if self.can_hatch_from_nest(turtle, 0, 2):
        nest[2].pop()
      self.place([turtle], 0, NORTH, HATCH_EAST if direction == EAST else HATCH_WEST)
    else:
      self.move(turtle, 0, direction)

    # self.print()
    # print()
    # print("==========================")
    # print("==========================")
    # print()

    if self.actions == 2:
      self.actions -= 1
    else:
      self.actions = 2
      self.current_player = (self.current_player + 1) % 2
      self.invert_state()

  def print(self):
    def print_nest(player):
      for row in self.nests[player]:
        print(row, end = "")
        print(" / ", end = "")
      print()
    print("player 1 scored", self.scores[1])
    print_nest(1)
    print()
    for i, space in enumerate(self.board):
      print(space, end = "")
      if i % 2 == 1:
        print()
    print()
    print("player 0 scored", self.scores[0])
    print_nest(0)
    print()

  def describe_move(self, move_id):
    turtle, direction = self.decode_move(move_id)
    if (self.can_hatch(turtle, 0)):
      print(move_id, ": hatch", turtle, "on the", DESCRIBE_DIR[direction])
    else:
      print(move_id, ": move", turtle,  DESCRIBE_DIR[direction])

  def describe_legal_moves(self):
    moves = self.legal_moves()
    for move_id, legal in enumerate(moves):
      if legal == 1:
        self.describe_move(move_id)

  def random_move(self):
    aug = [(i, x, random.random()) for i,x in enumerate(self.legal_moves())]
    moves = list(filter(lambda x: x[1] == 1, aug))
    moves.sort(key = lambda x: x[2])
    return moves[0][0]

# t = TurtleLogic()
# while(t.scores[0] < 7 and t.scores[1] < 7):
#   # t.print()

#   # t.describe_legal_moves()
#   # print(t.random_move())
#   # move = int(input())
#   # t.step(move)

#   move = t.random_move()
#   # t.describe_move(move)
#   t.step(move)
#   # time.sleep(1)

# print("move #", t.move_count)
