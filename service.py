from hashlib import sha256
import json
import time
from flask import jsonify
from flask import Flask, request
import datetime
from flask_cors import CORS, cross_origin
import requests


app = Flask(__name__)
CORS(app, origins='*')

ADMIN_ID = "3520242040955"
class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce

    def compute_hash(self):
        """
        A function that return the hash of the block contents.
        """
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()

def saveData(chain,filename):

    data = []
    for i in chain:
        a = i.__dict__
        data.append(a)
    
    with open(filename,'w',encoding='utf-8') as file:
        json.dump(data,file,indent=4)



def initBlockchain():
    blockchain.create_genesis_block()


def loadData(blockchain,filename):
    with open(filename,'r',encoding='utf-8') as file:
        chain = json.loads(file.read())
    if len(chain) == 0:
        initBlockchain()
    else:
        for data in chain:
            # data = i.__dict__
            new_block = Block(index=data['index'],
                                transactions=data['transactions'],
                                timestamp=data['timestamp'],
                                previous_hash=data['previous_hash']
                                )
            new_block.nonce = data['nonce']
            new_block.hash = data['hash']
            blockchain.chain.append(new_block)
      #  print(blockchain.chain[0].__dict__)
    
class Blockchain:
    # difficulty of our PoW algorithm
    difficulty = 2

    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []

    def create_genesis_block(self):
        """
        A function to generate genesis block and appends it to
        the chain. The block has index 0, previous_hash as 0, and
        a valid hash.
        """
        genesis_block = Block(0, [], 0, "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)
        saveData(blockchain.chain,'data.json')

    @property
    def last_block(self):
        return self.chain[-1]

    def add_block(self, block, proof):
        """
        A function that adds the block to the chain after verification.
        Verification includes:
        * Checking if the proof is valid.
        * The previous_hash referred in the block and the hash of latest block
          in the chain match.
        """
        previous_hash = self.last_block.hash

        if previous_hash != block.previous_hash:
            return False

        if not Blockchain.is_valid_proof(block, proof):
            return False

        block.hash = proof
        self.chain.append(block)
        return True

    @staticmethod
    def proof_of_work(block):
        """
        Function that tries different values of nonce to get a hash
        that satisfies our difficulty criteria.
        """
        block.nonce = 0

        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()

        return computed_hash

    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    @classmethod
    def is_valid_proof(cls, block, block_hash):
        """
        Check if block_hash is valid hash of block and satisfies
        the difficulty criteria.
        """
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.compute_hash())

    @classmethod
    def check_chain_validity(cls, chain):
        result = True
        previous_hash = "0"

        for block in chain:
            block_hash = block.hash
            # remove the hash field to recompute the hash again
            # using `compute_hash` method.
            delattr(block, "hash")

            if not cls.is_valid_proof(block, block_hash) or \
                    previous_hash != block.previous_hash:
                result = False
                break

            block.hash, previous_hash = block_hash, block_hash

        return result

    def mine(self):
        """
        This function serves as an interface to add the pending
        transactions to the blockchain by adding them to the block
        and figuring out Proof Of Work.
        """
        if not self.unconfirmed_transactions:
            return False

        last_block = self.last_block

        new_block = Block(index=last_block.index + 1,
                          transactions=self.unconfirmed_transactions,
                          timestamp=time.time(),
                          previous_hash=last_block.hash)

        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        saveData(self.chain,'data.json')
        self.unconfirmed_transactions = []

        return True



app = Flask(__name__)

# the node's copy of blockchain
global blockchain 
blockchain = Blockchain()
loadData(blockchain,'data.json')
# the address to other participating members of the network
peers = set()




@app.route('/add_candidate', methods=['POST'])
@cross_origin(origin='*')
def add_candidate():
    data = request.get_json()
    required_fields = ["addedBy", "candidateId","candidateInfo","party","country","candidateFor"]
    for field in required_fields:
        if not data.get(field):
            return "Invalid transaction data", 404
    if data['addedBy'] == ADMIN_ID: #Address of admin
        tx_data = {} 
        tx_data['transaction type'] = "CANDIDATE_ADDITION"
        tx_data['Added by'] = data['addedBy']
        tx_data["timestamp"] = time.time() 
        tx_data['candidate id'] = data['candidateId']
        tx_data['country'] = data['country']
        tx_data['candidate info'] = data['candidateInfo']
        tx_data['candidate for'] = data['candidateFor']
        tx_data['party'] = data['party']
        blockchain.add_new_transaction(tx_data)
        saveData(blockchain.chain,'data.json')
        return "Success", 201
    saveData(blockchain.chain,'data.json')
    return "Failure", 500

@app.route('/candidates', methods=['GET'])
@cross_origin(origin='*')
def getCandidates():
    candidatesIds = []
    for i in blockchain.chain:
        for transaction in i.__dict__['transactions']:
            if transaction['transaction type'] == "CANDIDATE_ADDITION":
                candidate = {}
                candidate['id'] = transaction['candidate id']
                candidate['candidate info'] = transaction['candidate info']
                candidate['party'] = transaction['party']
                candidate['country'] = transaction['country']
                candidate['candidateFor'] = transaction['candidate for']
                candidatesIds.append(candidate)
    return candidatesIds,200


