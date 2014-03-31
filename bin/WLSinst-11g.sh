#!/bin/bash
######################################################
# NAME: WLSinst.sh
#
# DESC: Installs Oracle WebLogic Server (WLS) 10.3.5 software.
#
# LOG:
# yyyy/mm/dd [user] - [notes]
# 2013/09/12 cgwong - [v1.0.0] Creation.
# 2014/01/18 cgwong - [v1.1.0] Added logging functionality.
#                   - Updated variables, added central inventory function
# 2014/01/21 cgwong - [v1.1.1] Updated LOGFILE variable.
# 2014/02/09 cgwong - [v1.2.0] Added WLS patching.
#                     Added script name in header comments.
# 2014/02/17 cgwong - [v1.2.1] Used basename instead of readlink
# 2014/03/19 cgwong - [v2.0.0] Added functionality for WLS 10.3.5
#                     Added functionality for JRockit
#                     Used Java entropy fix in security module
#                     Switched to external response file edits.
# 2014/03/20 cgwong - [v2.1.0] Reduced functionality to WLS 11g specifically.
# 2014/03/21 cgwong - [v2.2.0] Added exit status.
#                     Added checks for file/directory existence.
#                     Switched to double ticks for messages.
#                     Removed inventory update.
#                     Other improvements (command line parameter) and bug fixes.
# 2014/03/24 cgwong - [v2.2.1] Updated patching variables.
# 2014/03/25 cgwong - [v2.3.1] Updated directory empty check.
#                     Included response file update.
######################################################

SCRIPT=`basename $0`
SCRIPT_PATH=$(dirname $SCRIPT)
SETUP_FILE=${SCRIPT_PATH}/WLSenv-inst.sh

. ${SETUP_FILE}

# -- Variables -- #
PID=$$
LOGFILE=${LOG_DIR}/`echo ${SCRIPT} | awk -F"." '{print $1}'`.log
PB_LOG=${LOG_DIR}/`echo ${SCRIPT} | awk -F"." '{print $1}'`-bsu.log
SKIP_JDK="N"
ERR=1     # Error status
SUC=0     # Success status

# -- Functions -- #
msg ()
{ # Print message to screen and log file
  # Valid parameters:
  #   $1 - function name
  #   $2 - Message Type or status
  #   $3 - message
  #
  # Log format:
  #   Timestamp: [yyyy-mm-dd hh24:mi:ss]
  #   Component ID: [compID: ]
  #   Process ID (PID): [pid: ]
  #   Host ID: [hostID: ]
  #   User ID: [userID: ]
  #   Message Type: [NOTE | WARN | ERROR | INFO | DEBUG]
  #   Message Text: "Metadata Services: Metadata archive (MAR) not found."

  # Variables
  TIMESTAMP=`date "+%Y-%m-%d %H:%M:%S"`
  [[ -n $LOGFILE ]] && echo -e "[${TIMESTAMP}],PRC: ${1},PID: ${PID},HOST: $TGT_HOST,USER: ${USER}, STATUS: ${2}, MSG: ${3}" | tee -a $LOGFILE
}

show_usage ()
{ # Show script usage
  echo "
 ${SCRIPT} - Linux shell script to install Oracle JRockit and WebLogic Server (WLS) 11g software.
  This script should NOT be used for WLS 12c installation as it does not include the
  logic required for that installation. There should be another script available
  to install WLS 12c. This script will install, in order of installation:
  
  1. The specified Oracle JRockit release (optional)
  2. The specified WLS 11g software release
  3. Any patches as specified to be applied to WLS
  
  The default environment setup file, ${SETUP_FILE}, is assumed to be in the same directory
  as this script. The -f parameter can be used to specify another file or location.

 USAGE
 ${SCRIPT} [OPTION]
 
 OPTIONS
  -f [path/file]
    Full path and file name for environment setup file to be used. The default is: ${SETUP_FILE}
  
  -nojdk
    Flag to skip an Oracle JDK installation (for when one already exists on the server).
    
  -h
    Display this help screen.    
"
}

