from flask import Flask, request, jsonify
import json
import os
import uuid

app = Flask(__name__)

# Mocked transactions (sendtoaddress and listtransactions)
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

    if method == 'listtransactions':
        # Return receives for deposit watcher. Optional: MOCK_LISTTRANSACTIONS_JSON env for fixed list.
        raw = os.environ.get('MOCK_LISTTRANSACTIONS_JSON')
        if raw:
            try:
                result = json.loads(raw)
                return jsonify({"result": result, "error": None, "id": data.get('id')})
            except json.JSONDecodeError:
                pass
        # Default: map our sent txs as "receive" for testing (category receive, address, amount, confirmations)
        n = int(params[1]) if len(params) > 1 else 10
        out = []
        for t in transactions[-n:]:
            out.append({
                "txid": t["txid"],
                "address": t["address"],
                "amount": t["amount"],
                "category": "receive",
                "confirmations": 7,
            })
        return jsonify({"result": out, "error": None, "id": data.get('id')})

    if method == 'gettransaction':
        txid = params[0] if params else None
        confirmations = 7
        # Optional: MOCK_GETTRANSACTION_CONFIRMATIONS or lookup in transactions
        for t in transactions:
            if t["txid"] == txid:
                return jsonify({
                    "result": {"confirmations": confirmations, "txid": txid},
                    "error": None,
                    "id": data.get('id')
                })
        # Unknown tx: return 0 confirmations
        return jsonify({
            "result": {"confirmations": 0, "txid": txid},
            "error": None,
            "id": data.get('id')
        })

    if method == 'sendrawtransaction':
        txid = uuid.uuid4().hex
        transactions.append({"txid": txid, "hex": params[0] if params else ""})
        return jsonify({"result": txid, "error": None, "id": data.get('id')})

    if method == 'listunspent':
        # For withdrawal: return mock UTXOs for the given address so BuildAndSignTx can run locally.
        minconf = int(params[0]) if params else 0
        maxconf = int(params[1]) if len(params) > 1 else 9999999
        addresses = list(params[2]) if len(params) > 2 else []
        out = []
        for addr in addresses:
            # One mock UTXO of 10000 DOGE for the address
            out.append({
                "txid": "mocktxid" + uuid.uuid4().hex[:24],
                "vout": 0,
                "address": addr,
                "amount": 10000.0,
                "confirmations": 6,
                "spendable": True,
            })
        return jsonify({"result": out, "error": None, "id": data.get('id')})

    if method == 'createrawtransaction':
        # Accept [inputs, outputs], return mock hex
        return jsonify({"result": "mock_raw_hex_" + uuid.uuid4().hex[:16], "error": None, "id": data.get('id')})

    if method == 'signrawtransaction':
        # Accept [hex, prevtxs?, privkeys?], return {hex, complete}
        raw = params[0] if params else ""
        return jsonify({
            "result": {"hex": raw + "_signed", "complete": True},
            "error": None,
            "id": data.get('id')
        })

    return jsonify({"result": None, "error": {"code": -32601, "message": "Method not found"}, "id": data.get('id')})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=22555)
