#!/bin/sh

BEA_HOME="/www/weblogic/weblogic12.1.1"
export BEA_HOME

WL_HOME="${BEA_HOME}/wlserver_12.1"
export WL_HOME

. ${WL_HOME}/common/bin/wlst.sh ${BEA_HOME}/deploy/scripts/startDomain.py
