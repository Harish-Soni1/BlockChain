import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

class BlockChain:

    def __init__(self) -> None:
        self.chain = []
        self.transaction = []
        self.createBlock(proof = 1, prevHash = '0')
        self.nodes = set()

    def createBlock(self, proof, prevHash):
        block = {
            'index': len(self.chain)+1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'prevHash': prevHash,
            'transaction': self.transaction
        }
        self.transaction = []
        self.chain.append(block)
        return block

    def getLastBlock(self):
        return self.chain[-1]

    def proofOfWork(self, prevProof) -> int:
        newProof = 1
        checkProof = False

        while not checkProof:
            hashOperation = hashlib.sha256(str(newProof**2 - prevProof**2).encode()).hexdigest()
            if hashOperation[:4] == '0000':
                checkProof = True
            else:
                newProof+=1
        
        return newProof

    def hash(self, block):
        encodedBlock = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encodedBlock).hexdigest()

    def isChainValid(self, chain) -> bool:
        prevBlock = chain[0]
        blockIndex = 1

        while blockIndex < len(chain):
            block = chain[blockIndex]
            if block['prevHash'] != self.hash(prevBlock):
                return False
            
            prevProof = prevBlock['proof']
            proof = block['proof']
            hashOperation = hashlib.sha256(str(proof**2 - prevProof**2).encode()).hexdigest()
            if hashOperation[:4] != '0000':
                return False

            prevBlock = block
            blockIndex += 1

        return True

    def addTransaction(self, sender, reciever, amount) -> int:
        self.transaction.append({
            'sender': sender,
            'reciever': reciever,
            'amount': amount
        })

        prevBlock = self.getLastBlock()
        return prevBlock['index'] + 1

    def addNode(self, address):
        parsedURL = urlparse(address)
        self.nodes.add(parsedURL.netloc)

    def replace_chain(self) -> bool:
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/getMyChain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.isChainValid(chain):
                    max_length = length
                    longest_chain = chain

        if longest_chain:
            self.chain = longest_chain
            return True
        
        return False


app = Flask(__name__)
node_address = str(uuid4()).replace('-', '')
myChain = BlockChain()

@app.route("/mineChain", methods=['Get'])
def mineBlock():
    prevBlock = myChain.getLastBlock()
    prevProof = prevBlock['proof']
    proof = myChain.proofOfWork(prevProof)
    prevHash = myChain.hash(prevBlock)
    myChain.addTransaction(node_address, 'Harish', 1)
    block = myChain.createBlock(proof, prevHash)
    response = {
        'status': 200,
        'message': 'Success',
        'index': block['index'],
        'timeStamp': block['timestamp'],
        'proof': block['proof'],
        'prevHash': block['prevHash'],
        'transactions': block['transaction']
    }

    return jsonify(response)


@app.route('/getMyChain', methods=['Get'])
def getChain():
    response = {
        'status': 200,
        'message': 'Success',
        'chain': myChain.chain,
        'length': len(myChain.chain)
    }
    return jsonify(response)


@app.route('/isChainValid', methods=['Get'])
def chainValid():
    response = {
        'status': 200,
        'message': 'Success',
        'chain': myChain.chain,
        'length': len(myChain.chain),
        'isValid': myChain.isChainValid(myChain.chain)
    }
    return jsonify(response)


@app.route('/addTransaction', methods=['POST'])
def addTransaction():
    json = request.get_json()
    transaction_keys = ['sender', 'reciever', 'amount']
    if not all (key in json for key in transaction_keys):
        return 'Some transaction parameters are missing', 400
    
    index = myChain.addTransaction(json['sender'], json['reciever'], json['amount'])
    response = {'message': f'Transaction in added as {index}', 'status': 200}
    return jsonify(response)


@app.route('/connectNode', methods=['POST'])
def connectNode():
    json = request.get_json()
    nodes = json['nodes']
    if nodes is None:
        return 'No Nodes', 400
    
    for node in nodes:
        myChain.addNode(node)

    response = {'message': "Done", 'total_nodes': list(myChain.nodes)}
    return jsonify(response)


@app.route('/replaceChain', methods=['Get'])
def replaceChain():
    is_chain_replaced = myChain.replace_chain()
    if is_chain_replaced:
        response = {
            'status': 200,
            'message': 'Your Chain is updated with largest one',
            'new_chain': myChain.chain,
            'length': len(myChain.chain)        }
    else:
        response = {
            'status': 200,
            'message': 'All Good, this chain is largest one',
            'chain': myChain.chain,
            'length': len(myChain.chain)        }
    return jsonify(response)


app.run('127.0.0.1', port=5000)