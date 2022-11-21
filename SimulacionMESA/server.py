"""
This programs helps to connect the simulation from Python
using MESA to Unity by creating HTTP routes respectively

Aleny Sofia Arévalo Magdaleno |  A01751272
Luis Humberto Romero Pérez | A01752789
Valeria Martínez Silva | A01752167
Pablo González de la Parra | A01745096

Created: 14 / 11 / 2022
"""

from flask import Flask, request, jsonify
from warehouse import *

# Size of the board:
NAgents = 1
width = 28
height = 28
warehouseModel = None
currentStep = 0
maxSteps = 0

app = Flask("Warehouse")


@app.route('/', methods=['POST', 'GET'])
def helloWorld():
    if request.method == 'GET':
        return jsonify({"message": "Connection with server was successful!"})


@app.route('/init', methods=['POST', 'GET'])
def initModel():
    global currentStep, warehouseModel, NAgents, width, height

    if request.method == 'POST':
        NAgents = int(request.form.get('NAgents'))
        width = int(request.form.get('width'))
        maxSteps = int(request.form.get('maxSteps'))
        height = int(request.form.get('height'))
        currentStep = 0

        warehouseModel = WarehouseModel(width, height, NAgents, maxSteps)

        return jsonify({"message": "Parameters received, model initiated."})


@app.route('/getRobots', methods=['GET'])
def getRobots():
    global warehouseModel

    if request.method == 'GET':
        robotPositions = [{"id": str(obj.unique_id),
                           "x": x, "y": 0, "z": z,
                           "hasBox": obj.has_box}
                          for (a, x, z) in warehouseModel.grid.coord_iter()
                          for obj in a if isinstance(obj, Robot)]
        return jsonify({'positions': robotPositions})


@app.route('/getBoxes', methods=['GET'])
def getBoxes():
    global warehouseModel

    if request.method == 'GET':
        boxesPositions = [{"id": str(obj.unique_id),
                           "x": x, "y": 0, "z": z,
                           "picked_up": obj.picked_up}
                          for (a, x, z) in warehouseModel.grid.coord_iter()
                          for obj in a if isinstance(obj, Box)]
        return jsonify({'positions': boxesPositions})


@app.route('/getPallets', methods=['GET'])
def getPallets():
    global warehouseModel

    if request.method == 'GET':
        palletsPositionsValues = []
        count = 0
        for x, y in warehouseModel.pallets.keys():
            palletsPositionsValues.append({"id": count,
                                           "x": x,
                                           "y": 0,
                                           "z": y,
                                           "value": warehouseModel.pallets[
                                            (x, y)]})
            count += 1
        return jsonify({'positions': palletsPositionsValues})


@app.route('/update', methods=['GET'])
def updateModel():
    global currentStep, warehouseModel
    if request.method == 'GET':
        warehouseModel.step()
        currentStep += 1
        return jsonify({'message': f'Model updated to step {currentStep}.',
                        'currentStep': currentStep})


if __name__ == '__main__':
    app.run(host="localhost", port=8585, debug=True)
