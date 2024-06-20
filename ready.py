from typing import List
import hashlib
import json
import time

class Transaction:
  def __init__(self, sender, recipient, amount):
    self.sender = sender
    self.recipient = recipient
    self.amount = amount

class Block:
  def __init__(self, index, previous_hash, transactions, timestamp=None):
    self.index = index
    self.previous_hash = previous_hash
    self.timestamp = timestamp or time.time()
    self.transactions = transactions
    self.nonce = 0
    self.hash = self.calculate_hash()

  def calculate_hash(self):
    data = {
        "index": self.index,
        "previous_hash": self.previous_hash,
        "timestamp": self.timestamp,
        "transactions": [vars(txn) for txn in self.transactions],
        "nonce": self.nonce
    }
    data_json = json.dumps(data, sort_keys=True).encode('utf-8')
    return hashlib.sha256(data_json).hexdigest()

class Blockchain:
  def __init__(self):
    self.chain = [self.create_genesis_block()]

  def create_genesis_block(self):
    return Block(0, "0", [], 1632535482.903651)

  def get_last_block(self):
    return self.chain[-1]

  def add_block(self, new_block):
    new_block.previous_hash = self.get_last_block().hash
    new_block.hash = new_block.calculate_hash()
    self.chain.append(new_block)

  def validate_block(self, block):
    # Check if the block has a valid hash
    if block.previous_hash != self.get_last_block().hash:
      return False
    
    # Check if the block has a valid hash
    if block.hash != block.calculate_hash():
      return False

    # Check if all transactions in the block are valid
    for transaction in block.transactions:
      if not self.validate_transaction(transaction):
        return False

    # Check if the block has a valid timestamp
    if block.timestamp < self.get_last_block().timestamp:
      return False

    # If all checks pass, the block is valid
    return True

  def handle_transaction(self, transaction):
    # Check if the transaction is valid
    if not self.validate_transaction(transaction):
      return False

    # If the transaction is valid, add it to the next block
    next_block = Block(len(self.chain), self.get_last_block().hash, [transaction])
    self.add_block(next_block)
    return True

  def validate_transaction(self, transaction):
    # Check if the transaction has a valid sender
    if transaction.sender not in self.get_all_addresses():
      return False

    # Check if the transaction has a valid recipient
    if transaction.recipient not in self.get_all_addresses():
      return False
    
    # Check if the transaction has a valid amount
    if transaction.amount < 0:
      return False

    # If all checks pass, the transaction is valid
    return True

  def get_all_addresses(self):
      addresses = set()
      for block in self.chain:
          for transaction in block.transactions:
              addresses.add(transaction.sender)
              addresses.add(transaction.recipient)

      return addresses

  def __iter__(self):
      # Make the Blockchain object iterable by returning an iterator
      return iter(self.chain)


# This function is used to validate a block before it is added to the blockchain
def validate_new_block(block, Blockchain):
  # Check if the block has a valid previous hash
    if block.previous_hash != Blockchain.get_last_block().hash:
        return False

    # Check if the block has a valid hash
    if block.hash != block.calculate_hash():
        return False

    # Check if all transactions in the block are valid
    for transaction in block.transactions:
        if not Blockchain.validate_transaction(transaction):
            return False

    # Check if the block has a valid timestamp
    if block.timestamp < Blockchain.get_last_block().timestamp:
        return False

    # If all checks pass, the block is valid
    return True

# This function can be used to handle a new transaction
def handle_new_transaction(transaction, Blockchain):
    return Blockchain.handle_transaction(transaction)

# Binary Merkle Tree )
class Node:
  def __init__(self, left, right, block:Block, is_copied = False) -> None:
    self.left: Node = left
    self.right: Node = right
    self.block: Block = block
    self.is_copied = is_copied

  @staticmethod
  def hash(val: str):
    return hashlib.sha256(val.encode('utf-8')).hexdigest()

  def copy(self):
    return Node(self.left, self.right, self.block, True)

class MerkleTree:
  def __init__(self, values : List[Block] ):
    self.BuildTree(values)

  def BuildTree(self, values: List[Block] ):
    leaves : List[Node] = [Node(None, None, e) for e in values]
    if len(leaves) % 2 == 1:
      leaves.append(Node.copy(leaves[-1]))
    self.root : Node = self.__BuildTreeRec(leaves)

  def __BuildTreeRec(self, nodes: List[Node]) -> Node:
    if len(nodes) %2 ==1:
      nodes.append(nodes[-1].copy)
    half : int = len(nodes) //2

    if len(nodes) == 2:
      new_block = Block([nodes[0].block.index, nodes[1].block.index], Node.hash(nodes[0].block.previous_hash + nodes[1].block.previous_hash), nodes[0].block.transactions + nodes[1].block.transactions, None)
      return Node(nodes[0], nodes[1], new_block)

    left: Node = self.__BuildTreeRec(nodes[:half])
    right: Node = self.__BuildTreeRec(nodes[half:])
    new_block = Block(left.block.index + right.block.index, Node.hash(left.block.previous_hash + right.block.previous_hash), left.block.transactions + right.block.transactions, None)
    return Node(left, right, new_block)

  def printTree(self) -> None:
    self.__printTreeRec(self.root)

  def __printTreeRec(self, node: Node) -> None:
    if node != None:
      if node.left != None:
        print("Left: "+str(node.left.block.previous_hash))
        print("Right: "+str(node.right.block.previous_hash))
      else :
        print("Leaf")
      if node.is_copied:
        print('(Padding)')
      # print("Block:")
      print("Index:"+str(node.block.index))
      print("hash:"+str(node.block.previous_hash))
      print("transactions:")
      for txn in node.block.transactions:
        print(f"  Sender: {txn.sender}, Recipient: {txn.recipient}, Amount: {txn.amount}")
      print()
      self.__printTreeRec(node.left)
      self.__printTreeRec(node.right)

  def getRootHash(self)-> str:
    return self.root.value

# Initialize the blockchain
my_blockchain = Blockchain()

# Console User Interface
mtree = MerkleTree(my_blockchain)
while True:
    print("\nBlockchain Menu:")
    print("1. Add Transaction")
    print("2. View Blockchain")
    print("3. Exit")
    choice = input("Enter your choice: ")
    if choice == "1":
        sender = input("Enter sender: ")
        recipient = input("Enter recipient: ")
        amount = float(input("Enter amount: "))
        transaction = Transaction(sender, recipient, amount)
        transaction_pool = [transaction]
        new_block = Block(len(my_blockchain.chain), my_blockchain.get_last_block().hash, transaction_pool)
        my_blockchain.add_block(new_block)
        mtree = MerkleTree(my_blockchain)
        print(f"Transaction added to the blockchain.")

    elif choice == "2":
      mtree.printTree()
      print()
      for block in my_blockchain.chain:
          print()
          print(f"Block {block.index}")
          print(f"Hash: {block.hash}")
          print(f"Previous Hash: {block.previous_hash}")
          print(f"Timestamp: {block.timestamp}")
          print("Transactions:")
          for txn in block.transactions:
              print(f"  Sender: {txn.sender}, Recipient: {txn.recipient}, Amount: {txn.amount}")
          print()
    elif choice == "3":
      print("Exiting the Blockchain program.")
      break

    else:
        print("Invalid choice. Please enter a valid option.")