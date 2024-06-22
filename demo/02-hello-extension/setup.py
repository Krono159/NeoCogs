from setuptools import setup

setup(
    name='neocogs-Hello',
    version='0.1',
    description="""A NeoCogs task to greet somebody""",
    packages=['neocogs.hello'],
    package_dir={'': 'src'},
    install_requires=['NeoCogs'],
    entry_points={ 'NeoCogs.extensions': ['Hello = neocogs.hello'] },
)
