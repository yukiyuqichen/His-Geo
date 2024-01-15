from setuptools import setup
from setuptools import find_packages


VERSION = '0.1.2'

setup(
    name='his_geo',  # package name
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
        'his_geo': ['*.py', 'data/*']
    },
    description='A library to extract historical toponyms from texts, geocode and visualize the results.',
    packages=find_packages(),
    zip_safe=False,
)