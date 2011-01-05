from setuptools import setup, find_packages

setup(name='cities',
      version='0.1',
      description='Django Cities',
      author='Ben Dowling',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      )