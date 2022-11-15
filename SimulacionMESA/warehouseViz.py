
from warehouse import *
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer


def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "Layer": 0,
                 "Color": "red",
                 "r": 0.5}

    if agent.live == 1:
        portrayal["Color"] = "blue"
        portrayal["Layer"] = 0
    elif agent.live == 2:
        portrayal["Color"] = "green"
        portrayal["Layer"] = 0
    else:
        portrayal["Color"] = "grey"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.1

    return portrayal


ancho = 15
alto = 15
grid = CanvasGrid(agent_portrayal, ancho, alto, 750, 750)
server = ModularServer(WarehouseModel,
                       [grid],
                       "Game of Life Model",
                       {"width": ancho, "height": alto})
server.port = 8521
server.launch()
