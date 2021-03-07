.. SSAM documentation master file, created by
   sphinx-quickstart on Sun Feb 02 22:41:59 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

   
Welcome to SSAM's documentation!
=========================================

Spatial Sustainability Assessment Model (SSAM)


Index
-----
.. toctree::
   :maxdepth: 3

   manual
   tutorial
   bibliography





Introduction
------------

	SSAM is a QGIS plugin for sustainability assessment in geographic environment, using environmental,  economic and social criteria. 
	It implements the algorithm  TOPSIS **[2]** which defines a ranking based on distance from the worst point and  closeness to an ideal point, for each used criteria.
	Entry of  weights can be done directly, if known, or  with the use of a pairwise comparison  table; in this way the user is led to define  a final vector weight, by means of a repeatable and verifiable path.

	The plugin works in QGIS **[3]**, a free and open source geographic software, widely used in several fields. With QGIS and python it is quite simple extend the software functionality and build new plugin. 

	SSAM is hosted in the official qgis plugin repository [http://plugins.qgis.org/plugins/] and is available under GNU GPL licence.
	The outputs of SSAM are both geographic and graphic. The first show the maps of the multicriteria analysis results for each elementary  area. The graphic output shows the numerical value of sustainability, with the use of  bars , bubbles and points .

	The plugin implements the DOMLEM [4] algorithm based on the "dominance based rough set" theory [5]. With its use the user can know the decisional rules derived from the TOPSIS algorithm and have a better overview of  the ranking  of sustainability shown by maps and graphs. The transparency, the  analysis and the  back analysis capability are extremely increased.

	The plugin SSAM uses a geographic vector file, eg. a shapefile, where the graphic data represent the single evaluation units (for example countries, regions or municipalities), while the alphanumeric data  (the attribute table), describe the environmental, economic and social indicators. The use of the algorithms available in the plugin allow to treat separately the indicators representing the three dimensions of sustainability, and to compute three different indexes. The linear combination of the three  indexes gives  a overall sustainability index for each geographic unit. 

	The user can use a wide number of indicators (the same number of those present in the shapefile) or he can use a set of data prepared by himself. However, using the data supplied from ARPA Umbria grants more robustness and repeatability  of output.
	In the next paragraphs we will use "plugin" and "SSAM" as synonymous. 
	We intend for “research unit” an administrative unit described by environmental, economic and social indicators (eg.  municipality, province, region, country, etc.) . 
	The numeric output of SSAM is the “sustainability index”, given from the linear combination of three different indexes: environmental index, economic index and social index. Higher is the value of those  indexes and better is the performance of a single "research unit".
