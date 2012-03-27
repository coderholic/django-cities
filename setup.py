from setuptools import setup, find_packages
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='django-cities',
    version='0.19',
    description='Place models and data for Django apps',
    author='Ben Dowling',
    author_email='ben.m.dowling@gmail.com',
    url='https://github.com/coderholic/django-cities',
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

