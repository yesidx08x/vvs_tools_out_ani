"""Launch Tik Manager for Photoshop."""

import sys
pack_paths =[ r'L:\VVS_PIPELINE\pipeline\in_house','L:\VVS_PIPELINE\pipeline\in_house\python\Python310\Lib\site-packages']
for path in pack_paths:
    if path not in sys.path:
        sys.path.append(path)
from stage.external.Qt import QtWidgets
from stage.UI import main

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = main.launch(app="photoshop", dont_show=True)
    win.on_new_version()
    sys.exit(app.exec_())