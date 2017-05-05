#!/usr/bin/env bash
# Copyright (c) 2015 Iotic Labs Ltd. All rights reserved.

# To run ExtMon2 produced by this script:
# PYTHONPATH=path/to/archive.pyz python3 -m ExtMon2

PYTHONPATH=../3rd

# Final archive name
OUT_NAME=ExtMon2.pyz
# Temporary build directory
TMP_DIR=build
# Python optimisation level
OPTIMIZE=2

rm -rf $TMP_DIR
mkdir $TMP_DIR

function writePyz {
    # PyZipFile does not seem to re-generate byte code so clean up first
    find -H "$1" -iname '*.py[cod]' -delete
    /usr/bin/env python3 -bbsS -W all -c "
from zipfile import PyZipFile, ZIP_STORED
from os.path import realpath, basename

name = realpath('${1}')
outfile = '%s/%s.pyz' % ('${TMP_DIR}', basename(name))
with PyZipFile(outfile, mode='w', compression=ZIP_STORED, optimize=${OPTIMIZE}) as z:
    z.writepy(name)
print(name + '.pyz written')
"

    return $?
}

echo -e "\n*** Compiling ExtMon2"
writePyz ExtMon2
if [ $? -ne 0 ]; then
  exit 1
fi

echo -e "\n*** Compiling ExtMon2 direct dependencies"
for i in `find ../3rd -mindepth 1 -maxdepth 1 | grep -vE "(__pycache__|\.py[cod]|(dist|egg)-info)$"`; do
    writePyz $i
    if [ $? -ne 0 ]; then
      exit 1
    fi
done

echo -e "\n*** Re-extracting individual pyz files"
mkdir ${TMP_DIR}/final
for i in ${TMP_DIR}/*.pyz; do
    unzip -oq $i -d ${TMP_DIR}/final
done
echo -e "\n*** Producing final archive ${OUT_NAME}"
OUT_DIR=`pwd`
pushd ${TMP_DIR}/final >> /dev/null
zip -qr ${OUT_DIR}/${OUT_NAME} *
popd >> /dev/null
rm -r ${TMP_DIR}
