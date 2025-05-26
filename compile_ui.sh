#!/bin/bash
cd ui
/usr/lib/qt6/uic -g python < gui.ui > ui_gui.py
/usr/lib/qt6/uic -g python < tag_adder.ui > ui_tag_adder.py
/usr/lib/qt6/uic -g python < time_adjuster.ui > ui_time_adjuster.py
cd ..
