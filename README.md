Tool for generating cc0 world maps in SVG
=========================================

The main feature is that it can generate equirectangular output, suitable for texture mapping.

Equirectangular projection
--------------------------
`./worldmapsvg.py -d 512x512 --equirectangular --land-color="#008000" --sea-color="#000010" -o test0.svg`

![alt tag](https://raw.github.com/sqaxomonophonen/worldmapsvg/master/media/test0.png)


Robinson projection
-------------------
`./worldmapsvg.py -d 512x512 --robinson --sea-color="#000000" -o test1.svg`

![alt tag](https://raw.github.com/sqaxomonophonen/worldmapsvg/master/media/test1.png)


Credits & Sources
=================
- public domain svg path parser and generator: https://pypi.python.org/pypi/svg.path
- public domain map source: https://en.wikipedia.org/wiki/File:WorldMap.svg (original source: CIA's World Factbook)
