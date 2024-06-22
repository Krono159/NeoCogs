#
# Copyright (c) 2013, Prometheus Research, LLC
# Released under MIT license, see `LICENSE` for details.
#

from setuptools import setup, find_namespace_packages

NAME = "Cogs"
VERSION = "0.4.5a0"
DESCRIPTION = """Toolkit for developing command-line utilities in Python"""
with open('README', 'r') as f:
    LONG_DESCRIPTION = f.read()
AUTHOR = """Kirill Simonov (Prometheus Research, LLC), Rework by Luis S. (MoccaDev)"""
AUTHOR_EMAIL = "krono159@proton.me"
LICENSE = "MIT"
URL = "pending"
DOWNLOAD_URL = "http://pypi.python.org/pypi/Cogs"
CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: MIT License",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Topic :: Utilities",
]
PACKAGES = find_namespace_packages(where='src')
PACKAGE_DIR = {'': 'src'}
INSTALL_REQUIRES = ['setuptools', 'PyYAML']
ENTRY_POINTS = {
    'console_scripts': [
        'cogs = cogs.run:main',
    ],
    'cogs.extensions': [],
}

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENSE,
    url=URL,
    download_url=DOWNLOAD_URL,
    classifiers=CLASSIFIERS,
    packages=PACKAGES,
    package_dir=PACKAGE_DIR,
    install_requires=INSTALL_REQUIRES,
    entry_points=ENTRY_POINTS,
)
