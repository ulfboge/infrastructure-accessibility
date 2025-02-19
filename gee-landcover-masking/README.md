# Land Cover Masking Script for Google Earth Engine

## Description
This script processes Landsat imagery by masking it based on specific land cover classes (Shrubland, Grassland, and Bare/Sparse Vegetation) from the ESA WorldCover dataset.

## Features
- Masks Landsat imagery using ESA WorldCover data
- Processes multiple years (2013-2023)
- Clips imagery to specific polygon areas
- Exports results to Google Drive

## Prerequisites
- Google Earth Engine account
- Access to the specified asset locations:
  - Polygon features: 'projects/ee-komba/assets/kaya/wirong/mask_5_8'
  - Landsat images in 'projects/ee-komba/assets/kaya/'

## Usage
1. Open the script in Google Earth Engine Code Editor
2. Run the script
3. Check the 'Tasks' tab to start the exports
4. Results will be saved to your Google Drive with naming convention: 'NDFI_Masked_[YEAR]_Area_[NUMBER]'

## Land Cover Classes Used
- 20: Shrubland
- 30: Grassland
- 60: Bare/Sparse Vegetation
