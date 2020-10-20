"""
Copyright 2020 Expedia, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from setuptools import setup, find_packages
import versioneer

setup(
    name="map_maker",
    version=versioneer.get_version(),
    packages=find_packages(exclude=["data/", "scripts/"]),
    author="Tim Renner",
    install_requires=[
        "click>=7.0",
        "toolz>=0.9",
        "bokeh>=1.1.0",
        "Shapely>=1.6.4.post2",
        "pyproj>=1.9.5.1,<2",
        "folium>=0.10.0,<1",
    ],
    entry_points={"console_scripts": ["map_maker=map_maker.cli:cli"]},
    cmdclass=versioneer.get_cmdclass(),
)
