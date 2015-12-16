from __future__ import print_function

# bootstrap: download setuptools 3.3 if needed
from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

# get the version number and author list from package
from pySecDec import __version__, __authors__

setup(
    name='pySecDec',
    packages=find_packages(),
    version=__version__,
    author=__authors__,
    author_email='secdec@projects.hepforge.org',
    url='secdec.hepforge.org',
    description='An implementation of "Sector Decomposition" (see arXiv:0803.4177).',
    # long_description=long_description, #TODO: write an abstract of this package
    # license='GPLv2', # TODO: license
    install_requires=['numpy', 'sympy', 'setuptools>=3.3'],
    extras_require={'testing': ['nose']},
    classifiers=['Development Status :: 2 - Pre-Alpha',
                 'Intended Audience :: Science/Research',
                 'Operating System :: Unix',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Topic :: Scientific/Engineering :: Physics',
                 ],
    platforms=['any'],
    )