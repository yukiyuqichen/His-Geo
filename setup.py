from setuptools import setup
from setuptools import find_packages


VERSION = '0.1.11'

setup(
    name='historical_geocoder',  # package name
    version=VERSION,  # package version
    author='Yuqi Chen',
    author_email='cyq0722@pku.edu.cn',
    install_requires=[
        'geopandas',
        'geopy',
        'shapely',
        'openai',
        'keplergl',
        'setuptools',
    ],
    package_data={
        'historical_geocoder': ['*.py', 'data/*']
    },
    description='A library to extract historical toponyms and locations from texts, geocode the locations, and visualize the results.',
    packages=find_packages(),
    zip_safe=False,
)