create_silent_install_files() 
{ # Create/setup installation response files
  # Setup JRockit response file
  if [ -f "${JVM_RSP_FILE}" ]; then
    msg create_silent_install_file INFO "Creating JVM silent install file..."
    sed "/USER_INSTALL_DIR/c\    <data-value name=\"USER_INSTALL_DIR\" value=\"${JAVA_HOME}\" />" ${JVM_RSP_FILE} > ${STG_DIR}/`basename ${JVM_RSP_FILE}`
    JVM_RSP_FILE=${STG_DIR}/`basename ${JVM_RSP_FILE}`    # Reset variable to new value for easier referencing in script
  else
    msg create_silent_install_file ERROR "Missing silent install file: ${JVM_RSP_FILE}"
    exit $ERR
  fi

  # Setup BSU response file
  if [ -f "${BSU_RSP_FILE}" ]; then
    msg create_silent_install_file INFO "Creating BSU silent install file..."
    sed "/BEAHOME/c\    <data-value name=\"BEAHOME\" value=\"${MW_HOME}\" />" ${BSU_RSP_FILE} > ${STG_DIR}/`basename ${BSU_RSP_FILE}`
    BSU_RSP_FILE=${STG_DIR}/`basename ${BSU_RSP_FILE}`    # Reset variable to new value for easier referencing in script
  else
    msg create_silent_install_file ERROR "Missing silent install file: ${BSU_RSP_FILE}"
    exit $ERR
  fi
  
  # Setup WLS response file
  if [ -f "${WL_RSP_FILE}" ]; then
    msg create_silent_install_file INFO "Creating WLS silent install file..."
    cat ${WL_RSP_FILE} | sed "/BEAHOME/c\    <data-value name=\"BEAHOME\" value=\"${MW_HOME}\" />" | sed "/WLS_INSTALL_DIR/c\    <data-value name=\"WLS_INSTALL_DIR\" value=\"${WL_HOME}\" />" | sed "/LOCAL_JVMS/c\    <data-value name=\"LOCAL_JVMS\" value=\"${JAVA_HOME}\" />" > ${STG_DIR}/`basename ${WL_RSP_FILE}`
    WL_RSP_FILE=${STG_DIR}/`basename ${WL_RSP_FILE}`    # Reset variable to new value for easier referencing in script
  else
    msg create_silent_install_file ERROR "Missing silent install file: ${WL_RSP_FILE}"
    exit $ERR
  fi
}

install_jdk() 
{ # Install Oracle JDK
  if [ ! -d "${ORACLE_BASE}" ]; then    # Create ORACLE_BASE directory if it does not exist
    msg install_jdk INFO "Creating directory: ${ORACLE_BASE}."
    mkdir -p ${ORACLE_BASE}
  fi

  if [ ! -f "$JVM_FILE" ]; then   # Check for existence of file
    msg install_jdk ERROR "Missing JVM file: ${JVM_FILE}."
    exit $ERR
  fi
  msg install_jdk INFO "Installing Oracle JRockit..."
  ${JVM_FILE} -mode=silent -silent_xml=${JVM_RSP_FILE}

  # Rename the file and create a link which uses the full version
  # This allows for easier JDK upgrades in future
  mv ${JVM_HOME} ${JAVA_HOME}/
  ln -s ${JAVA_HOME} ${JVM_HOME}
  
  # Adjust Java entropy value to avoid performance bug with Linux
  msg install_jdk INFO "Adjusting entropy gathering device settings..."
  sed '/securerandom/ s_file:/dev/urandom_file:/dev/./urandom_' ${JAVA_HOME}/jre/lib/security/java.security > ${STG_DIR}/java.security
  mv ${STG_DIR}/java.security ${JAVA_HOME}/jre/lib/security/java.security
}

install_wls() 
{ # Install WLS software
  if [ ! -f "${WL_FILE}" ]; then   # Check for existence of file
    msg install_wls ERROR "Missing file: ${WL_FILE}, unable to install WLS."
    exit $ERR
  fi
  if [ ! -f "${WL_RSP_FILE}" ]; then   # Check for existence of file
    msg install_wls ERROR "Missing file: ${WL_RSP_FILE}, unable to install WLS."
    exit $ERR
  fi
  msg install_wls INFO "Installing WebLogic Server..."
  ${JAVA_HOME}/bin/java -d64 -Xms512m -Xmx512m -jar ${WL_FILE} -mode=silent -silent_xml=${WL_RSP_FILE}
}

