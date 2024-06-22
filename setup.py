from setuptools import setup, find_namespace_packages

NAME = "NeoCogs"
VERSION = "0.4.5a1"
DESCRIPTION = "Toolkit for developing command-line utilities in Python"
with open('README', 'r') as f:
    LONG_DESCRIPTION = f.read()
AUTHOR = "Kirill Simonov (Prometheus Research, LLC), Rework by Luis S. (MoccaDev)"
AUTHOR_EMAIL = "krono159@proton.me"
LICENSE = "MIT"
URL = "https://github.com/Krono159/NeoCogs"  
DOWNLOAD_URL = "http://pypi.python.org/pypi/NeoCogs"
CLASSIFIERS = [
    "Development Status :: 2 - Pre-Alpha",
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
        'neocogs = neocogs.run:main',
    ],
    'neocogs.extensions': [],
}

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',  
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
