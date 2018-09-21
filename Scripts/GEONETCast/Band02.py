#!/usr/bin/env python3
#######################################################################################################
# Manipulate GOES-16 NetCDF's Provided By INPE Via FTP
#######################################################################################################
# # Required libraries ==================================================================================
import matplotlib.pyplot as plt # Import the Matplotlib package
from mpl_toolkits.basemap import Basemap # Import the Basemap toolkit
import numpy as np # Import the Numpy package
from Scripts.cpt_convert import loadCPT  # Import the CPT convert function
from matplotlib.colors import LinearSegmentedColormap  # Linear interpolation for color maps
from matplotlib.patches import Rectangle # Library to draw rectangles on the plot
from netCDF4 import Dataset # Import the NetCDF Python interface
import os # Import os Python library, which gives the hability of using operating system functionality
# # Required libraries ==================================================================================

def processing(path):
    """
    Generates images from NetCDF files
    pathDir: root direcotry with "Data", "Output" and "Scripts" folders
    pathFile: path to NetCDF file to be manipulated
    outFolder: path to directory where the generated images should be saved
    Output: .png image file
    """

    # Getting information from the file name ============================================================
    # Search for the GOES-16 channel in the file name
    INPE_Band_ID = (path[path.find("S10635")+6:path.find("_")])
    # print(INPE_Band_ID)
    # Get the band number subtracting the value by 332
    Band = int(INPE_Band_ID) - 332

    # Create a GOES-16 Bands string array
    Wavelenghts = ['[]','[0.47 μm]','[0.64 μm]','[0.865 μm]','[1.378 μm]','[1.61 μm]','[2.25 μm]','[3.90 μm]',
    '[6.19 μm]','[6.95 μm]','[7.34 μm]','[8.50 μm]','[9.61 μm]','[10.35 μm]','[11.20 μm]','[12.30 μm]','[13.30 μm]']
    Band_Wavelenght = Wavelenghts[int(Band)]
    # Search for the Scan start in the file name
    Start = (path[path.find(INPE_Band_ID + "_")+4:path.find(".nc")])
    # Getting the date from the file name
    year = Start[0:4]
    month = Start[4:6]
    day = Start[6:8]
    date = day + "-" + month + "-" + year
    time = Start [8:10] + ":" + Start [10:12] + " UTC" # Time of the Start of the Scan

    # Get the unit based on the channel. If channels 1 trough 6 is Albedo. If channels 7 to 16 is BT.
    Unit = "Albedo (%)"
    # Choose a title for the plot
    Title = " GOES-16 ABI CMI Band " + str(Band) + " " + Band_Wavelenght + " " + Unit + " " + date + " " + time
    # Insert the institution name
    Institution = "CEPAGRI - UNICAMP"
    # Required libraries ================================================================================

    # Open the file using the NetCDF4 library
    nc = Dataset(path)

    # Choose the visualization extent (min lon, min lat, max lon, max lat)
    extent = [-115.98, -55.98, -25.01, 34.98]
    min_lon = extent[0]; max_lon = extent[2]; min_lat = extent[1]; max_lat = extent[3]

    # Get the latitudes
    lats = nc.variables['lat'][:]
    # Get the longitudes
    lons = nc.variables['lon'][:]

    # print (lats)
    # print (lons)

    # latitude lower and upper index
    latli = np.argmin(np.abs(lats - extent[1]))
    latui = np.argmin(np.abs(lats - extent[3]))

    # longitude lower and upper index
    lonli = np.argmin(np.abs(lons - extent[0]))
    lonui = np.argmin(np.abs(lons - extent[2]))

    # Extract the Brightness Temperature / Reflectance values from the NetCDF
    data = nc.variables['Band1'][ latli:latui , lonli:lonui ]

    # Flip the y axis, divede by 100
    data = (np.flipud(data) / 100)

    # Define the size of the saved picture ==============================================================
    DPI = 150
    ax = plt.figure(figsize=(2000/float(DPI), 2000/float(DPI)), frameon=True, dpi=DPI)
    #====================================================================================================

    # Plot the Data =====================================================================================
    # Create the basemap reference for the Rectangular Projection
    bmap = Basemap(llcrnrlon=extent[0], llcrnrlat=extent[1], urcrnrlon=extent[2], urcrnrlat=extent[3], epsg=4326)

    # Draw the countries and Brazilian states shapefiles
    bmap.readshapefile('/Scripts/GEONETCast/Shapefiles/BRA_adm1','BRA_adm1',linewidth=0.50,color='cyan')
    bmap.readshapefile('/Scripts/GEONETCast/Shapefiles/ne_10m_admin_0_countries','ne_10m_admin_0_countries',linewidth=0.50,color='cyan')

    # Draw parallels and meridians
    bmap.drawparallels(np.arange(-90.0, 90.0, 5.0), linewidth=0.3, dashes=[4, 4], color='white', labels=[False,False,False,False],
        fmt='%g', labelstyle="+/-", xoffset=-0.80, yoffset=-1.00, size=7)
    bmap.drawmeridians(np.arange(0.0, 360.0, 5.0), linewidth=0.3, dashes=[4, 4], color='white', labels=[False,False,False,False],
        fmt='%g', labelstyle="+/-", xoffset=-0.80, yoffset=-1.00, size=7)

    # Converts a CPT file to be used in Python
    cpt = loadCPT('/Scripts/GEONETCast/Colortables/Square Root Visible Enhancement.cpt')
    # Makes a linear interpolation
    cpt_convert = LinearSegmentedColormap('cpt', cpt)
    # Plot the GOES-16 channel with the converted CPT colors (you may alter the min and max to match your preference)
    bmap.imshow(data, origin='upper', cmap=cpt_convert, vmin=0, vmax=100)

    # Insert the colorbar at the bottom
    cb = bmap.colorbar(location='bottom', size = '2%', pad = '-3.5%', ticks=[20, 40, 60, 80])
    cb.ax.set_xticklabels(['20', '40', '60', '80'])
    cb.outline.set_visible(False) # Remove the colorbar outline
    cb.ax.tick_params(width = 0) # Remove the colorbar ticks
    cb.ax.xaxis.set_tick_params(pad=-14.5) # Put the colobar labels inside the colorbar
    cb.ax.tick_params(axis='x', colors='black', labelsize=8) # Change the color and size of the colorbar labels

    # Add a black rectangle in the bottom to insert the image description
    lon_difference = (extent[2] - extent[0]) # Max Lon - Min Lon
    currentAxis = plt.gca()
    currentAxis.add_patch(Rectangle((extent[0], extent[1]), lon_difference, lon_difference * 0.015, alpha=1, zorder=3, facecolor='black'))

    # Add the image description inside the black rectangle
    lat_difference = (extent[3] - extent[1]) # Max lat - Min lat
    plt.text(extent[0], extent[1] + lat_difference * 0.003,Title,horizontalalignment='left', color = 'white', size=10)
    plt.text(extent[2], extent[1] + lat_difference * 0.003,Institution, horizontalalignment='right', color = 'yellow', size=10)

    # Add logos / images to the plot
    logo_GNC = plt.imread('/Scripts/GEONETCast/Logos/GNC_Logo.png')
    logo_INPE = plt.imread('/Scripts/GEONETCast/Logos/INPE_Logo.png')
    logo_NOAA = plt.imread('/Scripts/GEONETCast/Logos/NOAA_Logo.png')
    logo_GOES = plt.imread('/Scripts/GEONETCast/Logos/GOES_Logo.png')
    logo_cepagri = plt.imread('/Scripts/GEONETCast/Logos/Logo_CEPAGRI.png')

    ax.figimage(logo_GNC, 20, 70, zorder=3, alpha = 1, origin = 'upper')
    ax.figimage(logo_INPE, 90, 70, zorder=3, alpha = 1, origin = 'upper')
    ax.figimage(logo_NOAA, 165, 70, zorder=3, alpha = 1, origin = 'upper')
    ax.figimage(logo_GOES, 228, 70, zorder=3, alpha = 1, origin = 'upper')
    ax.figimage(logo_cepagri, 326, 70, zorder=3, alpha=1, origin='upper')

    # Save the result
    # print('/Scripts/GEONETCast/Output/' + path[12:18] + '/INPE_G16_CH' + str(Band) + '_' + Start + '.png')
    plt.savefig('/Scripts/GEONETCast/Output/' + path[12:18] + '/INPE_G16_CH' + str(Band) + '_' + Start + '.png', dpi=DPI, bbox_inches='tight', pad_inches=0)

