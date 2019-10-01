#!/bin/bash
echo "Copying Deps... "
ln -sf ../*.c* .
#cp ../*.c* .
echo "Building ioticagent_http_cc3000.h..."
cat ioticagent_http_cc3000.h.tmpl ../agent.h > ioticagent_http_cc3000.h
echo "Building ioticagent_http_ethernet.h..."
cat ioticagent_http_ethernet.h.tmpl ../agent.h > ioticagent_http_ethernet.h
