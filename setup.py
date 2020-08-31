from setuptools import setup
import os
import os.path


# Utility function to read the README file.
# Used for the long_description. It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='django-cities-light',
    version='3.7.0',
    description='Simple alternative to django-cities',
    author='James Pic,Dominick Rivard,Alexey Evseev',
    author_email='jamespic@gmail.com, dominick.rivard@gmail.com, myhappydo@gmail.com',
    url='https://github.com/yourlabs/django-cities-light',
    packages=['cities_light'],
    include_package_data=True,
    zip_safe=False,
    long_description=read('README.rst'),
    license='MIT',
    keywords='django cities countries postal codes',
    install_requires=[
        'pytz',
        'unidecode>=0.04.13',
        'django-autoslug>=1.9.8',
        'progressbar2>=3.51.4'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
