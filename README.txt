Copyright (c) 2013 Gianluca Massei <g_massa@libero.it>
http://maplab.alwaysdata.net

Licensed under the terms of GNU GPL v2 (or any later)
http://www.gnu.org/copyleft/gpl.html

---
# for rebuild GUI:

rm *.pyc
pyuic5 -o ui_geoSUST.py geoSUST.ui
pyrcc5 -o resources.py resources.qrc

