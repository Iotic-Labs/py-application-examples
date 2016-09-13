#!/bin/bash
export PYTHONPATH=~/infra.git/new_agent/src:.
echo -e "\n****** Python 3.x ******\n"
../3rd/python3/static_checks/run.sh flake8.cfg pylint.rc *.py
