# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RailML
                                 A QGIS plugin
 Import/Export functions for RailML format
                             -------------------
        begin                : 2017-08-01
        copyright            : (C) 2017 by Johannes Ludwig
        email                : ludwigjohannes@ymail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load RailML class from file RailML.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .railml import RailML
    return RailML(iface)
