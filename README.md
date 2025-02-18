# Infrastructure Accessibility QGIS Plugin

A QGIS Processing plugin that analyzes infrastructure accessibility for cooperatives by calculating proximity scores to roads and markets.

## Features

- Calculates accessibility scores based on proximity to:
  - Roads (line features)
  - Markets (point features)
- Configurable buffer distances for both roads and markets
- Adjustable weighting between road and market accessibility
- Outputs a styled layer with graduated colors showing accessibility scores

## Installation

1. Open QGIS
2. Go to Plugins → Manage and Install Plugins
3. Select "Install from ZIP" tab
4. Browse to the downloaded plugin ZIP file
5. Click "Install Plugin"

## Usage

1. Open QGIS Processing Toolbox
2. Find "Infrastructure Accessibility Analysis" under "Infrastructure Analysis"
3. Set the following parameters:
   - Cooperatives Layer (point features)
   - Roads Layer (line features)
   - Markets Layer (point features)
   - Buffer distances for roads and markets
   - Weight for road accessibility (0-1)
4. Run the analysis

The output layer will show cooperatives colored from red (poor accessibility) to green (good accessibility).

## Requirements

- QGIS 3.0 or later
- Processing Framework enabled

## Development

To contribute to this plugin:

1. Clone the repository: