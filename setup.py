#!/usr/bin/env python

from setuptools import setup


if __name__ == '__main__':
    setup(
        name='ExperienceTracker',
        version='0.0.0',
        description='Archive execution data to a database for posterity',
        author='Pierre Delaunay',
        packages=['experience_tracker'],
        install_requires=[
          'flask'
        ],
        entry_points={
            'console_scripts': [
                'exp-tracker = experience_tracker.tracker:main',
                'exp-explorer = experience_tracker.explorer:main'
            ]
        }
    )
