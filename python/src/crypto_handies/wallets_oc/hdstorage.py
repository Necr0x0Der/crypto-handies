from getpass import getpass
import hashlib
import base64
import json
from cryptography.fernet import Fernet, InvalidToken
from os.path import isfile


class HDKeyRing:
    '''
    This is a simple storage, each item of which can be encrypted
    with its own password in addition to encryption of the whole content.
    The main purpose is to keep wallets encrypted with protected access
    to them. Any data can be kept in it, though.
    '''
    def __init__(self, fname: str, file_password: str = None):
        self.fname = fname
        self.entries = {}
        self.file_password = file_password
        if isfile(fname):
            with open(fname, 'rb') as fr:
                if file_password is None:
                    file_password = getpass()
                data = fr.read()
                self.entries = json.loads(self._decrypt(file_password, data))

    def new_password(self):
        p1 = getpass()
        print("==== Retype ====")
        p2 = getpass()
        return None if p1 != p2 else p1

    def get_entries(self):
        return self.entries.keys()

    def get_entry(self, name, password=None):
        if password is None:
            password = getpass()
        return json.loads(self._decrypt(password, self.entries[name]))

    def _password_to_key_base64(self, password: str, salt: bytes = b'some_salt', iterations: int = 100000) -> str:
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations, dklen=32)
        return base64.urlsafe_b64encode(key).decode('utf-8')

    def _encrypt(self, password, jdata):
        b = json.dumps(jdata).encode('utf-8')
        if password == '':
            return b
        f = Fernet(self._password_to_key_base64(password))
        return f.encrypt(b)

    def _decrypt(self, password, data):
        try:
            if password != '':
                f = Fernet(self._password_to_key_base64(password))
                data = f.decrypt(data)
                return data.decode('utf-8')
            else:
                return data
        except InvalidToken as e:
            print("Wrong password")
            return "{}"

    def set_entry(self, name, data):
        print("Encode the entry:")
        p = self.new_password()
        if p is None:
            print("Passwords don't match. Data is not saved")
            return
        self.entries[name] = self._encrypt(p, data).decode('utf-8')
        with open(self.fname, 'wb') as fw:
            pf = self.file_password
            if pf is None:
                print("Encode the file:")
                pf = self.new_password()
                if pf is None:
                    print("Passwords don't match. Data is not saved")
                    return
            fw.write(self._encrypt(pf, self.entries))

    def set_hdentry(self, name, hdw, comment=""):
        self.set_entry(name,
            {
                'mnemonic': hdw.mnemonic(),
                'address': hdw.address(),
                'private-key': hdw.private_key(),
                'public-key': hdw.public_key(),
                'comment': comment
            }
        )

