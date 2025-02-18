# Infrastructure & Accessibility Map QGIS Plugin

A QGIS plugin that visualizes infrastructure accessibility for cooperatives, showing their proximity to roads, markets, and other key infrastructure.

## Features

- Visualizes road networks and market locations
- Creates distance buffers from cooperatives to nearest major roads/markets
- Uses symbol sizes to indicate accessibility levels
- Generates accessibility scores based on proximity to infrastructure

## Installation

1. Download the ZIP file from the latest release
2. Open QGIS
3. Go to Plugins → Manage and Install Plugins
4. Choose "Install from ZIP" and select the downloaded file
5. Enable the plugin in the Plugins menu

## Required Data

The plugin expects the following input layers:
- Cooperatives (point layer)
- Roads (line layer)
- Markets (point layer)

## Usage

1. Ensure all required layers are loaded in your QGIS project
2. Go to Plugins → Infrastructure Accessibility → Generate Accessibility Map
3. Select your input layers in the dialog
4. Click "Run" to generate the visualization

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 