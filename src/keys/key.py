# key.py

from base64 import b64decode, b64encode

import rsa
from rsa import PrivateKey, PublicKey, VerificationError


def licence_key(window):
    try:
        with open(window.settings.value("priv_key"), "rb") as file:
            priv_key = PrivateKey.load_pkcs1(file.read())
    except (OSError, ValueError) as err:
        print(err)
        raise
    else:
        licence = rsa.sign(window.edit_user.text().encode(), priv_key, "SHA-256")
        return b64encode(licence).decode()


def new_keys(dialog):
    pub_key, priv_key = rsa.newkeys(512)

    try:
        with open(dialog.button_pub_key.text(), "wb") as file:
            file.write(pub_key.save_pkcs1())
    except OSError as err:
        print(err)
        raise

    try:
        with open(dialog.button_priv_key.text(), "wb") as file:
            file.write(priv_key.save_pkcs1())
    except OSError as err:
        print(err)
        raise


def valid(user, licence_key, pub_key):
    try:
        with open(pub_key, "rb") as file:
            pub_key = PublicKey.load_pkcs1(file.read())
    except OSError as err:
        print(err)
        raise

    try:
        rsa.verify(user.encode(), b64decode(licence_key), pub_key)
    except VerificationError:
        return False
    else:
        return True
