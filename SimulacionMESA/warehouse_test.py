"""
This programs helps to analize the result from running
the multiagent system of a robot, as well as
storing these graphs in the same folder

Aleny Sofia Arévalo Magdaleno |  A01751272
Luis Humberto Romero Pérez | A01752789
Valeria Martínez Silva | A01752167
Pablo González de la Parra | A01745096

Created: 14 / 11 / 2022
"""

from warehouse import *
import matplotlib.pyplot as plt

# Initial variables
WIDTH = 30
HEIGHT = 30
NUM_AGENTS = [10, 25, 30]
MAX_STEPS = 1500

# Calling the model [numAgents] amount of times
for agent in NUM_AGENTS:
    model = WarehouseModel(WIDTH, HEIGHT, agent, MAX_STEPS)

    for _ in range(MAX_STEPS):
        model.step()

    # Get agent moves (steps)
    agent_moves = model.datacollector.get_agent_vars_dataframe()

    # Calculate moves for each agent
    all_agent_moves = agent_moves.xs(model.time - 1, level="Step")

    # Plot total agents moves
    all_agent_moves[:5].plot(kind="bar")
    plt.title("Agents total moves")
    plt.ylabel("Moves (steps)")
    plt.xlabel("Agent ID")
    plt.savefig(f'SimulacionMESA/Statistics/{agent}_boxes_movements.png')

    # Print statistics
    print(f"-----Datos iniciales-----")
    print(f"Álmacen de : {WIDTH} * {HEIGHT} espacios")
    print(f"Número de celdas totales: {WIDTH * HEIGHT}")
    print(f"Número de agentes: {agent}")
    print(f"Tiempo máximo: {MAX_STEPS} steps")
    print(f"-----Datos finales-----")
    print(f"Tiempo recorrido: {model.time} steps\n")
