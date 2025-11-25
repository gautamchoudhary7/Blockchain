from flask import Flask, jsonify, request
from flask_cors import CORS
from blockchain import Blockchain
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Instantiate the Blockchain
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    """Mine a new block"""
    # We run the proof of work algorithm to get the next proof
    last_block = blockchain.last_block
    last_proof = last_block.proof
    proof = blockchain.proof_of_work(last_proof)
    
    # We must receive a reward for finding the proof
    # The sender is "0" to signify that this node has mined a new coin
    blockchain.new_transaction(
        sender="0",
        recipient="miner",
        product_id="system",
        product_name="Block Reward",
        location="Network",
        status="mined"
    )
    
    # Forge the new block by adding it to the chain
    previous_hash = blockchain.hash(last_block.to_dict())
    block = blockchain.new_block(proof, previous_hash)
    
    response = {
        'message': 'New block forged',
        'index': block.index,
        'transactions': block.transactions,
        'proof': block.proof,
        'previous_hash': block.previous_hash
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    """Create a new transaction"""
    values = request.get_json()
    
    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'product_id', 'product_name', 'location', 'status']
    if not all(k in values for k in required):
        return 'Missing values', 400
    
    # Create a new transaction
    index = blockchain.new_transaction(
        sender=values['sender'],
        recipient=values['recipient'],
        product_id=values['product_id'],
        product_name=values['product_name'],
        location=values['location'],
        status=values['status'],
        metadata=values.get('metadata', {})
    )
    
    response = {
        'message': f'Transaction will be added to Block {index}',
        'transaction': blockchain.current_transactions[-1]
    }
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    """Get the full blockchain"""
    response = {
        'chain': [block.to_dict() for block in blockchain.chain],
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

@app.route('/chain/valid', methods=['GET'])
def valid_chain():
    """Check if the blockchain is valid"""
    is_valid = blockchain.valid_chain(blockchain.chain)
    response = {
        'valid': is_valid,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

@app.route('/products', methods=['GET'])
def get_products():
    """Get all unique products in the blockchain"""
    products = blockchain.get_all_products()
    response = {
        'products': products,
        'count': len(products)
    }
    return jsonify(response), 200

@app.route('/products/<product_id>/history', methods=['GET'])
def get_product_history(product_id):
    """Get the complete history of a specific product"""
    history = blockchain.get_product_history(product_id)
    response = {
        'product_id': product_id,
        'history': history,
        'count': len(history)
    }
    return jsonify(response), 200

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get blockchain statistics"""
    total_transactions = sum(len(block.transactions) for block in blockchain.chain)
    products = blockchain.get_all_products()
    
    response = {
        'total_blocks': len(blockchain.chain),
        'total_transactions': total_transactions,
        'total_products': len(products),
        'pending_transactions': len(blockchain.current_transactions)
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

