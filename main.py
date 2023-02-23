from typing import List, Dict
from datetime import datetime
import json
from hashlib import sha256
from fastapi import FastAPI, status


class Blockchain:
    chain: List[Dict] = []
    transcation = 0  # Amount of moneys

    def __init__(self):
        # Genesis Block
        self.create_block(1, '0')

    def create_block(self, nonce, previous_hash) -> Dict:
        block = {}
        block['index'] = len(self.chain) + 1
        block['previous_hash'] = previous_hash
        block['timestamp'] = str(datetime.now())
        block['nonce'] = nonce
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    # Hash the block
    def hash(self, block: Dict) -> str:
        data = json.dumps(block, sort_keys=True).encode()
        return sha256(data).hexdigest()

    # Proof of Work
    def proof_of_work(self, previous_nonce) -> int:
        # Math Problem: Want nonce that make target hash in format '0000xxxxxxxxxxxx'
        new_nonce = 0
        check_proof = False

        while check_proof is False:
            new_nonce += 1
            hash_operation = sha256(
                str(new_nonce ** 2 - previous_nonce ** 2).encode()).hexdigest()
            check_proof = hash_operation[:4] == '0000'

        return new_nonce

    def check(self):
        previous_block = self.chain[0]
        block_index = 1
        while block_index < len(self.chain):
            block = self.chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_nonce = previous_block['nonce']
            nonce = block['nonce']

            hashoperate = sha256(
                str(nonce ** 2 - previous_nonce ** 2).encode()).hexdigest()
            if hashoperate[:4] != '0000':
                return False
            previous_block = block
            block_index += 1

        return True


app = FastAPI()
bc = Blockchain()


@app.get('/')
def hello():
    return "World"


@app.get('/chain', status_code=status.HTTP_200_OK)
def get_chain():
    return {
        "chain": bc.chain,
        "length": len(bc.chain)
    }


@app.get('/chain/valid', status_code=status.HTTP_200_OK)
def is_valid():
    return {
        "message": "Chain is valid" if bc.check() else "Chain is not valid"
    }


@app.post('/mining', status_code=status.HTTP_201_CREATED)
def mining_block():
    amount = 1000000

    bc.transcation += amount
    # Get previous block
    previous_block = bc.get_previous_block()
    # Find nonce
    previous_nonce = previous_block['nonce']
    nonce = bc.proof_of_work(previous_nonce)
    # Hash
    previous_hash = bc.hash(previous_block)
    # Create new block
    block = bc.create_block(nonce, previous_hash)
    block['data'] = bc.transcation
    return block
