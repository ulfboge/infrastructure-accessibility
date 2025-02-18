"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterVectorLayer,
    QgsProcessingParameterNumber,
    QgsProcessingParameterFeatureSink,
    QgsField,
    QgsFeatureSink,
    QgsSymbol,
    QgsGraduatedSymbolRenderer,
    QgsGradientColorRamp,
    QgsProcessingUtils,
    QgsProcessingException
)
import processing

class InfrastructureAccessibilityAlgorithm(QgsProcessingAlgorithm):
    """
    Infrastructure Accessibility analysis algorithm.
    Calculates accessibility scores for cooperatives based on their
    proximity to roads and markets.
    """

    # Constants used to refer to parameters and outputs
    INPUT_COOPERATIVES = 'INPUT_COOPERATIVES'
    INPUT_ROADS = 'INPUT_ROADS'
    INPUT_MARKETS = 'INPUT_MARKETS'
    ROAD_BUFFER_DISTANCES = 'ROAD_BUFFER_DISTANCES'
    MARKET_BUFFER_DISTANCES = 'MARKET_BUFFER_DISTANCES'
    ROAD_WEIGHT = 'ROAD_WEIGHT'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return InfrastructureAccessibilityAlgorithm()

    def name(self):
        """
        Returns the algorithm name.
        """
        return 'infrastructureaccessibility'

    def displayName(self):
        """
        Returns the translated algorithm name.
        """
        return self.tr('Infrastructure Accessibility Analysis')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to.
        """
        return self.tr('Infrastructure Analysis')

    def groupId(self):
        """
        Returns the unique ID of the group.
        """
        return 'infrastructureanalysis'

    def shortHelpString(self):
        """
        Returns a short helper string for the algorithm.
        """
        return self.tr('''
        Calculates accessibility scores for cooperatives based on their proximity to infrastructure.
        
        Parameters:
            - Cooperatives layer (point)
            - Roads layer (line)
            - Markets layer (point)
            - Buffer distances for roads and markets
            - Weight for road accessibility vs market accessibility
            
        Outputs a new layer with accessibility scores and graduated styling.
        ''')

    def initAlgorithm(self, config=None):
        """
        Define the inputs and outputs of the algorithm.
        """
        # Add the input vector layers
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT_COOPERATIVES,
                self.tr('Cooperatives Layer'),
                [QgsProcessing.TypeVectorPoint]
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT_ROADS,
                self.tr('Roads Layer'),
                [QgsProcessing.TypeVectorLine]
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT_MARKETS,
                self.tr('Markets Layer'),
                [QgsProcessing.TypeVectorPoint]
            )
        )

        # Add numeric parameters
        self.addParameter(
            QgsProcessingParameterNumber(
                self.ROAD_BUFFER_DISTANCES,
                self.tr('Road Buffer Distances (comma-separated meters)'),
                QgsProcessingParameterNumber.Integer,
                defaultValue=1000,
                optional=False,
                minValue=1
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.MARKET_BUFFER_DISTANCES,
                self.tr('Market Buffer Distances (comma-separated meters)'),
                QgsProcessingParameterNumber.Integer,
                defaultValue=2000,
                optional=False,
                minValue=1
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.ROAD_WEIGHT,
                self.tr('Road Accessibility Weight (0-1)'),
                QgsProcessingParameterNumber.Double,
                defaultValue=0.6,
                optional=False,
                minValue=0,
                maxValue=1
            )
        )

        # Add the output
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Accessibility Results')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Process the algorithm.
        """
        # Get parameters
        cooperatives = self.parameterAsVectorLayer(parameters, self.INPUT_COOPERATIVES, context)
        roads = self.parameterAsVectorLayer(parameters, self.INPUT_ROADS, context)
        markets = self.parameterAsVectorLayer(parameters, self.INPUT_MARKETS, context)
        road_distance = self.parameterAsInt(parameters, self.ROAD_BUFFER_DISTANCES, context)
        market_distance = self.parameterAsInt(parameters, self.MARKET_BUFFER_DISTANCES, context)
        road_weight = self.parameterAsDouble(parameters, self.ROAD_WEIGHT, context)
        market_weight = 1 - road_weight

        if feedback.isCanceled():
            return {}

        # Create road buffers
        feedback.pushInfo('Creating road buffers...')
        road_buffers = processing.run(
            "native:multiplebuffer",
            {
                'INPUT': roads,
                'DISTANCE': [road_distance, road_distance * 2, road_distance * 5],
                'SEGMENTS': 5,
                'DISSOLVE': False,
                'OUTPUT': 'memory:'
            },
            context=context,
            feedback=feedback
        )['OUTPUT']

        if feedback.isCanceled():
            return {}

        # Create market buffers
        feedback.pushInfo('Creating market buffers...')
        market_buffers = processing.run(
            "native:multiplebuffer",
            {
                'INPUT': markets,
                'DISTANCE': [market_distance, market_distance * 2, market_distance * 5],
                'SEGMENTS': 5,
                'DISSOLVE': False,
                'OUTPUT': 'memory:'
            },
            context=context,
            feedback=feedback
        )['OUTPUT']

        if feedback.isCanceled():
            return {}

        # Prepare output layer
        fields = cooperatives.fields()
        fields.append(QgsField('accessibility_score', QVariant.Double))
        
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            cooperatives.wkbType(),
            cooperatives.sourceCrs()
        )

        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # Calculate accessibility scores
        total = 100.0 / cooperatives.featureCount() if cooperatives.featureCount() else 0
        
        for current, feature in enumerate(cooperatives.getFeatures()):
            if feedback.isCanceled():
                break

            # Calculate scores
            point = feature.geometry()
            
            # Road score
            road_score = 0
            for buffer_feat in road_buffers.getFeatures():
                if point.intersects(buffer_feat.geometry()):
                    road_score = 100 - (buffer_feat['distance'] * 0.01)
                    break
            
            # Market score
            market_score = 0
            for buffer_feat in market_buffers.getFeatures():
                if point.intersects(buffer_feat.geometry()):
                    market_score = 100 - (buffer_feat['distance'] * 0.01)
                    break
            
            # Calculate total score
            total_score = (road_score * road_weight) + (market_score * market_weight)
            
            # Create output feature
            out_feat = feature
            out_feat.setAttributes(feature.attributes() + [total_score])
            sink.addFeature(out_feat, QgsFeatureSink.FastInsert)

            feedback.setProgress(int(current * total))

        # Style the output layer
        layer = QgsProcessingUtils.mapLayerFromString(dest_id, context)
        if layer:
            symbol = QgsSymbol.defaultSymbol(layer.geometryType())
            renderer = QgsGraduatedSymbolRenderer.createRenderer(
                layer,
                'accessibility_score',
                5,
                QgsGraduatedSymbolRenderer.Jenks,
                symbol
            )
            
            # Set color ramp
            renderer.updateColorRamp(QgsGradientColorRamp(
                QColor(255, 0, 0),  # red for poor accessibility
                QColor(0, 255, 0)   # green for good accessibility
            ))
            
            layer.setRenderer(renderer)
            layer.triggerRepaint()

        return {self.OUTPUT: dest_id}


class InfrastructureAccessibilityProvider(QgsProcessingProvider):
    def loadAlgorithms(self):
        self.addAlgorithm(InfrastructureAccessibilityAlgorithm())

    def id(self):
        return 'infrastructureaccessibility'

    def name(self):
        return self.tr('Infrastructure Accessibility')

    def icon(self):
        return QgsProcessingProvider.icon(self)

    def longName(self):
        return self.name() 