"""Core package"""
import dgl

__all__ = ['say_hello']

def say_hello(name):
    """Say hello to every one.

    Parameters
    ----------
    name : str
        Who

    Returns
    -------
    bool
        Succeed or not.
    """
    print('DGL version: {}'.format(dgl.__version__))
    print('{}: Heeeeeeeeeeeeeeeeeello!'.format(name))
    return True
