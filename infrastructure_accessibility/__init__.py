from qgis.core import QgsApplication
from .infrastructure_accessibility_algorithm import InfrastructureAccessibilityProvider

def classFactory(iface):
    """Load the plugin.
    
    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    provider = InfrastructureAccessibilityProvider()
    provider.iface = iface  # Store iface reference
    QgsApplication.processingRegistry().addProvider(provider)
    return provider 