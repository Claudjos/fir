from setuptools import setup, find_packages
from os import path


this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


NAME = "pyfir"
VERSION = "0.0.3"

REQUIRES = []


setup(
    name=NAME,
    version=VERSION,
    description="Module to ease WSGI App testing.",
    author="Claudjos",
    author_email="claudjosmail@gmail.com",
    url="https://github.com/Claudjos/fir",
    keywords=["Web App", "Testing"],
    install_requires=REQUIRES,
    packages=find_packages(),
    package_data={},
    include_package_data=False,
    long_description_content_type='text/markdown',
    long_description=long_description
)
