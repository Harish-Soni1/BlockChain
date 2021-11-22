import datetime
import hashlib
import json
from flask import Flask, jsonify

class BlockChain:

    def __init__(self) -> None:
        self.chain = []
        self.createBlock(proof = 1, prevHash = '0')

    def createBlock(self, proof, prevHash):
        block = {
            'index': len(self.chain)+1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'prevHash': prevHash
        }
        self.chain.append(block)
        return block

    def getLastBlock(self):
        return self.chain[-1]

    def proofOfWork(self, prevProof):
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

    def isChainValid(self, chain):
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


app = Flask(__name__)
myChain = BlockChain()

@app.route("/mineChain", methods=['Get'])
def mineBlock():
    prevBlock = myChain.getLastBlock()
    prevProof = prevBlock['proof']
    proof = myChain.proofOfWork(prevProof)
    prevHash = myChain.hash(prevBlock)
    block = myChain.createBlock(proof, prevHash)
    response = {
        'status': 200,
        'message': 'Success',
        'index': block['index'],
        'timeStamp': block['timestamp'],
        'proof': block['proof'],
        'prevHash': block['prevHash']
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

app.run()