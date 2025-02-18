from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsProject, QgsMapLayer, QgsWkbTypes
import os.path
from .infrastructure_accessibility import InfrastructureAccessibilityMap
from .dialog import InfrastructureAccessibilityDialog

class InfrastructureAccessibilityPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.map_tool = None
        self.first_start = None

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI"""
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')
        
        self.action = QAction(
            QIcon(icon_path),
            'Infrastructure Accessibility',
            self.iface.mainWindow()
        )
        self.action.triggered.connect(self.run)
        
        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu('Infrastructure Accessibility', self.action)
        
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon"""
        self.iface.removePluginMenu('Infrastructure Accessibility', self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        """Run method that performs all the real work"""
        if self.first_start:
            self.first_start = False
            self.dlg = InfrastructureAccessibilityDialog()
        
        # Populate layer combos
        layers = QgsProject.instance().mapLayers().values()
        
        self.dlg.cooperatives_combo.clear()
        self.dlg.roads_combo.clear()
        self.dlg.markets_combo.clear()
        
        for layer in layers:
            if layer.type() == QgsMapLayer.VectorLayer:
                if layer.geometryType() == QgsWkbTypes.PointGeometry:
                    self.dlg.cooperatives_combo.addItem(layer.name(), layer)
                    self.dlg.markets_combo.addItem(layer.name(), layer)
                elif layer.geometryType() == QgsWkbTypes.LineGeometry:
                    self.dlg.roads_combo.addItem(layer.name(), layer)
        
        # Show the dialog
        result = self.dlg.exec_()
        
        # See if OK was pressed
        if result:
            # Get selected layers
            cooperatives = self.dlg.cooperatives_combo.currentData()
            roads = self.dlg.roads_combo.currentData()
            markets = self.dlg.markets_combo.currentData()
            
            # Run the analysis
            map_tool = InfrastructureAccessibilityMap(self.iface)
            map_tool.process_layers(cooperatives, roads, markets) 