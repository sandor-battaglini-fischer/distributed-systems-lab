from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    # place holders
    return jsonify({
        'message': 'Analysis complete',
        'data': data
    })

if __name__ == '__main__':
    app.run(debug=True)