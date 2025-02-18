from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel, QFileDialog
from qgis.PyQt.QtGui import QColor
from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsSymbol,
    QgsGraduatedSymbolRenderer,
    QgsProcessingFeedback,
    QgsDistanceArea,
    QgsField,
    QgsGradientColorRamp,
    QgsProcessingUtils,
    QgsMessageLog
)
from qgis.PyQt.QtCore import QVariant
from qgis.analysis import QgsNativeAlgorithms
import processing

class InfrastructureAccessibilityMap:
    def __init__(self, iface):
        self.iface = iface
        self.project = QgsProject.instance()

    def process_layers(self, cooperatives, roads, markets):
        """Process the selected layers"""
        try:
            # Create distance buffers
            road_buffers = self.create_buffers(roads, [1000, 2000, 5000], 'road_buffers')
            if not road_buffers:
                self.iface.messageBar().pushWarning(
                    "Error", "Failed to create road buffers"
                )
                return

            market_buffers = self.create_buffers(markets, [2000, 5000, 10000], 'market_buffers')
            if not market_buffers:
                self.iface.messageBar().pushWarning(
                    "Error", "Failed to create market buffers"
                )
                return

            # Calculate accessibility scores
            success = self.calculate_accessibility_scores(cooperatives, road_buffers, market_buffers)
            if not success:
                self.iface.messageBar().pushWarning(
                    "Error", "Failed to calculate accessibility scores"
                )
                return

            # Style the cooperative layer
            self.style_cooperatives(cooperatives)

            # Refresh the map canvas
            self.iface.mapCanvas().refresh()

            self.iface.messageBar().pushSuccess(
                "Success", "Infrastructure accessibility analysis completed"
            )

        except Exception as e:
            self.iface.messageBar().pushCritical(
                "Error", f"An error occurred: {str(e)}"
            )
            QgsMessageLog.logMessage(
                f"Error in infrastructure accessibility analysis: {str(e)}",
                level=QgsMessageLog.CRITICAL
            )

    def create_buffers(self, layer, distances, output_name):
        """Create multiple buffer rings around features"""
        try:
            params = {
                'INPUT': layer,
                'DISTANCE': distances,
                'SEGMENTS': 5,
                'DISSOLVE': False,
                'OUTPUT': 'memory:' + output_name
            }
            result = processing.run("native:multiplebuffer", params)
            buffer_layer = result['OUTPUT']
            
            if buffer_layer and buffer_layer.isValid():
                self.project.addMapLayer(buffer_layer)
                return buffer_layer
            return None

        except Exception as e:
            QgsMessageLog.logMessage(
                f"Error creating buffers: {str(e)}",
                level=QgsMessageLog.CRITICAL
            )
            return None

    def calculate_accessibility_scores(self, cooperatives, road_buffers, market_buffers):
        """Calculate accessibility scores for cooperatives"""
        try:
            # Check if accessibility_score field exists
            score_idx = cooperatives.fields().indexOf('accessibility_score')
            if score_idx == -1:
                # Add a field for accessibility score
                cooperatives.dataProvider().addAttributes([
                    QgsField("accessibility_score", QVariant.Double)
                ])
                cooperatives.updateFields()
                score_idx = cooperatives.fields().indexOf('accessibility_score')

            # Calculate scores based on proximity
            cooperatives.startEditing()
            
            total_features = cooperatives.featureCount()
            current_feature = 0

            for feat in cooperatives.getFeatures():
                # Update progress
                current_feature += 1
                progress = (current_feature / total_features) * 100
                
                point = feat.geometry()
                road_score = self.calculate_proximity_score(point, road_buffers)
                market_score = self.calculate_proximity_score(point, market_buffers)
                
                # Combined score (weighted average)
                total_score = (road_score * 0.6) + (market_score * 0.4)
                
                cooperatives.changeAttributeValue(feat.id(), score_idx, total_score)

            success = cooperatives.commitChanges()
            return success

        except Exception as e:
            QgsMessageLog.logMessage(
                f"Error calculating accessibility scores: {str(e)}",
                level=QgsMessageLog.CRITICAL
            )
            return False

    def calculate_proximity_score(self, point, buffer_layer):
        """Calculate proximity score based on buffer distances"""
        try:
            score = 0
            for buffer_feat in buffer_layer.getFeatures():
                if point.intersects(buffer_feat.geometry()):
                    # Higher score for closer buffers
                    distance = buffer_feat['distance']
                    if isinstance(distance, (int, float)):
                        score = 100 - (distance * 0.01)
                        break
            return score

        except Exception as e:
            QgsMessageLog.logMessage(
                f"Error calculating proximity score: {str(e)}",
                level=QgsMessageLog.CRITICAL
            )
            return 0

    def style_cooperatives(self, layer):
        """Style cooperatives layer based on accessibility scores"""
        try:
            # Create graduated symbol renderer
            symbol = QgsSymbol.defaultSymbol(layer.geometryType())
            
            # Set symbol size and color
            symbol.setSize(3)  # Base size for points
            
            renderer = QgsGraduatedSymbolRenderer.createRenderer(
                layer,
                'accessibility_score',
                5,  # number of classes
                QgsGraduatedSymbolRenderer.Jenks,  # classification method
                symbol
            )
            
            # Set color ramp (red to green)
            color_ramp = QgsGradientColorRamp(
                QColor(255, 0, 0),  # red for poor accessibility
                QColor(0, 255, 0)   # green for good accessibility
            )
            renderer.updateColorRamp(color_ramp)
            
            # Update symbol sizes based on classes
            for idx, range_item in enumerate(renderer.ranges()):
                symbol = range_item.symbol().clone()
                # Increase size for better accessibility
                symbol.setSize(3 + (idx * 1))
                range_item.setSymbol(symbol)
            
            layer.setRenderer(renderer)
            
            # Refresh layer
            layer.triggerRepaint()

        except Exception as e:
            QgsMessageLog.logMessage(
                f"Error styling cooperatives layer: {str(e)}",
                level=QgsMessageLog.CRITICAL
            ) 