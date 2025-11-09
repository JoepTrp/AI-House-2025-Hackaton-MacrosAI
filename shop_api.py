from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/groceries', methods=['POST'])
def acknowledge_groceries():
    # You don't need to do anything with the incoming data
    # just return the acknowledgment.
    
    # We will get the data just to show it's possible
    data = request.json
    print(f"Received data: {data}")
    
    # Return your specific message and a 200 OK status
    response_message = {"answer": "Groceries Acknowledged"}
    return jsonify(response_message), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)