#!/bin/sh

PATH="${PATH}:/www/app/oracle/weblogic/Oracle_WT1/opmn/bin/"
ORACLE_INSTANCE="/www/app/oracle/weblogic/Oracle_WT1/instances/instance1/"
export ORACLE_INSTANCE

if [ "$1" == "status" ] ; then
  opmnctl status
fi

if [ "$1" == "stopohs" ] ; then
  opmnctl stopproc process-type=OHS
fi

if [ "$1" == "startohs" ] ; then
  opmnctl startproc process-type=OHS
fi
