from brownie import web3
from brownie.network.account import PublicKeyAccount
import csv
import json
from pathlib import Path
import time
from itertools import zip_longest
from eth_abi.packed import encode_abi_packed
from eth_utils import encode_hex


class MerkleTree:
    def __init__(self, elements):
        self.elements = sorted(set(web3.keccak(hexstr=el) for el in elements))
        self.layers = MerkleTree.get_layers(self.elements)

    @property
    def root(self):
        return self.layers[-1][0]

    def get_proof(self, el):
        el = web3.keccak(hexstr=el)
        idx = self.elements.index(el)
        proof = []
        for layer in self.layers:
            pair_idx = idx + 1 if idx % 2 == 0 else idx - 1
            if pair_idx < len(layer):
                proof.append(encode_hex(layer[pair_idx]))
            idx //= 2
        return proof

    @staticmethod
    def get_layers(elements):
        layers = [elements]
        while len(layers[-1]) > 1:
            layers.append(MerkleTree.get_next_layer(layers[-1]))
        return layers

    @staticmethod
    def get_next_layer(elements):
        return [MerkleTree.combined_hash(a, b) for a, b in zip_longest(elements[::2], elements[1::2])]

    @staticmethod
    def combined_hash(a, b):
        if a is None:
            return b
        if b is None:
            return a
        return web3.keccak(b''.join(sorted([a, b])))


def get_proof(balances):
    elements = [(index, account, balances[account]) for index, account in enumerate(sorted(balances))]
    nodes = [encode_hex(encode_abi_packed(['uint', 'address', 'uint'], el)) for el in elements]
    tree = MerkleTree(nodes)
    distribution = {
        'merkleRoot': encode_hex(tree.root),
        'tokenTotal': sum(balances.values()),
        'claims': {
            user: {'index': index, 'amount': amount, 'proof': tree.get_proof(nodes[index])}
            for index, user, amount in elements
        },
    }
    print(f'merkle root: {encode_hex(tree.root)}')
    return distribution


def main():
    allocations = {}
    with Path("allocations.csv").open() as fp:
        reader = csv.reader(fp)
        for address, amount in reader:
            try:
                address = PublicKeyAccount(address.strip()).address
            except ValueError:
                print(f"Warning: skipping invalid address '{address}'")
                continue
            if address in allocations:
                raise ValueError(address)
            allocations[address] = int(amount.replace(',', '')) * 10**18

    distribution = get_proof(allocations)

    date = time.strftime("%Y-%m-%d", time.gmtime())
    distro_json = Path(f'distribution-{date}.json')

    with distro_json.open('w') as fp:
        json.dump(distribution, fp)

    print("total airdrop: ", sum(int(i['amount'], 16) for i in distribution['claims'].values()))
    print(f"Distribution saved to {distro_json}")
