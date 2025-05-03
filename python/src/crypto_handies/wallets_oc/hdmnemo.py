# NOTE: hdwallet can be used instead.
#       This implementation is only for speedup and transparency.

import hashlib
import hmac
import struct
import binascii
from ecdsa import SECP256k1
from eth_utils import to_checksum_address, keccak


BIP39_PBKDF2_ROUNDS = 2048
BIP39_SALT_MODIFIER = "mnemonic"
BIP32_PRIVDEV = 0x80000000
BIP32_SEED_MODIFIER = b'Bitcoin seed'
BIP32_CURVE = SECP256k1


class DerivationPath:
    '''
    Derivation path to 
    Typical derivation path is "m/44'/60'/0'/0/0", which means
        m / purpose' / coin_type' / account' / change / address_index
        ' means that BIP32_PRIVDEV should be added
    '''
    def __init__(self, path_str):
        assert path_str[:2] == 'm/', "Not a valid derivation path"
        self.path = [int(v[:-1]) + BIP32_PRIVDEV if "'" in v else int(v) \
                     for v in path_str[2:].split('/')]

    @classmethod
    def Eth(cls, idx=0):
        return cls(f"m/44'/60'/0'/0/{idx}")

    def __iter__(self):
        return iter(self.path)

    def __repr__(self):
        names = ['purpose', 'coin_type', 'account', 'change', 'address_index']
        return '\n'.join(f'{names[i]}: {self.path[i]}' for i in range(len(self.path)))


class HDMnemo:
    '''
    Light-weight and Ethereum compatible, but limited implementation of
    Hierarchical Deterministic (HD) Wallet from BIP39.
    
    Useful for faster conversion from mnemonics to keys.
    
    From compact code, it's also easier to see that your mnemonics
    are not sent anywhere.
    '''
    def __init__(self, private_key, mnemo=None):
        assert len(private_key) == 32, "Private key length should be 32"
        self._private_key = private_key
        self._point = int.from_bytes(private_key, byteorder='big') * BIP32_CURVE.generator
        self._mnemo = mnemo

    @classmethod
    def from_mnemonic(cls, words, deriv_path=DerivationPath.Eth(), passphrase=""):
        if isinstance(words, list):
            words = ' '.join(words)
        # convert mnemonic -> bip39 seed
        mnemonic = bytes(words, 'utf8')
        salt = bytes(BIP39_SALT_MODIFIER + passphrase, 'utf8')
        seed = hashlib.pbkdf2_hmac('sha512', mnemonic, salt, BIP39_PBKDF2_ROUNDS)
        # bip39 seed -> bip32 master node
        seed_hash = hmac.new(BIP32_SEED_MODIFIER, seed, hashlib.sha512).digest()
        chain_code = seed_hash[32:]
        wallet = cls(private_key=seed_hash[:32], mnemo=words)
        for piece in deriv_path:
            child_key, chain_code = wallet._derive_childkey(chain_code, piece)
            wallet = cls(child_key, mnemo=words)
        return wallet

    def _derive_childkey(self, parent_chain_code, i):
        assert len(parent_chain_code) == 32
        k = parent_chain_code
        if (i & BIP32_PRIVDEV) != 0:
            key = b'\x00' + self._private_key
        else:
            key = bytes(self)
        d = key + struct.pack('>L', i)
        while True:
            h = hmac.new(k, d, hashlib.sha512).digest()
            key, chain_code = h[:32], h[32:]
            a = int.from_bytes(key, byteorder='big')
            b = int.from_bytes(self._private_key, byteorder='big')
            key = (a + b) % BIP32_CURVE.order
            if a < BIP32_CURVE.order and key != 0:
                key = key.to_bytes(32, byteorder='big')
                break
            d = b'\x01' + h[32:] + struct.pack('>L', i)
        return key, chain_code

    def __bytes__(self):
        xstr = self._point.x().to_bytes(32, byteorder='big')
        parity = self._point.y() & 1
        return (2 + parity).to_bytes(1, byteorder='big') + xstr

    def address(self):
        x = self._point.x()
        y = self._point.y()
        s = x.to_bytes(32, 'big') + y.to_bytes(32, 'big')
        return to_checksum_address(keccak(s)[12:])

    def private_key(self):
        return binascii.hexlify(self._private_key).decode("utf-8")

    def public_key(self):
        return binascii.hexlify(bytes(self)).decode("utf-8")

    def mnemonic(self):
        return self._mnemo
