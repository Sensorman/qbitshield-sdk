from setuptools import setup, find_packages

setup(
    name='qbitshield',
    version='0.1.0',
    description='Quantum-safe key generation SDK using Prime Harmonic Modulation',
    author='Will Daoud',
    author_email='will@qbitshield.com',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
