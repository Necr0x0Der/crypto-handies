from getpass import getuser, getpass
from crypto_handies import Mnemorator
from crypto_handies import HDMnemo
from crypto_handies import HDKeyRing

# We use the user name as a password that encrypts the pairs
# {name: encrypted_data}. If names are secret, one may use
# a stronger password. Here, it is used just for the whole
# file to be a sequence of nameless bytes.
kr = HDKeyRing('myfile.enc', getuser())
# Use different set of words for a real wallet
mnemo = Mnemorator().random_from_words('gate clump ball normal any oak tourist evil detail awful snack clap')
hdw = HDMnemo.from_mnemonic(mnemo)
# Printting just for demonstration purposes
print(hdw)
# You will be prompted for a password,
# and the file will be created
kr.set_hdentry('first-wallet', hdw, "just a random wallet")

# Now we read this file and try to decode
print("Enter the same password for decoding:")
krc = HDKeyRing('myfile.enc', getuser())
data = krc.get_entry('first-wallet')
print(data['address'])
assert data['address'] == hdw.address()