@app.route('/candidates_count', methods=['GET'])
@cross_origin(origin='*')
def getCandidatesCount():

    candidatesIds = []
    for i in blockchain.chain:
        for transaction in i.__dict__['transactions']:
            if transaction['transaction type'] == "CANDIDATE_ADDITION":
                candidate = {}
                candidate['id'] = transaction['candidate id']
                candidate['candidate info'] = transaction['candidate info']
                candidate['party'] = transaction['party']
                candidate['country'] = transaction['country']
                candidate['candidateFor'] = transaction['candidate for']
                candidatesIds.append(candidate)
    count=len(candidatesIds)
    return str(count)

@app.route('/delete_all_votes', methods=['DELETE'])
def delete_all_votes():
    deleted_votes_count = 0
    for block in blockchain.chain:
        for transaction in block.__dict__['transactions']:
            if transaction['transaction type'] == 'VOTE':
                # Remove the transaction from the block's transactions list
                block.__dict__['transactions'].remove(transaction)
                deleted_votes_count += 1
    
    return f'Successfully deleted {deleted_votes_count} votes.'

@app.route('/add_vote', methods=['POST'])
def add_vote():
    data = request.get_json()
    if  isVotePossible(data['votedBy'],data['compaignId']):
        tx_data = {}
        tx_data['transaction type'] = 'VOTE'
        tx_data['election compaign id'] = data['compaignId']
        tx_data['voted to'] = data.get('candidateId')
        tx_data['voted by'] = data['votedBy']
        blockchain.add_new_transaction(tx_data)
        return "Success"
    saveData(blockchain.chain,'data.json')
    return 'Failure '   
def isAlreadyVoted(voterId,compaignId):
    for block in blockchain.chain:
        for transaction in block.__dict__['transactions']:
            if transaction['transaction type'] == 'VOTE' and transaction['election compaign id'] == compaignId:
                if transaction['voted by'] == voterId:
                    return True
    return False
def isVotePossible(voterId,compaignId):
    if not(isAlreadyVoted(voterId,compaignId)):
        return True
    return False

def isElectionEnded(compaignId):
     for block in blockchain.chain:
        for transaction in block.__dict__['transactions']:
            if transaction['transaction type'] == 'ELECTION_COMPAIGN':
                if transaction['compaign id'] == compaignId:
                        return not(transaction['timestamp'] <= time.time() <= transaction['end time'])

@app.route('/election_campaigns_count', methods=['GET'])
@cross_origin(origin='*')
def get_election_campaigns_count():
    elections_count = sum(
        1 for block in blockchain.chain
        for transaction in block.transactions
        if 'transaction_type' in transaction and transaction['transaction_type'] == 'ELECTION_CAMPAIGN'
    )
    return str(elections_count)

@app.route('/candidate_vote_count', methods=['POST'])
def getVotesCount9():
    data = request.get_json()
    votes_count = 0
    for block in blockchain.chain:
        for transaction in block.__dict__['transactions']:
            if transaction['transaction type'] == 'VOTE':
                if transaction['voted to'] == data['candidateId']:
                    votes_count = votes_count + 1
    return str(votes_count)

@app.route('/vote_all_count', methods=['GET'])
@cross_origin(origin='*')
def getVotesAllCount():
    votes_count = 0
    for block in blockchain.chain:
        for transaction in block.__dict__['transactions']:
            if transaction['transaction type'] == 'VOTE':
                votes_count = votes_count + 1
    return str(votes_count)


@app.route('/vote_casted', methods=['POST'])
def getTotalVoteCount():
    data = request.get_json()
    votes_count = 0
    for block in blockchain.chain:
        for transaction in block.__dict__['transactions']:
            if transaction['transaction type'] == 'VOTE':
                if transaction['election compaign id'] == data['compaignId']:
                    votes_count = votes_count + 1
    return {'vote count':votes_count}

@app.route('/election_compaigns', methods=['GET'])
@cross_origin(origin='*')
def getVotesCount1():
    elections = []
    for block in blockchain.chain:
        for transaction in block.__dict__['transactions']:
            if transaction['transaction type'] == 'ELECTION_COMPAIGN':
                record = {}
                record['createdBy'] = transaction['createdBy']
                record['compaign id'] = transaction['compaign id']
                record['candidates ids'] = transaction['candidates ids']
                record['election info'] = transaction['election info']
                record['start Date'] = transaction['start Date']
                record['end Date'] = transaction['end Date']
                elections.append(record)
    return {'Elections Compaigns':elections}        