patch_wls ()
{ # Apply patches to WLS
  if [ `ls ${PB_DIR}/*.zip 2>/dev/null | wc -l` -gt 0 ]; then   # Not empty directory
    msg patch_wls INFO "Applying patch bundle ${PB} to WLS..."

    # Apply Updated BSU (Smart Update) first
    # This is ONLY required for WLS 10.3.5 so it can apply latest patches. The file MUST be manually renamed correctly
    # as we are expecting it to match a certain format such that the filtering works
    if [ `ls ${PB_DIR}/p*Generic-bsu.zip 2>/dev/null | wc -l` -gt 0 ]; then
      [ ! -d ${PB_DIR}/cache_dir ] && mkdir ${PB_DIR}/cache_dir    # Create BSU cache directory if it does not exist
      unzip -oq ${PB_DIR}/p*-bsu.zip -d ${PB_DIR}/cache_dir
      msg patch_wls INFO "Updating WLS Smart Update to v3.3.0"
      ${JAVA_HOME}/bin/java -jar ${PB_DIR}/cache_dir/patch-client-installer330_generic32.jar -mode=silent -silent_xml=${BSU_RSP_FILE}
      rm -rf ${PB_DIR}/cache_dir    # Clean up BSU cache directory 
    fi
    
    # Apply PSU first. The file MUST be manually renamed correctly
    # as we are expecting it to match a certain format such that the filtering works
    [ ! -d ${PB_CACHE_DIR} ] && mkdir ${PB_CACHE_DIR}    # Create BSU cache directory if it does not exist
    unzip -oq ${PB_DIR}/p*Generic-psu*.zip -d ${PB_CACHE_DIR}
    psupatch=`basename $(ls -1 ${PB_CACHE_DIR}/*.jar | cut -d '.' -f1)`        # Get just the patch ID name
    
    # Save current directory and switch to the location of bsu script as it cannot be called outside it's home (MOS 1326309.1; bug# 8478260)
    CURR_DIR=${PWD}
    cd ${BSU_DIR}
    msg patch_wls INFO "Applying PSU to WLS."
    ${BSU_DIR}/bsu.sh -install -patchlist=${psupatch} -patch_download_dir=${PB_CACHE_DIR} -prod_dir=${WL_HOME} -log=${PB_LOG}  

    # Check if other patches are available
    if [ `ls -l ${PB_DIR}/p*.zip 2>/dev/null | grep -v psu | grep -v bsu | wc -l` -gt 0 ]; then   # Not empty directory
      # Uncompress other patches in directory (in zip format) to cache dir and apply
      for fname in `ls -l ${PB_DIR}/p*.zip | grep -v psu | grep -v bsu`; do
        unzip -oq ${fname} -d ${PB_CACHE_DIR}
      done

      # Apply other patches
      for patchname in `basename $(ls -1 ${PB_CACHE_DIR}/*.jar | grep -v ${psupatch} | cut -d '.' -f1)`; do
        msg patch_wls INFO "Applying WLS patch ${patchname}."
        ${BSU_DIR}/bsu.sh -install -patchlist=${patchname} -patch_download_dir=${PB_CACHE_DIR} -prod_dir=${WL_HOME} -log=${PB_LOG}
      done
    fi
    cd ${CURR_DIR}
  else    # Empty directory
    msg patch_wls INFO "No zipped patches found to apply in ${PB_DIR}."
  fi
}


# -- Main Code -- #
# Process command line
while [ $# -gt 0 ] ; do
  case $1 in
  -f)   # Different setup file
    SETUP_FILE=$2
    if [ -z "$SETUP_FILE" ] || [ ! -f "$SETUP_FILE" ]; then
      msg MAIN ERROR "A valid file is required for the -f parameter."
      show_usage
      exit $ERR
    fi
    . ${SETUP_FILE}
    shift ;;
  -nojdk)   # Skip JDK installation
    SKIP_JDK="Y"
    shift ;;
  -h)   # Print help and exit
    show_usage
    exit $SUC ;;
  *)   # Print help and exit
    show_usage
    exit $ERR ;;
  esac
  shift
done

# Setup staging
RUN_DT=`date "+%Y%m%d-%H%M%S"`
STG_DIR=${STG_DIR}/install-${RUN_DT}
[ ! -d "${STG_DIR}" ] && mkdir -p ${STG_DIR}

create_silent_install_files
[ "${SKIP_JDK}" == "N" ] && install_jdk
install_wls
patch_wls

# END