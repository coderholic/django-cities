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
    version='0.2',
    description='Place models and data for Django apps',
    author='Dan Carter (original by Ben Dowling)',
    author_email='carterd@gmail.com',
    url='https://github.com/Kometes/django-cities',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    long_description=read('README.md'),
    license = "MIT",
    keywords = "django cities countries regions postal codes geonames",
    classifiers = [
    "Development Status :: 3 - Alpha",
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