# Path to the GOES-R simulated image file
path = '/GEONETCast/Band02/'

# Create output folder if it does not exist
# "Band01, Band02, ..."
try:
    os.mkdir("/Scripts/GEONETCast/Output/Band02")
except FileExistsError:
    pass

# Run the function "processing" for each NetCDF file
dirs = os.listdir(path)
for file in dirs:
    try:
        processing(path + file)
        # print(path)
    except OSError:
        print("Erro Arquivo")

## FOLDER STRUCTURE

# Scripts/
# └── GEONETCast
#     ├── Band01.py
#     ├── Band02.py
#     ├── Band03.py
#     ├── Band04.py
#     ├── Band05.py
#     ├── Band06.py
#     ├── Band07.py
#     ├── Band08.py
#     ├── Band09.py
#     ├── Band10.py
#     ├── Band11.py
#     ├── Band12.py
#     ├── Band13.py
#     ├── Band14.py
#     ├── Band15.py
#     ├── Band16.py
#     ├── Colortables
#     │   ├── IR4AVHRR6.cpt
#     │   ├── Square Root Visible Enhancement.cpt
#     │   ├── SVGAIR2_TEMP.cpt
#     │   ├── SVGAIR_TEMP.cpt
#     │   ├── SVGAWVX_TEMP.cpt
#     │   └── WVCOLOR35.cpt
#     ├── Logos
#     │   ├── GNC_Logo.png
#     │   ├── GOES_Logo.png
#     │   ├── INPE_Logo.png
#     │   ├── Logo_CEPAGRI.png
#     │   └── NOAA_Logo.png
#     ├── Output
#     │   ├── Band01
#     │   │   └── INPE_G16_CH1_201808251945.png
#     │   ├── Band02
#     │   │   └── INPE_G16_CH2_201808301345.png
#     │   ├── Band03
#     │   │   └── INPE_G16_CH3_201808292145.png
#     │   ├── Band04
#     │   │   └── INPE_G16_CH4_201808291515.png
#     │   ├── Band05
#     │   │   └── INPE_G16_CH5_201808281930.png
#     │   ├── Band06
#     │   │   └── INPE_G16_CH6_201808301830.png
#     │   ├── Band07
#     │   │   └── INPE_G16_CH7_201808242030.png
#     │   ├── Band08
#     │   │   └── INPE_G16_CH8_201808301045.png
#     │   ├── Band09
#     │   │   └── INPE_G16_CH9_201808241245.png
#     │   ├── Band10
#     │   │   └── INPE_G16_CH10_201808251415.png
#     │   ├── Band11
#     │   │   └── INPE_G16_CH11_201808240015.png
#     │   ├── Band12
#     │   │   └── INPE_G16_CH12_201808300345.png
#     │   ├── Band13
#     │   │   └── INPE_G16_CH13_201808270215.png
#     │   ├── Band14
#     │   │   └── INPE_G16_CH14_201808251000.png
#     │   ├── Band15
#     │   │   └── INPE_G16_CH15_201808241600.png
#     │   └── Band16
#     │       └── INPE_G16_CH16_201808311530.png
#     ├── Scripts
#     │   ├── cpt_convert.py
#     └── Shapefiles
#         ├── BRA_adm1.dbf
#         ├── BRA_adm1.shp
#         ├── BRA_adm1.shx
#         ├── ne_10m_admin_0_countries.cpg
#         ├── ne_10m_admin_0_countries.dbf
#         ├── ne_10m_admin_0_countries.prj
#         ├── ne_10m_admin_0_countries.README.html
#         ├── ne_10m_admin_0_countries.shp
#         ├── ne_10m_admin_0_countries.shx
#         └── ne_10m_admin_0_countries.VERSION.txt
# GEONETCast/
# ├── Band01
# │   └── S10635333_201808251945.nc
# ├── Band02
# │   └── S10635334_201808301345.nc
# ├── Band03
# │   └── S10635335_201808292145.nc
# ├── Band04
# │   └── S10635336_201808291515.nc
# ├── Band05
# │   └── S10635337_201808281930.nc
# ├── Band06
# │   └── S10635338_201808301830.nc
# ├── Band07
# │   └── S10635339_201808242030.nc
# ├── Band08
# │   └── S10635340_201808301045.nc
# ├── Band09
# │   └── S10635341_201808241245.nc
# ├── Band10
# │   └── S10635342_201808251415.nc
# ├── Band11
# │   └── S10635344_201808240015.nc
# ├── Band12
# │   └── S10635345_201808300345.nc
# ├── Band13
# │   └── S10635346_201808270215.nc
# ├── Band14
# │   └── S10635347_201808251000.nc
# ├── Band15
# │   └── S10635348_201808241600.nc
# └── Band16
#     └── S10635349_201808311530.nc

# 39 directories, 73 files