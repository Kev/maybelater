#!/bin/bash

#Please set the following variables:
#These examples assume you have the project in $HOME/devel/maybelater/project with a config file named config-kev.xml
PATH_CONTAINING_PROJECT_FOLDER=$HOME/devel/maybelater
PROJECT_MODULE=project
CONFIG_FILE=config-kev.xml
#Stop editing

export PYTHONPATH=$PATH_CONTAINING_PROJECT_FOLDER:$PYTHONPATH
export DJANGO_SETTINGS_MODULE="${PROJECT_MODULE}.settings"

python xmppbot.py --config=$CONFIG_FILE $1