from flask import Flask, request, jsonify
import pennylane as qml
import numpy as np

app = Flask(__name__)

dev = qml.device("default.qubit", wires=1)

@qml.qnode(dev)
def circuit(theta):
    qml.RX(theta, wires=0)
    return qml.expval(qml.PauliZ(0))

@app.route("/run", methods=["POST"])
def run_circuit():
    data = request.json
    theta = data.get("theta", 0.5)  # Default value
    result = circuit(theta)
    return jsonify({"result": result})

if __name__ == "__main__":
    app.run(debug=True)
