# RailQGIS
A RailML (https://railml.org) Import/Export Plugin for QGIS

Disclaimer: This project is completely experimental and I'm just about to start experimenting with both QGIS, Python, RaiML and Git. So don't expect anything. No guarantees at all ;-)

What works: Import of pure coordinates only.
* Analyse the number of coordinates saved in a <geoCoord ... /> tags in RailML
* Load these points as a temporary Layer into QGIS

Requirements (as of v0.1):
* A RailML file (tested v2.2 and v2.3, other v2.x files should probably work) ...
* ... containing EPSG:4326 (WGS 84) coordinates
* Coordinates are written in the format "LAT LON" (can be changed in code line 54/55)
