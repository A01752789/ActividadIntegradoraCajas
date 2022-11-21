"""
This programs helps to visualize the process of the multi-agent
system in the web browser

Aleny Sofia Arévalo Magdaleno |  A01751272
Luis Humberto Romero Pérez | A01752789
Valeria Martínez Silva | A01752167
Pablo González de la Parra | A01745096

Created: 14 / 11 / 2022
"""

from warehouse import *
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer


def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "Layer": 0,
                 "Color": "red",
                 "r": 0.5}

    if agent.color == 1:
        portrayal["Color"] = "blue"
        portrayal["Layer"] = 0
    elif agent.color == 2:
        portrayal["Color"] = "red"
        portrayal["Layer"] = 0
    elif agent.color == 3:
        portrayal["Color"] = "blue"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.1
    else:
        portrayal["Color"] = "grey"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.1

    return portrayal


ancho = 15
alto = 15
NAgents = 30
grid = CanvasGrid(agent_portrayal, ancho, alto, 750, 750)
server = ModularServer(WarehouseModel,
                       [grid],
                       "Warehouse Model",
                       {"width": ancho, "height": alto, "NAgents": NAgents})
server.port = 8521
server.launch()
