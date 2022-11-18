import math
from math import sqrt
from mesa import Agent, Model, DataCollector
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
import random


# Robot agent
class Robot(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        # Agent variables
        self.type = 'robot'
        self.color = 1
        self.next_color = None
        self.has_box = False
        self.next_state = None

    def get_neighbors_content(self):
        neighbors_content = []
        # Neighbors
        neighbors = self.model.grid.get_neighborhood(
                self.pos,
                moore=False,
                include_center=False)
        for neighbor in neighbors:
            # If neighbor is a pallet
            if neighbor in self.model.pallets:
                neighbors_content.append(['pallet',
                                         self.model.pallets[neighbor],
                                         neighbor])
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
                    # If there is a robot carrying a box
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

    def can_drop_it(self, neighbors_content):
        for neighbor in neighbors_content:
            if neighbor[0] == 'pallet':
                if neighbor[1] < 5:
                    return neighbor[-1]
        return False

    def drop_box(self, pallet):
        self.model.pallets[pallet] += 1

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
        if closest_pallet:
            return closest_pallet
        else:
            return False

    def move_with_box(self, neighbors_content):
        min_distance = [float('inf')]
        for neighbor in neighbors_content:
            if neighbor[0] == 'empty' and neighbor[-1] not in \
                    self.model.reserved_cells:
                distance = self.closest_pallet(neighbor)
                if distance:
                    if distance[-1] < min_distance[-1]:
                        min_distance = distance
                else:
                    min_distance = [0, self.pos]
        self.model.reserved_cells.append(min_distance[1])
        return min_distance[1]

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

    def pick_up_box(self, box):
        self.model.initial_boxes[box[-1]] = [self.unique_id, self.pos]

    def step(self):
        # Get a list of neighbors with the content of each cell (List / [])
        neighbors_content = self.get_neighbors_content()
        if self.has_box:
            # Checks whether agent is beside a pallet (Coordinate / False)
            can_drop_it = self.can_drop_it(neighbors_content)
            if can_drop_it:
                # Drop a box in a pallet
                self.drop_box(can_drop_it)
                self.next_state = self.pos
                self.has_box = False
                self.model.picked_boxes[self.unique_id] = can_drop_it
            else:
                # Move to a pallet
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
            self.next_color = 2
        else:
            self.next_color = 1

    def advance(self):
        self.model.reserved_cells = []
        self.model.reserved_boxes = []
        self.color = self.next_color
        self.model.grid.move_agent(self, self.next_state)


# Box agent
class Box(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        # Agent variables
        self.type = 'box'
        self.color = 0
        self.next_color = 0
        self.not_move = False
        self.agent_details = None
        self.next_state = None
        self.picked_up = False

    def step(self):
        if not self.not_move:
            if self.agent_details is None:
                if self.pos in self.model.initial_boxes:
                    self.agent_details = self.model.initial_boxes[self.pos]
                    del self.model.initial_boxes[self.pos]
                    self.model.picked_boxes[self.agent_details[0]] = \
                        self.agent_details[-1]
                    self.next_state = self.agent_details[-1]
                    self.picked_up = True
                else:
                    self.picked_up = False
                    self.next_state = self.pos
            else:
                self.picked_up = True
                self.next_state = self.model.picked_boxes[self.agent_details
                                                          [0]]
                if self.next_state in self.model.pallets:
                    self.picked_up = False
                    self.not_move = True
        else:
            self.picked_up = False
            self.next_state = self.pos

        if self.picked_up:
            self.next_color = 3
        else:
            self.next_color = 0

    def advance(self):
        self.color = self.next_color
        self.model.grid.move_agent(self, self.next_state)


# Warehouse model
class WarehouseModel(Model):
    def __init__(self, width, height, NAgents):
        # Standard variables
        self.grid = MultiGrid(width, height, False)
        self.schedule = SimultaneousActivation(self)
        self.running = True
        self.picked_boxes = {}
        self.reserved_cells = []
        self.initial_boxes = {}
        self.reserved_boxes = []

        # Calculate the number of pallets
        num_pallets = math.ceil(NAgents / 5)
        corners = [(0, 0), (0, 14), (14, 14), (14, 0)]
        self.pallets = {}

        # Assing number of pallets
        count = 0
        while count < num_pallets:
            if count < 4:
                self.pallets[corners[count]] = 0
            else:
                if count % 2 == 0:
                    corner = self.random.choice([0, 2])
                    y = corners[corner][1]
                    while True:
                        x = self.random.randrange(self.grid.width)
                        if (x, y) not in self.pallets:
                            self.pallets[(x, y)] = 0
                            break
                else:
                    corner = self.random.choice([1, 3])
                    x = corners[corner][0]
                    while True:
                        y = self.random.randrange(self.grid.height)
                        if (x, y) not in self.pallets:
                            self.pallets[(x, y)] = 0
                            break
            count += 1

        unique_id = 0
        occupied_cells = {}
        # Create robot agent
        for _ in range(5):
            robot = Robot((unique_id), self)
            while True:
                # Choose random cell
                x = self.random.randrange(self.grid.width)
                y = self.random.randrange(self.grid.height)
                if (x, y) not in occupied_cells and \
                        (x, y) not in self.pallets:
                    self.grid.place_agent(robot, (x, y))
                    self.schedule.add(robot)
                    occupied_cells[(x, y)] = True
                    break
            unique_id += 1

        # Create box agent
        for _ in range(NAgents):
            box = Box((unique_id), self)
            while True:
                # Choose random cell
                x = self.random.randrange(self.grid.width)
                y = self.random.randrange(self.grid.height)
                if (x, y) not in occupied_cells and \
                        (x, y) not in self.pallets:
                    self.grid.place_agent(box, (x, y))
                    self.schedule.add(box)
                    occupied_cells[(x, y)] = True
                    break
            unique_id += 1

    def step(self):
        # Model step
        print(self.pallets)
        self.schedule.step()
