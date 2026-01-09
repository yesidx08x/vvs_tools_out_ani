@echo off
set PATH=C:\VVS_PLUGINS\pipeline\in_house\python\Python310;%PATH%
set PYTHONPATH=C:\VVS_PLUGINS\pipeline\in_house\python\Python310\Lib;C:\VVS_PLUGINS\pipeline\in_house\python\Python310\DLLs
set PYTHONHOME=C:\VVS_PLUGINS\pipeline\in_house\python\Python310
set OCIO=L:\VVS_PIPELINE\vvs-dcc-plugins\common\aces_1.2\config.ocio
set NUITKA_PYTHONPATH=L:\VVS_PIPELINE\pipeline\in_house\apps\exr2tif;C:\VVS_PLUGINS\pipeline\in_house\python\Python310\DLLs;C:\VVS_PLUGINS\pipeline\in_house\python\Python310\lib;C:\VVS_PLUGINS\pipeline\in_house\python\Python310;C:\Users\soul\AppData\Roaming\Python\Python310\site-packages;C:\VVS_PLUGINS\pipeline\in_house\python\Python310\lib\site-packages;C:\VVS_PLUGINS\pipeline\in_house\python\Python310\lib\site-packages\win32;C:\VVS_PLUGINS\pipeline\in_house\python\Python310\lib\site-packages\win32\lib;C:\VVS_PLUGINS\pipeline\in_house\python\Python310\lib\site-packages\Pythonwin;C:\VVS_PLUGINS\pipeline\in_house\python\Python310\lib\site-packages\setuptools\_vendor
set nk_path=C:\Program Files\Nuke14.1v1\Nuke14.1.exe
cd /d L:\VVS_PIPELINE\pipeline\in_house\apps\exr2tif
start app.exe
exit