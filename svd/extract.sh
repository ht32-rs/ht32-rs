#!/bin/sh
set -ev
wget https://mcu.holtek.com.tw/pack/Holtek.HT32_DFP.1.0.44.pack -O holtek_pack.zip
unzip -LL holtek_pack.zip
rm -r arm holtek.ht32_dfp.pdsc
mv svd/* .
rm -r svd
