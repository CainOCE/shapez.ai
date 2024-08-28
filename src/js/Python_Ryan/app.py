from flask import Flask, request, jsonify
from flask_cors import CORS
from model import Model
app = Flask(__name__)
CORS(app)

@app.route('/process', methods=['POST'])
# It gets the data from the js which is all good, then if processes it then a value is returned to such js function.
# It still can be imporved if there is any issues with it
def process():
    data = request.json

    print(data)
    model = Model(data)
    print(model.GameState)

    example_return = "example of a return"
    return jsonify({'move': example_return})

if __name__ == '__main__':
    app.run(debug=True)