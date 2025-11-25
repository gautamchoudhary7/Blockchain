import hashlib
import json
from time import time
from typing import List, Dict, Any
from uuid import uuid4

class Block:
    """Represents a single block in the blockchain"""
    
    def __init__(self, index: int, transactions: List[Dict], proof: int, previous_hash: str):
        self.index = index
        self.transactions = transactions
        self.proof = proof
        self.previous_hash = previous_hash
        self.timestamp = time()
    
    def to_dict(self) -> Dict:
        """Convert block to dictionary"""
        return {
            'index': self.index,
            'transactions': self.transactions,
            'proof': self.proof,
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp
        }
    
    @staticmethod
    def hash(block: Dict) -> str:
        """Create a SHA-256 hash of a block"""
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()


class Blockchain:
    """The main blockchain class for supply chain transparency"""
    
    def __init__(self):
        self.chain: List[Block] = []
        self.current_transactions: List[Dict] = []
        self.nodes = set()
        
        # Create the genesis block
        self.new_block(proof=100, previous_hash='1')
    
    def new_block(self, proof: int, previous_hash: str = None) -> Block:
        """Create a new block in the blockchain"""
        block = Block(
            index=len(self.chain) + 1,
            transactions=self.current_transactions,
            proof=proof,
            previous_hash=previous_hash or self.hash(self.chain[-1].to_dict()) if self.chain else '1'
        )
        
        # Reset the current list of transactions
        self.current_transactions = []
        
        self.chain.append(block)
        return block
    
    def new_transaction(self, sender: str, recipient: str, product_id: str, 
                       product_name: str, location: str, status: str, 
                       metadata: Dict = None) -> int:
        """Add a new transaction to the list of transactions
        
        Returns the index of the block that will hold this transaction
        """
        transaction = {
            'id': str(uuid4()),
            'sender': sender,
            'recipient': recipient,
            'product_id': product_id,
            'product_name': product_name,
            'location': location,
            'status': status,
            'timestamp': time(),
            'metadata': metadata or {}
        }
        
        self.current_transactions.append(transaction)
        return self.last_block.index + 1
    
    @staticmethod
    def proof_of_work(last_proof: int) -> int:
        """Simple Proof of Work Algorithm:
        Find a number p' such that hash(pp') contains leading 4 zeroes
        where p is the previous proof and p' is the new proof
        """
        proof = 0
        while Blockchain.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof
    
    @staticmethod
    def valid_proof(last_proof: int, proof: int) -> bool:
        """Validates the proof: Does hash(last_proof, proof) contain 4 leading zeroes?"""
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"
    
    @property
    def last_block(self) -> Block:
        """Returns the last block in the chain"""
        return self.chain[-1]
    
    def hash(self, block: Dict) -> str:
        """Creates a SHA-256 hash of a block"""
        return Block.hash(block)
    
    def valid_chain(self, chain: List[Block]) -> bool:
        """Determine if a given blockchain is valid"""
        last_block = chain[0]
        current_index = 1
        
        while current_index < len(chain):
            block = chain[current_index]
            
            # Check that the hash of the block is correct
            last_block_hash = self.hash(last_block.to_dict())
            if block.previous_hash != last_block_hash:
                return False
            
            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block.proof, block.proof):
                return False
            
            last_block = block
            current_index += 1
        
        return True
    
    def get_product_history(self, product_id: str) -> List[Dict]:
        """Get the complete history of a product across the blockchain"""
        history = []
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.get('product_id') == product_id:
                    history.append({
                        'block_index': block.index,
                        'transaction': transaction,
                        'block_hash': self.hash(block.to_dict()),
                        'timestamp': block.timestamp
                    })
        return history
    
    def get_all_products(self) -> List[str]:
        """Get list of all unique product IDs in the blockchain"""
        products = set()
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.get('product_id'):
                    products.add(transaction.get('product_id'))
        return list(products)
    
    def to_dict(self) -> Dict:
        """Convert blockchain to dictionary format"""
        return {
            'chain': [block.to_dict() for block in self.chain],
            'length': len(self.chain)
        }

