from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing, QgsProcessingAlgorithm,
    QgsProcessingParameterRasterLayer, QgsProcessingParameterFileDestination,
    QgsRasterLayer, QgsProcessingUtils)
import numpy as np
from osgeo import gdal

class LandCoverChangeDetector(QgsProcessingAlgorithm):
    """
    This algorithm detects changes between two classified land cover maps
    and generates a change detection map and statistics.
    """
    
    INPUT_RASTER1 = 'INPUT_RASTER1'
    INPUT_RASTER2 = 'INPUT_RASTER2'
    OUTPUT_RASTER = 'OUTPUT_RASTER'
    
    def tr(self, string):
        return QCoreApplication.translate('Processing', string)
        
    def createInstance(self):
        return LandCoverChangeDetector()
        
    def name(self):
        return 'landcoverchangedetector'
        
    def displayName(self):
        return self.tr('Land Cover Change Detector')
        
    def group(self):
        return self.tr('Raster Analysis')
        
    def groupId(self):
        return 'rasteranalysis'
        
    def shortHelpString(self):
        return self.tr('Detects changes between two classified land cover maps')
        
    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_RASTER1,
                self.tr('First classified image'),
                optional=False
            )
        )
        
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_RASTER2,
                self.tr('Second classified image'),
                optional=False
            )
        )
        
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT_RASTER,
                self.tr('Change detection result'),
                fileFilter='GeoTIFF files (*.tif)'
            )
        )
        
    def processAlgorithm(self, parameters, context, feedback):
        raster1 = self.parameterAsRasterLayer(parameters, self.INPUT_RASTER1, context)
        raster2 = self.parameterAsRasterLayer(parameters, self.INPUT_RASTER2, context)
        output_path = self.parameterAsOutputLayer(parameters, self.OUTPUT_RASTER, context)
        
        # Read raster data into numpy arrays
        ds1 = gdal.Open(raster1.source())
        ds2 = gdal.Open(raster2.source())
        
        array1 = ds1.GetRasterBand(1).ReadAsArray()
        array2 = ds2.GetRasterBand(1).ReadAsArray()
        
        # Create change detection map
        change_map = np.where(array1 != array2, 1, 0)
        
        # Get geotransform and projection from input
        geotransform = ds1.GetGeoTransform()
        projection = ds1.GetProjection()
        
        # Create output raster
        driver = gdal.GetDriverByName('GTiff')
        out_ds = driver.Create(output_path, 
                             ds1.RasterXSize, 
                             ds1.RasterYSize, 
                             1, 
                             gdal.GDT_Byte)
        
        out_ds.SetGeoTransform(geotransform)
        out_ds.SetProjection(projection)
        
        # Write the change detection results
        out_band = out_ds.GetRasterBand(1)
        out_band.WriteArray(change_map)
        
        # Calculate statistics
        total_pixels = change_map.size
        changed_pixels = np.sum(change_map)
        change_percentage = (changed_pixels / total_pixels) * 100
        
        feedback.pushInfo(f'Total changed area: {changed_pixels} pixels')
        feedback.pushInfo(f'Percentage changed: {change_percentage:.2f}%')
        
        # Clean up
        out_ds = None
        ds1 = None
        ds2 = None
        
        return {self.OUTPUT_RASTER: output_path} 