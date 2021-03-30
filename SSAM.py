# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name            : SSAM - Spatial Sustainability Assessment Model
Description     : geographical MCDA for sustainability assessment
Date            : 6/2/2021
copyright       : ARPA Umbria - Università degli Studi di Perugia (C) 2019
email           : (developper) Gianluca Massei (geonomica@gmail.com)

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


from __future__ import absolute_import
from builtins import object

from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication,Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QMessageBox, QMenu, QAction
from qgis.core import QgsMapLayer
# Initialize Qt resources from file resources.py
from . import resources
import os
import webbrowser

import numpy as np





class SSAM:
    def __init__(self, iface):
        self.iface = iface    # salviamo il riferimento all'interfaccia di QGis

    def initGui(self):
        self.actionSUST = QAction(QIcon(":/plugins/ssam/icon.png"), "SSAM II (Spatial Sustainability Assessment Model)", self.iface.mainWindow())
        self.actionSUST.triggered.connect(self.runSSAM)
        self.iface.addToolBarIcon(self.actionSUST)
        self.iface.addPluginToMenu( "&SSAM II",self.actionSUST )

    def unload(self):
        self.iface.removePluginMenu( "&SSAM II",self.actionSUST)
        self.iface.removeToolBarIcon(self.actionSUST)
        
    def runSSAM(self):
        from .guiSSAM import guiSSAMDialog
        self.active_layer = self.iface.activeLayer()
        self.base_layer = self.iface.activeLayer()
        if ((self.active_layer == None) or (self.active_layer.type() != QgsMapLayer.VectorLayer)):
            result=QMessageBox.warning(self.iface.mainWindow(), "SSAM",
            ("No active layer found\n" "Please make active one or more vector layer\n" \
            "Do you need documents or data ?"), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if result  == QMessageBox.Yes:
                webbrowser.open("http://maplab.alwaysdata.net/SSAM.html")
        else:
            dlg = guiSSAMDialog(self.iface)
            flags = Qt.Window | Qt.WindowSystemMenuHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint
            dlg.setWindowFlags(flags)
            dlg.setWindowModality(Qt.NonModal)
            #dlg.setModal(False)
            dlg.show()
            dlg.exec_()

