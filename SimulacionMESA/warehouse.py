"""
This programs helps to model and simulate a warehouse
where the objective of the robots is to pick up all the
boxes and put them in pallets

Aleny Sofia Arévalo Magdaleno |  A01751272
Luis Humberto Romero Pérez | A01752789
Valeria Martínez Silva | A01752167
Pablo González de la Parra | A01745096

Created: 14 / 11 / 2022
"""

import math
import random
from mesa import Agent, Model, DataCollector
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation


def all_pallets_full(model):
    """Determines whether all pallets are full
    Parameters: model -> Model of the multiagent system
    Return value: bool -> If all pallets are full"""
    for value in model.pallets.values():
        if value < 5:
            return False
    return True


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
        self.objective_box = None
        self.moves = 0

    def get_neighbors_content(self):
        """Facilitates the filtering and detection
        of content in neighboring cells
        Parameters: None
        Return value: neighbors_content -> Content
        of all neighboring cells"""
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
        """Checks whether there is a pallet in neighbor
        cell and if it isn't full
        Parameters: neighbors_content -> Content
        of all neighboring cells
        Return value: coordinate -> If there is a pallet"""
        for neighbor in neighbors_content:
            if neighbor[0] == 'pallet':
                # Number of boxes in pallet
                if neighbor[1] < 5:
                    # Return coordinate of pallet
                    return neighbor[-1]
        return False

    def drop_box(self, pallet_coordinate):
        """Drops a box, sums the number of
        boxes in a pallet
        Parameters: pallet_coordinate -> Coordinate of a
        pallet
        Return value: None"""
        self.model.pallets[pallet_coordinate] += 1
        self.next_state = self.pos
        self.has_box = False
        self.model.picked_boxes[self.unique_id] = pallet_coordinate

    def closest_pallet(self, neighbor):
        """Determines the closest non full
        pallet of a neighbor cell
        Parameters: neighbor -> A single neighbor cell
        Return value: closest_pallet -> Info. of a pallet"""
        x1, y1 = neighbor[-1]
        min_distance = float('inf')
        closest_pallet = 0
        for key in self.model.pallets:
            if self.model.pallets[key] < 5:
                # Calculates the distance between cell and pallet
                distance = math.sqrt(((key[0] - x1)**2) + ((key[1] - y1)**2))
                if distance < min_distance:
                    # Closest pallet and neighbor information
                    closest_pallet = [key, neighbor[-1], distance]
                    min_distance = distance
        if closest_pallet:
            # Returns info of closest pallet to neighbor
            return closest_pallet
        else:
            # There isn't a close pallet
            return False

    def move_with_box(self, neighbors_content):
        """Determines the next position that is closest
        to a non full pallet
        Parameters: neighbors_content -> Content
        of all neighboring cells
        Return value: shortest_path -> Best neighbor cell"""
        min_distance = float('inf')
        shortest_path = []
        for neighbor in neighbors_content:
            if neighbor[0] == 'empty' and neighbor[-1] not in \
                    self.model.reserved_cells:
                distance = self.closest_pallet(neighbor)
                if distance:
                    # If there is a closest pallet
                    if distance[-1] < min_distance:
                        min_distance = distance[-1]
                        shortest_path = distance
        if shortest_path:
            # Returns best neighbor cell
            self.model.reserved_cells.append(shortest_path[1])
            self.next_state = shortest_path[1]
            self.model.picked_boxes[self.unique_id] = self.next_state
            return shortest_path[1]
        else:
            # There is no best neighbor cell
            self.next_state = self.pos
            self.model.picked_boxes[self.unique_id] = self.next_state
            return self.pos

    def is_there_a_box(self, neighbors_content):
        """Checks whether there is a single
        box in neighbor cell
        Parameters: neighbors_content -> Content
        of all neighboring cells
        Return value: neighbor -> Cell with a box"""
        for neighbor in neighbors_content:
            if neighbor[0] == 'box' and neighbor[-1] not \
                    in self.model.reserved_boxes:
                self.model.reserved_boxes.append(neighbor[-1])
                return neighbor
        return False

    def move_without_box(self, neighbors_content):
        """Moves to a random empty cell
        Parameters: neighbors_content -> Content
        of all neighboring cells
        Return value: bool -> If robot can move"""
        random.shuffle(neighbors_content)
        for neighbor in neighbors_content:
            if neighbor[0] == 'empty' and neighbor[-1] not in \
                    self.model.reserved_cells:
                self.model.reserved_cells.append(neighbor[-1])
                self.next_state = neighbor[-1]
                self.moves += 1
                return True
        # Can't move anywhere
        self.next_state = self.pos
        return False

    def pick_up_box(self, box):
        """Picks up a box
        Parameters: box -> Coordinate of cell with box
        Return value: None"""
        self.model.picked_objective_boxes.append(box[-1])
        # if box[-1] in self.model.objective_boxes:
        #     self.model.objective_boxes.remove(box[-1])
        self.model.initial_boxes[box[-1]] = [self.unique_id, self.pos]
        self.next_state = self.pos
        self.has_box = True

    def call_for_help(self, box_position):
        """Adds coordinate of box for empty robots to mark
        them as their objective
        Parameters: box_position -> Coordinate of cell with box
        Return value: None"""
        if box_position not in self.model.objective_boxes_added:
            self.model.objective_boxes.append(box_position)
            self.model.objective_boxes_added.append(box_position)

    def closest_cell_objetive_box(self, neighbor):
        """Determines the closest cell to
        objective box
        Parameters: neighbor -> Coordinate of cell with box
        Return value: distance -> Distance between a neighbor
        and a cell with box"""
        x1, y1 = neighbor[-1]
        distance = math.sqrt(((self.objective_box[0] - x1)**2) +
                             ((self.objective_box[1] - y1)**2))
        return distance

    def move_to_objective_box(self, neighbors_content):
        """Determines the shortest path to box from
        and empty robot agent. Similar to move_with_box
        Parameters: neighbors_content -> Content
        of all neighboring cells
        Return value: shortest_path -> Best next move"""
        min_distance = float('inf')
        shortest_path = self.pos
        for neighbor in neighbors_content:
            # Only considers empty cells
            if neighbor[0] == 'empty' and neighbor[-1] not in \
                    self.model.reserved_cells:
                distance = self.closest_cell_objetive_box(neighbor)
                if distance < min_distance:
                    min_distance = distance
                    shortest_path = neighbor[-1]
        if shortest_path:
            self.moves += 1
            # Returns best neighbor cell
            self.model.reserved_cells.append(shortest_path)
            self.next_state = shortest_path
            return shortest_path
        else:
            # There is no best neighbor cell
            self.next_state = self.pos
            return self.pos

    def step(self):
        if self.objective_box in self.model.picked_objective_boxes:
            self.objective_box = None
        """Hierarchy of steps in robot"""
        # Get a list of neighbors with the content of each cell (List / [])
        neighbors_content = self.get_neighbors_content()
        # Check whether there is a box in the neighbors (Content / False)
        is_there_a_box = self.is_there_a_box(neighbors_content)
        if self.has_box:
            if is_there_a_box:
                self.call_for_help(is_there_a_box[-1])
            # Checks whether agent is beside a pallet (Coordinate / False)
            can_drop_it = self.can_drop_it(neighbors_content)
            if can_drop_it:
                # Drop a box in a pallet
                self.drop_box(can_drop_it)
            else:
                # Move to a pallet
                self.move_with_box(neighbors_content)
        else:
            if is_there_a_box:
                if self.objective_box:
                    if self.objective_box not in \
                            self.model.picked_objective_boxes:
                        self.model.objective_boxes.append(self.objective_box)
                    self.objective_box = None
                self.pick_up_box(is_there_a_box)
            else:
                if self.model.objective_boxes and not self.objective_box:
                    self.objective_box = self.model.objective_boxes.pop()
                    self.move_to_objective_box(neighbors_content)
                elif self.objective_box:
                    self.move_to_objective_box(neighbors_content)
                else:
                    # Aparta tu movimiento
                    self.move_without_box(neighbors_content)

        # Changes color for visualization
        if self.has_box:
            self.next_color = 2
        else:
            self.next_color = 1

    def advance(self):
        # Resets reserved cells and boxes
        self.model.reserved_cells = []
        self.model.reserved_boxes = []
        # Changes color for visualization
        self.color = self.next_color
        # Moves agent
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
        self.moves = 0

    def is_picked_up(self):
        """Checks whether a box is picked up
        Parameters: None
        Return value: bool -> Whether or not is picked up"""
        if self.pos in self.model.initial_boxes:
            return True
        else:
            return False

    def get_picked_up(self):
        """Moves box to agent position
        Parameters: None
        Return value: None"""
        self.agent_details = self.model.initial_boxes[self.pos]
        del self.model.initial_boxes[self.pos]
        self.model.picked_boxes[self.agent_details[0]] = \
            self.agent_details[-1]
        self.next_state = self.agent_details[-1]
        self.picked_up = True

    def stay_still(self):
        """Stays still
        Parameters: None
        Return value: None"""
        self.picked_up = False
        self.next_state = self.pos

    def move_with_agent(self):
        """Moves to same position as agent
        Parameters: None
        Return value: None"""
        self.picked_up = True
        self.moves += 1
        self.next_state = self.model.picked_boxes[
            self.agent_details[0]]

    def step(self):
        """Hierarchy of steps in box"""
        # If it is not in pallet
        if not self.not_move:
            if self.agent_details is None:
                if self.is_picked_up():
                    # Get picked up by agent
                    self.get_picked_up()
                else:
                    # Don't move from current position
                    self.stay_still()
            else:
                self.move_with_agent()
                # If it is in a pallet
                if self.next_state in self.model.pallets:
                    self.picked_up = False
                    self.not_move = True
        # If it is in pallet
        else:
            self.picked_up = False
            self.next_state = self.pos

        # Changes color for visualization
        if self.picked_up:
            self.next_color = 3
        else:
            self.next_color = 0

    def advance(self):
        # Changes color for visualization
        self.color = self.next_color
        # Moves agent
        self.model.grid.move_agent(self, self.next_state)