@app.route('/remove_election_compaigns', methods=['GET'])
def removeElectionCampaigns():
    removed_campaigns = []
    for block in blockchain.chain:
        removed_transactions = [t for t in block.__dict__['transactions'] if t['transaction type'] == 'ELECTION_COMPAIGN']
        removed_campaigns.extend(removed_transactions)        
        block.__dict__['transactions'] = [t for t in block.__dict__['transactions'] if t['transaction type'] != 'ELECTION_COMPAIGN']
    return {'Removed Election Campaigns': removed_campaigns}




@app.route('/add_election_compaign', methods=['POST'])
def addElectionCompaign():
    data = request.get_json()
    if  data['createdBy'] == ADMIN_ID: #Address of admin
        tx_data = {}
        tx_data['transaction type'] = "ELECTION_COMPAIGN"
        tx_data['createdBy'] = data['createdBy']
        tx_data['compaign id'] = getTotalCompaigns() + 1
        tx_data['start Date'] = "Today"
        tx_data['candidates ids'] = data['candidates']
        tx_data['end Date'] = data['endTime']
        tx_data['election info'] = data['electionInfo']
        blockchain.add_new_transaction(tx_data)
        return "Success"
    return "Failure"

def getTotalCompaigns():
    no_of_compaigns = 0
    for block in blockchain.chain:
        for transaction in block.__dict__['transactions']:
            if transaction['transaction type'] == 'ELECTION_COMPAIGN':
                no_of_compaigns = no_of_compaigns + 1

    return no_of_compaigns



# endpoint to return the node's copy of the chain.
# Our application will be using this endpoint to query
# all the posts to display.
@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data),
                       "chain": chain_data,
                       "peers": list(peers)})


# endpoint to request the node to mine the unconfirmed
# transactions (if any). We'll be using it to initiate
# a command to mine from our application itself.
@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if not result:
        return "No transactions to mine"
    else:
        # Making sure we have the longest chain before announcing to the network
        chain_length = len(blockchain.chain)
        consensus()
        if chain_length == len(blockchain.chain):
            # announce the recently mined block to the network
            announce_new_block(blockchain.last_block)
        return "Block #{} is mined.".format(blockchain.last_block.index)


# endpoint to add new peers to the network.
@app.route('/register_node', methods=['POST'])
def register_new_peers():
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    # Add the node to the peer list
    peers.add(node_address)

    # Return the consensus blockchain to the newly registered node
    # so that he can sync
    return get_chain()


@app.route('/register_with', methods=['POST'])
def register_with_existing_node():
    """
    Internally calls the `register_node` endpoint to
    register current node with the node specified in the
    request, and sync the blockchain as well as peer data.
    """
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    data = {"node_address": request.host_url}
    headers = {'Content-Type': "application/json"}

    # Make a request to register with remote node and obtain information
    response = requests.post(node_address + "/register_node",
                             data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        global blockchain
        global peers
        # update chain and the peers
        chain_dump = response.json()['chain']
        blockchain = create_chain_from_dump(chain_dump)
        peers.update(response.json()['peers'])
        return "Registration successful", 200
    else:
        # if something goes wrong, pass it on to the API response
        return response.content, response.status_code


def create_chain_from_dump(chain_dump):
    generated_blockchain = Blockchain()
    generated_blockchain.create_genesis_block()
    for idx, block_data in enumerate(chain_dump):
        if idx == 0:
            continue  # skip genesis block
        block = Block(block_data["index"],
                      block_data["transactions"],
                      block_data["timestamp"],
                      block_data["previous_hash"],
                      block_data["nonce"])
        proof = block_data['hash']
        added = generated_blockchain.add_block(block, proof)
        if not added:
            raise Exception("The chain dump is tampered!!")
    return generated_blockchain


# endpoint to add a block mined by someone else to
# the node's chain. The block is first verified by the node
# and then added to the chain.
@app.route('/add_block', methods=['POST'])
def verify_and_add_block():
    block_data = request.get_json()
    block = Block(block_data["index"],
                  block_data["transactions"],
                  block_data["timestamp"],
                  block_data["previous_hash"],
                  block_data["nonce"])

    proof = block_data['hash']
    added = blockchain.add_block(block, proof)

    if not added:
        return "The block was discarded by the node", 400

    return "Block added to the chain", 201


#unconfirmed transactions
@app.route('/pending_tx')
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)


def consensus():
    
    #If a longer valid chain is found, our chain is replaced with it.

    global blockchain

    longest_chain = None
    current_len = len(blockchain.chain)

    for node in peers:
        response = requests.get('{}chain'.format(node))
        length = response.json()['length']
        chain = response.json()['chain']
        if length > current_len and blockchain.check_chain_validity(chain):
            current_len = length
            longest_chain = chain

    if longest_chain:
        blockchain = longest_chain
        return True

    return False


def announce_new_block(block):
    for peer in peers:
        url = "{}add_block".format(peer)
        headers = {'Content-Type': "application/json"}
        requests.post(url,
                      data=json.dumps(block.__dict__, sort_keys=True),
                      headers=headers)

if __name__ == '__main__':
    app.run(debug=True)