#!/usr/bin/env bash
basedir=$(dirname $(readlink -f $0))
cd $basedir
python main.py
python backup.py
