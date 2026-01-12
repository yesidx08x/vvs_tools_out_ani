@echo off

::set OCIO=L:\VVS_PIPELINE\vvs-dcc-plugins\common\aces_1.2\config.ocio
set absolutePath=L:\VVS_PIPELINE\pipeline\in_house\maya
set standalonePath=L:\VVS_PIPELINE\vvs-dcc-plugins\standalone
set XBMLANGPATH=%standalonePath%/mayaDev/vvs_Shelf/icons;%absolutePath%/res/icons; 
set PYTHONPATH=%PYTHONPATH%;%absolutePath%;%absolutePath%/scripts;
set MAYA_SCRIPT_PATH=%absolutePath%/scripts;
set MAYA_PATH=L:\VVS_PIPELINE\pipeline\in_house\maya
set MAYA_MODULE_PATH=L:\VVS_PIPELINE\vvs-dcc-plugins\maya\default\submitters\Maya
set MAYA_RENDER_SETUP_INCLUDE_ALL_LIGHTS = 0
set MAYA_ENV_DIR=L:\VVS_PIPELINE\pipeline\in_house\maya\2025
set MAYA_SHELF_PATH=L:\VVS_PIPELINE\pipeline\in_house\maya\2025\prefs\shelves
set project_name=DM
set project_id=1036
set fps=24
set resolutions=2048X858
set AUTOTX=0
set view_transform=Rec.709 (ACES)
set MAYA_ENABLE_LEGACY_RENDER_LAYERS=0
cd /d "C:\Program Files\Autodesk\Maya2025\bin"
start maya.exe

exit
