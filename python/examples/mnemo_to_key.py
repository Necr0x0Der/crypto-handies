from crypto_handies import Mnemorator
from crypto_handies import HDMnemo
# hdwallet option
from hdwallet import HDWallet
from hdwallet.mnemonics import BIP39Mnemonic
from hdwallet.cryptocurrencies import Ethereum

from random import randint

m = Mnemorator()

print("\n========== words starting with 'a', FFFF in address ==========")
words = m.mnemo.wordlist[:12]
words[-2] = '?'
words[2] = '?'
for r in m.fill_words(words, max_count=3000):
    hdmnemo = HDMnemo.from_mnemonic(r)
    if 'FFFF' in hdmnemo.address().upper():
        print(r, ' : ', hdmnemo.address())
        # One can definitely use HDWallet with much more features,
        # but it is slower for enumeration purposes.
        # Here, we just check that the result is the same.
        hdwallet = HDWallet(cryptocurrency=Ethereum).from_mnemonic(mnemonic=BIP39Mnemonic(r))
        assert hdwallet.address() == hdmnemo.address()

print("\n========== Address fitting - not for malicious use! ==========")
# Imagine that you forget a few words from your mnemonics, but
# remember/have first two and last two symbols from your address
ground_truth = [m.mnemo.wordlist[randint(0, 100)] for _ in range(12)]
ground_truth = list(m.shuffle_words(ground_truth, max_out=1))[0]
addr = HDMnemo.from_mnemonic(ground_truth).address()
print("Origin: ", addr) # just a random address
words = ground_truth.split(' ')
words[1] = words[9] = '?' # erasing two words
# let's try to restore the address
for r in m.fill_words(words, max_count=40000):
    hdmnemo = HDMnemo.from_mnemonic(r)
    addr_m = hdmnemo.address()
    if addr_m[2:4] == addr[2:4] and addr_m[-2:] == addr[-2:]:
        print('Found : ', addr_m)
        break
