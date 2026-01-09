import sys

pack_paths =[ r'L:\VVS_PIPELINE\pipeline\in_house']
for path in pack_paths:
    if path not in sys.path:
        sys.path.append(path)
from stage.external.Qt import QtWidgets
from stage.UI import main

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    from time import time
    import os
    start = time()
    main.launch(app="photoshop")
    end = time()
    print("Took %s seconds", (end - start))
    sys.exit(app.exec_())