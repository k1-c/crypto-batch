from functools import wraps
import hashlib
from hashlib import sha256
import re

import six

import os
import random
import codecs
import base58

if six.PY3:
    long = int


def ensure_bytes(data):
    if not isinstance(data, six.binary_type):
        return data.encode('utf-8')
    return data


def ensure_str(data):
    if isinstance(data, six.binary_type):
        return data.decode('utf-8')
    elif not isinstance(data, six.string_types):
        raise ValueError("Invalid value for string")
    return data


def chr_py2(num):
    """Ensures that python3's chr behavior matches python2."""
    if six.PY3:
        return bytes([num])
    return chr(num)


def hash160(data):
    """Return ripemd160(sha256(data))"""
    rh = hashlib.new('ripemd160', sha256(data).digest())
    return rh.digest()


def is_hex_string(string):
    """Check if the string is only composed of hex characters."""
    pattern = re.compile(r'[A-Fa-f0-9]+')
    if isinstance(string, six.binary_type):
        string = str(string)
    return pattern.match(string) is not None


def long_to_hex(l, size):
    """Encode a long value as a hex string, 0-padding to size.

    Note that size is the size of the resulting hex string. So, for a 32Byte
    long size should be 64 (two hex characters per byte"."""
    f_str = "{0:0%sx}" % size
    return ensure_bytes(f_str.format(l).lower())


def long_or_int(val, *args):
    return long(val, *args)


def memoize(f):
    """Memoization decorator for a function taking one or more arguments."""
    def _c(*args, **kwargs):
        if not hasattr(f, 'cache'):
            f.cache = dict()
        key = (args, tuple(kwargs))
        if key not in f.cache:
            f.cache[key] = f(*args, **kwargs)
        return f.cache[key]
    return wraps(f)(_c)


def bytes_to_str(b):
    """ Converts bytes into a hex-encoded string.
    Args:
        b (bytes): bytes to encode
    Returns:
        h (str): hex-encoded string corresponding to b.
    """
    return codecs.encode(b, 'hex_codec').decode('ascii')


def address_to_key_hash(s):
    """ Given a Bitcoin address decodes the version and
    RIPEMD-160 hash of the public key.
    Args:
        s (bytes): The Bitcoin address to decode
    Returns:
        (version, h160) (tuple): A tuple containing the version and
        RIPEMD-160 hash of the public key.
    """
    n = base58.b58decode_check(s)
    version = n[0]
    h160 = n[1:]
    return version, h160


def rand_bytes(n, secure=True):
    """ Returns n random bytes.
    Args:
        n (int): number of bytes to return.
        secure (bool): If True, uses os.urandom to generate
            cryptographically secure random bytes. Otherwise, uses
            random.randint() which generates pseudo-random numbers.
    Returns:
        b (bytes): n random bytes.
    """
    if secure:
        return os.urandom(n)
    else:
        return bytes([random.randint(0, 255) for i in range(n)])