import os
from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='garjobsubmaker',
    version='0.1.0',
    description='Python tool to generate ND-GAr jobsub commands',
    long_description=readme,
    author='Francisco Martínez López',
    author_email='f.martinezlopez@qmul.ac.uk',
    url='https://github.com/fmartinezlopez/GArJobSubMaker',
    license=license,
    packages=find_packages(exclude=('scripts')),
    package_data={'': ['LICENSE']},
    include_package_data=True
)