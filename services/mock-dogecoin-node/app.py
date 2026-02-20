from flask import Flask, request, jsonify
import json
import uuid

app = Flask(__name__)

# Mocked transactions
transactions = []
blocks = []

@app.route('/', methods=['POST'])
def rpc():
    data = request.get_json()
    method = data.get('method')
    params = data.get('params', [])
    
    if method == 'getnewaddress':
        return jsonify({"result": f"D{uuid.uuid4().hex[:33]}", "error": None, "id": data.get('id')})
    
    if method == 'sendtoaddress':
        txid = uuid.uuid4().hex
        transactions.append({"txid": txid, "amount": params[1], "address": params[0]})
        return jsonify({"result": txid, "error": None, "id": data.get('id')})
        
    return jsonify({"result": None, "error": {"code": -32601, "message": "Method not found"}, "id": data.get('id')})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=22555)
