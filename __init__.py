# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name			 	 : SSAM Spatial Sustainability Assessment Model
Description          : geographical MCDA for sustainability assessment
Date                 : 10/05/2019
copyright            : (C) 2012 by Gianluca Massei
email                : g_massa@libero.it

 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""


def classFactory(iface):	# inizializza il plugin
	from .SSAM import SSAM	# importiamo la classe che realizza il plugin
	return SSAM(iface)	# creiamo una istanza del plugin