# Warehouse model
class WarehouseModel(Model):
    def __init__(self, width, height, NAgents, maxSteps):
        # Standard variables
        self.grid = MultiGrid(width, height, False)
        self.schedule = SimultaneousActivation(self)
        self.running = True
        self.picked_boxes = {}
        self.reserved_cells = []
        self.initial_boxes = {}
        self.reserved_boxes = []
        self.pallets = {}
        self.maxSteps = maxSteps

        self.objective_boxes = []
        self.objective_boxes_added = []
        self.picked_objective_boxes = []

        # Calculate the number of pallets
        num_pallets = math.ceil(NAgents / 5)
        corners = [(0, 0), (0, height-1), (width-1, height-1), (width-1, 0)]

        # Assing number of pallets
        for count in range(num_pallets):
            if count < 4:
                # First add the corners
                self.pallets[corners[count]] = 0
            else:
                # Add pallets on top and bottom row
                if count % 2 == 0:
                    corner = self.random.choice([0, 2])
                    y = corners[corner][1]
                    while True:
                        # Move in x position
                        x = self.random.randrange(2, self.grid.width-3)
                        if (x, y) not in self.pallets:
                            self.pallets[(x, y)] = 0
                            break
                # Add pallets on left and right column
                else:
                    corner = self.random.choice([1, 3])
                    x = corners[corner][0]
                    while True:
                        # Choose in y position
                        y = self.random.randrange(2, self.grid.height-3)
                        if (x, y) not in self.pallets:
                            self.pallets[(x, y)] = 0
                            break

        unique_id = 0
        occupied_cells = {}
        # Create robot agent
        for _ in range(5):
            robot = Robot((unique_id), self)
            while True:
                # Choose random cell
                x = self.random.randrange(2, self.grid.width-3)
                y = self.random.randrange(2, self.grid.height-3)
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
                x = self.random.randrange(2, self.grid.width-3)
                y = self.random.randrange(2, self.grid.height-3)
                if (x, y) not in occupied_cells and \
                        (x, y) not in self.pallets:
                    self.grid.place_agent(box, (x, y))
                    self.schedule.add(box)
                    occupied_cells[(x, y)] = True
                    break
            unique_id += 1

        # Statistics
        self.datacollector = DataCollector(
            agent_reporters={"Moves": "moves"})
        self.time = 0

    def step(self):
        # Model step
        if all_pallets_full(self) or self.time >= self.maxSteps:
            return
        else:
            self.time += 1
        self.datacollector.collect(self)
        self.schedule.step()
