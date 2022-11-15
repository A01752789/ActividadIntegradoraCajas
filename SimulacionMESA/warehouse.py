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
        self.has_box = False
        self.next_state = None

    def get_neighbors_content(self):
        neighbors_content = []
        # Vecinos del agente
        neighbors = self.model.grid.get_neighborhood(
                self.pos,
                moore=False,
                include_center=False)
        for neighbor in neighbors:
            # Contenido de cada celda
            content = self.model.grid.get_cell_list_contents(neighbor)
            if content:
                # Celda no esta vacía
                num_boxes = 0
                for object in content:
                    if object.type == 'robot':
                        # Si hay un robot
                        neighbors_content.append(['robot', neighbor])
                        break
                    elif object.type == 'box':
                        # Si tiene una caja
                        num_boxes += 1
                else:
                    if neighbor in self.model.pallets:
                        neighbors_content.append(['pallet', num_boxes, neighbor])
                    else:
                        neighbors_content.append(['box', num_boxes, neighbor])
            else:
                if neighbor in self.model.pallets:
                    neighbors_content.append(['pallet', 0, neighbor])
                else:
                    neighbors_content.append(['empty', neighbor])
        return neighbors_content

    def is_there_a_box(self, neighbors_content):
        for neighbor in neighbors_content:
            if neighbor[0] == 'box':
                return neighbor
        return False

    def move_without_box(self, neighbors_content):
        # random_neighbors_content = random.shuffle(neighbors_content)
        for neighbor in neighbors_content:
            if neighbor[0] == 'empty' and neighbor[-1] not in \
                    self.model.reserved_cells:
                self.model.reserved_cells.append(neighbor[-1])
                self.next_state = neighbor[-1]
                return True
        self.next_state = self.pos
        return False

    def can_drop_it(self, neighbors_content):
        for neighbor in neighbors_content:
            if neighbor[0] == 'pallet':
                return neighbor[-1]
        return False

    # TO-DO
    def pick_up_box(self, box):
        self.model.picked_boxes.append(box[-1])

    # TO-DO
    def drop_box(self, pallet):
        self.model.pallets[pallet] += 1

    def step(self):
        print("robot")

        # Get a list of max 4 neighbors per agent with their content (List / Empty list)
        neighbors_content = self.get_neighbors_content()

        if self.has_box:
            # Checks whether agent is beside a pallet (Coordinate / False)
            can_drop_it = self.can_drop_it(neighbors_content)

            if can_drop_it:
                self.drop_box(can_drop_it)
                self.next_state = self.pos
                self.has_box = False
            else:
                self.move_without_box(neighbors_content)
                # Move towards end place y apartala
        else:
            # Check whether there is a box in the neighbors (List of cell content / False)
            is_there_a_box = self.is_there_a_box(neighbors_content)

            if is_there_a_box:
                self.pick_up_box(is_there_a_box)
                self.next_state = self.pos
                self.has_box = True
            else:
                # Aparta tu movimiento
                self.move_without_box(neighbors_content)

    def advance(self):
        self.model.reserved_cells = []
        self.model.grid.move_agent(self, self.next_state)


# Box agent
class Box(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.type = 'box'
        self.live = 0
        self.next_state = None

    def step(self):
        print("box")
        if self.pos in self.model.picked_boxes:
            self.model.grid.remove_agent(self)
            self.model.picked_boxes.remove()

    def advance(self):
        print("adbox")

        ...


class WarehouseModel(Model):
    def __init__(self, width, height):
        self.grid = MultiGrid(width, height, False)
        self.schedule = SimultaneousActivation(self)
        self.running = True  # Para la visualizacion usando navegador
        self.occupied_cells = {}
        self.reserved_cells = []
        self.pallets = {(0, 0): 0}
        self.picked_boxes = []

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

        for _ in range(10):
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
