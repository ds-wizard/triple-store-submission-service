from setuptools import setup, find_packages
import os

from triple_store_submitter import __version__, __package_name__

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = ''.join(f.readlines())

setup(
    name=__package_name__,
    version=__version__,
    keywords='dsw submission document triple-store',
    description='Submission service for storing data from DSW to Triple Stores',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Marek Suchánek',
    author_email='suchama4@fit.cvut.cz',
    license='Apache2',
    packages=find_packages(),
    install_requires=[
        'aiohttp',
        'PyYAML',
        'rdflib',
        'requests',
        'SPARQLWrapper',
    ],
    classifiers=[
        'Framework :: AsyncIO',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
    ],
)
