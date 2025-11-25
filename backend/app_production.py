"""
Production version of the Flask app with environment variable support
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from blockchain import Blockchain
import os

app = Flask(__name__)

# Configure CORS based on environment
allowed_origins = os.environ.get('ALLOWED_ORIGINS', '*').split(',')
CORS(app, resources={r"/*": {"origins": allowed_origins}})

# Configuration
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
app.config['ENV'] = os.environ.get('FLASK_ENV', 'production')

# Instantiate the Blockchain
blockchain = Blockchain()

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for monitoring"""
    return jsonify({'status': 'healthy', 'service': 'blockchain-api'}), 200

@app.route('/mine', methods=['GET'])
def mine():
    """Mine a new block"""
    last_block = blockchain.last_block
    last_proof = last_block.proof
    proof = blockchain.proof_of_work(last_proof)
    
    blockchain.new_transaction(
        sender="0",
        recipient="miner",
        product_id="system",
        product_name="Block Reward",
        location="Network",
        status="mined"
    )
    
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
    
    required = ['sender', 'recipient', 'product_id', 'product_name', 'location', 'status']
    if not all(k in values for k in required):
        return jsonify({'error': 'Missing required fields'}), 400
    
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
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    app.run(host=host, port=port, debug=app.config['DEBUG'])

