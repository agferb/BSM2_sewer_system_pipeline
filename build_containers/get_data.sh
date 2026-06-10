#!/bin/sh
set -eu

TMP=$(mktemp -d)
wget -q -P "$TMP" http://iwa-mia.org/wp-content/uploads/2019/04/dyninfluent_bsm2.zip
unzip -o "$TMP/dyninfluent_bsm2.zip" -d "$TMP"
mv "$TMP/dyninfluent_bsm2.txt" bsm2_full_data.txt
rm -rf "$TMP"
