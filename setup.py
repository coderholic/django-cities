from setuptools import setup, find_packages
import os
import os.path


# Utility function to read the README file.
# Used for the long_description. It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="django-cities-light",
    use_scm_version={
        "version_scheme": "post-release",
        "write_to": "src/cities_light/version.py",
    },
    setup_requires=["setuptools_scm"],
    description="Simple alternative to django-cities",
    author="James Pic,Dominick Rivard,Alexey Evseev",
    author_email="jamespic@gmail.com, dominick.rivard@gmail.com, myhappydo@gmail.com",
    url="https://github.com/yourlabs/django-cities-light",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    zip_safe=False,
    long_description=read("README.rst"),
    license="MIT",
    keywords="django cities countries postal codes",
    install_requires=[
        "pytz",
        "unidecode>=0.04.13",
        "django-autoslug>=1.9.8",
        "progressbar2>=3.51.4",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
