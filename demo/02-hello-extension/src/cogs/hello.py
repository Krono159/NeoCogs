from neocogs import task
import os

@task
def Hello(name=None):
    """greet someone (if not specified, the current user)"""
    if name is None:
        name = os.environ.get('USER', 'User') 
    print("Hello, %s!" % name.capitalize())
