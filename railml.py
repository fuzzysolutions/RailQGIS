# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RailML
                                 A QGIS plugin
 Import/Export functions for RailML format
                              -------------------
        begin                : 2017-08-01
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Johannes Ludwig
        email                : ludwigjohannes@ymail.com
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt, QDir, QVariant
from PyQt4.QtGui import QAction, QIcon, QFileDialog
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources

# Import the code for the DockWidget
from railml_dockwidget import RailMLDockWidget
import os.path

# Import the ElementTree XML API
import xml.etree.ElementTree as ET
from fileinput import filename


# Namespace definition - blank (To be updated in updatens())
railnsURI = ""
railns = ""
ns = {'rail': railnsURI,
      'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
      'schemaLocation': railnsURI      
      }



# Global XML Tag definitions (prepared for possible changes in RailML Scheme definition
geoCoord = "geoCoord"
coord = "coord"
id = "id"
epsgCode = "epsgCode"


#Latitude / Longitude order as used in the coord="0 1" tag
lat = 1
lon = 0

railmlpath = ""
railmlname=""

epsg="4326"

class RailML:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'RailML_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&RailML')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'RailML')
        self.toolbar.setObjectName(u'RailML')

        #print "** INITIALIZING RailML"

        self.pluginIsActive = False
        self.dockwidget = None
        
        

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('RailML', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/RailML/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'RailML'),
            callback=self.run,
            parent=self.iface.mainWindow())

    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING RailML"

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        #print "** UNLOAD RailML"

        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&RailML'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    #--------------------------------------------------------------------------
    def updateNs(self):
        """Get the actual namespace
        """
        global railns
        global railnsURI
        global ns
        railns = "{"+railnsURI+"}"
        ns = {'rail': railnsURI,
              'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
              'schemaLocation': railnsURI      
              }
        
    # convert coordinates from lat_lon to lat,lon
    def convCoords(self, text):
        newtext=text.split()
        return newtext
    
    def parse_railml(self):
        """Load and analyse the railml structure
        """
        global geoCoord
        global ns
        global railnsURI
        global railmlpath
        global elements
        global epsg
        global epsgCode
        
        i=0
        
        self.dockwidget.labelCoordCount.clear()
        self.dockwidget.labelCoordCount.setText("searching ...")
        
        tree = ET.parse(railmlpath)
        root = tree.getroot()
        railnsURI=root.tag.split('}')[0].strip('{')
        self.updateNs()
        elements = root.findall((".//%s"+geoCoord+"/..") %railns)
        for element in elements:
            i=i+1
        self.dockwidget.labelCoordCount.clear()
        self.dockwidget.labelCoordCount.setText(str(i) + " Elements found.")
        if i > 0:
            self.dockwidget.buttonLoadPoints.setEnabled(True)
        else:
            self.dockwidget.buttonLoadPoints.setEnabled(False)
        #Automatically detect EPSG code from first element
        coordtag=elements[1].find((".//%s"+geoCoord) %railns)
        epsg=str(coordtag.get(epsgCode))
        if epsg=="None":
            epsg="4326" # Fallback
    
    def load_Points(self):
        """Loads Points as temporary Layer into QGIS.
            Attention: Here goes Lat Lon Coordinate conversion in (see for new RailML version ...
        """        
        global railmlpath
        global railmlname
        global ns
        global coord
        global geoCoord
        global id
        global elements
        global epsg
        
        self.dockwidget.labelCoordCount.clear()
        self.dockwidget.labelCoordCount.setText("loading ...")
        
        pointLayer = self.iface.addVectorLayer(('Point?crs=epsg:'+epsg), railmlname , 'memory')
        prov = pointLayer.dataProvider()     # Set the provider to accept the data source
        prov.addAttributes([QgsField('id', QVariant.String)])  # Add an "id" field to the layer
        feat = QgsFeature()             # Prepare a container for new features
        pointLayer.updateFields()   # Update in order to enable id field
        
        i=0
        tree = ET.parse(railmlpath)
        root = tree.getroot()
        
        for element in elements:
            i=i+1
            elementid = element.get(id)
            coordtag=element.find((".//%s"+geoCoord) %railns)
            coordtext=self.convCoords(coordtag.get(coord))
            point = QgsPoint(float(coordtext[lat]), float(coordtext[lon]))  # get the new coordinate
            feat.setGeometry(QgsGeometry.fromPoint(point))  # load it into the feature container
            feat.setAttributes([elementid])
            prov.addFeatures([feat])    # add the feature
        pointLayer.updateExtents()      # Update extent of the layer
        
        self.dockwidget.labelCoordCount.clear()
        self.dockwidget.labelCoordCount.setText(str(i) + " Elements loaded.")
        
    def select_input_file(self):
        """Loads a new RailML file."""
        global railmlname
        global railmlpath
        railmlpath = QFileDialog.getOpenFileName(self.dockwidget, "Select RailML file","", "RailML files (*.railml *.xml)")
        if railmlpath != "":
            self.dockwidget.labelFilename.clear()
            railmlname=QDir(railmlpath).dirName()
            self.dockwidget.labelFilename.setText(railmlname)
            self.parse_railml()


    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True

            #print "** STARTING RailML"

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = RailMLDockWidget()

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
            self.dockwidget.show()
            
            global railmlpath
            
            self.dockwidget.buttonNewFile.clicked.connect(self.select_input_file)
            self.dockwidget.buttonLoadPoints.clicked.connect(self.load_Points)

