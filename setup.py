import sys

from setuptools import setup, find_packages


deps = ["distribute", "PyYaml", "voluptuous"]


if sys.version_info[:2] == (2, 6):
    deps.append('argparse')


setup(
    name='toxer',
    version='0.1.0',
    packages=find_packages(exclude=("test.*",)),

    entry_points={
        'console_scripts': [
            'toxer = toxer:main',
            'toxer-build = toxer:build_images',
        ],
    },

    url='',
    license='MIT',
    author='Aleksandr Rudakov',
    author_email='ribozz@gmail.com',
    description='Run your tox tests inside docker with different linux distributions.',
    long_description=open('README.md').read(),
    install_requires=deps,

    # cmdclass={'test': PyTest},

    extras_require={
        'dev': ['pytest', 'coverage', 'pytest-cov', 'mock'],
        'travis': ['coveralls'],
        'docs': ['sphinx==1.2b3', 'sphinx-argparse']
    }
)
