#!/bin/bash
cd /home/topis/Documents/deluge/deluge/plugins/deletepartials
mkdir temp
export PYTHONPATH=./temp
python setup.py build develop --install-dir ./temp
cp ./temp/DeletePartials.egg-link /home/topis/.config/deluge/plugins
rm -fr ./temp
