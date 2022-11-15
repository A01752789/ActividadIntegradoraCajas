from math import sqrt
from mesa import Agent, Model, DataCollector
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
import random


# Robot agent
class Robot(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.type = 'robot'
        self.live = 1
        self.next_live = 1
        self.has_box = False
        self.next_state = None

    def get_neighbors_content(self):
        neighbors_content = []
        # Neighbors
        neighbors = self.model.grid.get_neighborhood(
                self.pos,
                moore=False,
                include_center=False)
        # For every neighbor
        for neighbor in neighbors:
            # If neighbor is a pallet
            if neighbor in self.model.pallets:
                neighbors_content.append(['pallet',
                                         self.model.pallets[neighbor],
                                         neighbor])
            # If neighbor is not a pallet
            else:
                # Content of each cell
                content = self.model.grid.get_cell_list_contents(neighbor)

                # Cell is not empty
                if content:
                    # For every element in the cell
                    robot, box = False, False
                    for object in content:
                        # If there is a robot
                        if object.type == 'robot':
                            robot = True
                        # If there is a box
                        elif object.type == 'box':
                            box = True
                    if robot and box:
                        neighbors_content.append(['robot-with-box', neighbor])
                    elif box:
                        neighbors_content.append(['box', neighbor])
                    else:
                        neighbors_content.append(['robot', neighbor])
                # Cell is empty
                else:
                    neighbors_content.append(['empty', neighbor])
        return neighbors_content

    def is_there_a_box(self, neighbors_content):
        for neighbor in neighbors_content:
            if neighbor[0] == 'box' and neighbor[-1] not \
                    in self.model.reserved_boxes:
                self.model.reserved_boxes.append(neighbor[-1])
                return neighbor
        return False

    def move_without_box(self, neighbors_content):
        random.shuffle(neighbors_content)
        for neighbor in neighbors_content:
            if neighbor[0] == 'empty' and neighbor[-1] not in \
                    self.model.reserved_cells:
                self.model.reserved_cells.append(neighbor[-1])
                self.next_state = neighbor[-1]
                return True
        self.next_state = self.pos
        return False

    def closest_pallet(self, neighbor):
        x1, y1 = neighbor[-1]
        min_distance = float('inf')
        closest_pallet = 0
        for key in self.model.pallets:
            if self.model.pallets[key] < 5:
                distance = sqrt(((key[0] - x1)**2) + ((key[1] - y1)**2))
                if distance < min_distance:
                    closest_pallet = [key, neighbor[-1], distance]
                    min_distance = distance
        return closest_pallet

    def move_with_box(self, neighbors_content):
        min_distance = [float('inf')]
        for neighbor in neighbors_content:
            if neighbor[0] == 'empty' and neighbor[-1] not in \
                    self.model.reserved_cells:
                distance = self.closest_pallet(neighbor)
                if distance[-1] < min_distance[-1]:
                    min_distance = distance
        self.model.reserved_cells.append(min_distance[1])
        return min_distance[1]

    def can_drop_it(self, neighbors_content):
        for neighbor in neighbors_content:
            if neighbor[0] == 'pallet':
                return neighbor[-1]
        return False

    # TO-DO
    def pick_up_box(self, box):
        self.model.initial_boxes[box[-1]] = [self.unique_id, self.pos]

    # TO-DO
    def drop_box(self, pallet):
        self.model.pallets[pallet] += 1

    def step(self):
        # Get a list of max 4 neighbors per agent with the content (List / [])
        neighbors_content = self.get_neighbors_content()
        if self.has_box:
            # Checks whether agent is beside a pallet (Coordinate / False)
            can_drop_it = self.can_drop_it(neighbors_content)
            if can_drop_it:
                self.drop_box(can_drop_it)
                self.next_state = self.pos
                self.has_box = False
                self.model.picked_boxes[self.unique_id] = can_drop_it
            else:
                # TODO (Both)
                self.next_state = self.move_with_box(neighbors_content)
                self.model.picked_boxes[self.unique_id] = self.next_state
        else:
            # Check whether there is a box in the neighbors (Content / False)
            is_there_a_box = self.is_there_a_box(neighbors_content)

            if is_there_a_box:
                self.pick_up_box(is_there_a_box)
                self.next_state = self.pos
                self.has_box = True
            else:
                # Aparta tu movimiento
                self.move_without_box(neighbors_content)

        if self.has_box:
            self.next_live = 2
        else:
            self.next_live = 1

    def advance(self):
        self.model.reserved_cells = []
        self.model.reserved_boxes = []
        self.live = self.next_live
        self.model.grid.move_agent(self, self.next_state)


# Box agent
class Box(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.type = 'box'
        self.live = 0
        self.not_move = False
        self.agent_details = None
        self.next_state = None

    def step(self):
        if not self.not_move:
            if self.agent_details is None:
                if self.pos in self.model.initial_boxes:
                    self.agent_details = self.model.initial_boxes[self.pos]
                    del self.model.initial_boxes[self.pos]
                    self.model.picked_boxes[self.agent_details[0]] = \
                        self.agent_details[-1]
                    self.next_state = self.agent_details[-1]
                else:
                    self.next_state = self.pos
            else:
                self.next_state = self.model.picked_boxes[self.agent_details
                                                          [0]]
                if self.next_state in self.model.pallets:
                    self.not_move = True
        else:
            self.next_state = self.pos

    def advance(self):
        self.model.grid.move_agent(self, self.next_state)


class WarehouseModel(Model):
    def __init__(self, width, height):
        self.grid = MultiGrid(width, height, False)
        self.schedule = SimultaneousActivation(self)
        self.running = True  # Para la visualizacion usando navegador
        self.occupied_cells = {}
        self.reserved_cells = []
        self.picked_boxes = {}
        self.initial_boxes = {}
        self.pallets = {(0, 0): 0,
                        (14, 14): 0,
                        (0, 14): 0,
                        (14, 0): 0}
        self.reserved_boxes = []

        unique_id = 0
        for _ in range(5):
            robot = Robot((unique_id), self)
            while True:
                x = self.random.randrange(self.grid.width)
                y = self.random.randrange(self.grid.height)
                if (x, y) not in self.occupied_cells and \
                        (x, y) not in self.pallets:
                    self.grid.place_agent(robot, (x, y))
                    self.schedule.add(robot)
                    self.occupied_cells[(x, y)] = True
                    break
            unique_id += 1

        for _ in range(20):
            box = Box((unique_id), self)
            while True:
                x = self.random.randrange(self.grid.width)
                y = self.random.randrange(self.grid.height)
                if (x, y) not in self.occupied_cells and \
                        (x, y) not in self.pallets:
                    self.grid.place_agent(box, (x, y))
                    self.schedule.add(box)
                    self.occupied_cells[(x, y)] = True
                    break
            unique_id += 1

    def step(self):
        self.schedule.step()
