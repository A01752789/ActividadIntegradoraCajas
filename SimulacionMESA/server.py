from flask import Flask, request, jsonify
from warehouse import *

# Size of the board:
number_agents = 10
width = 28
height = 28
warehouseModel = None
currentStep = 0

app = Flask("Warehouse")


@app.route('/init', methods=['POST', 'GET'])
def initModel():
    global currentStep, warehouseModel, number_agents, width, height

    if request.method == 'POST':
        # number_agents = int(request.form.get('NAgents'))
        width = int(request.form.get('width'))
        height = int(request.form.get('height'))
        currentStep = 0

        print(request.form)
        print(width, height)
        warehouseModel = WarehouseModel(width, height)

        return jsonify({"message": "Parameters received, model initiated."})


@app.route('/getRobots', methods=['GET'])
def getRobots():
    global warehouseModel

    if request.method == 'GET':
        robotPositions = [{"id": str(obj.unique_id), "x": x, "y": 1, "z": z}
                          for (a, x, z) in warehouseModel.grid.coord_iter()
                          for obj in a if isinstance(obj, Robot)]
        return jsonify({'positions': robotPositions})


@app.route('/getBoxes', methods=['GET'])
def getBoxes():
    global warehouseModel

    if request.method == 'GET':
        boxesPositions = [{"id": str(obj.unique_id), "x": x, "y": 1, "z": z}
                          for (a, x, z) in warehouseModel.grid.coord_iter()
                          for obj in a if isinstance(obj, Box)]
        return jsonify({'positions': boxesPositions})


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
