from qgis.PyQt.QtWidgets import (QDialog, QVBoxLayout, QPushButton, QLabel, 
                                QDialogButtonBox, QFormLayout)
from qgis.gui import QgsMapLayerComboBox
from qgis.core import QgsMapLayerProxyModel

class InfrastructureAccessibilityDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Infrastructure Accessibility Analysis")
        
        # Create layout
        layout = QFormLayout()
        
        # Create layer selection combos using QgsMapLayerComboBox
        self.cooperatives_combo = QgsMapLayerComboBox()
        self.roads_combo = QgsMapLayerComboBox()
        self.markets_combo = QgsMapLayerComboBox()
        
        # Set filters for layer types
        self.cooperatives_combo.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.roads_combo.setFilters(QgsMapLayerProxyModel.LineLayer)
        self.markets_combo.setFilters(QgsMapLayerProxyModel.PointLayer)
        
        # Add to layout
        layout.addRow("Cooperatives Layer:", self.cooperatives_combo)
        layout.addRow("Roads Layer:", self.roads_combo)
        layout.addRow("Markets Layer:", self.markets_combo)
        
        # Add standard buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
        
        self.setLayout(layout) 