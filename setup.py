from setuptools import setup, find_packages
import os

# Utility function to read the README file.
# Used for the long_description. It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='django-cities',
    version='0.4.1',
    description='Place models and worldwide place data for Django',
    author='Ben Dowling',
    author_email='ben.m.dowling@gmail.com',
    url='https://github.com/coderholic/django-cities',
    packages=find_packages(exclude=['example']),
    include_package_data=True,
    zip_safe=False,
    long_description=read('README.md'),
    license = "MIT",
    keywords = "django cities countries regions postal codes geonames",
    classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: Web Environment",
    "Framework :: Django",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)

