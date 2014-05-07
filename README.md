WebLogic Server (WLS) Software Installation Tool
================================================
 
Installs the software stack for Oracle Weblogic Server. Specifically, the 
following steps are done:
  
  1. Install the specified Oracle JDK (optional) - This is Oracle JRockit 
     for WLS 11g and JDK 1.7 for WLS 12c. This stop is optional given there 
     may be an existing installation which will be used instead.
     
  2. Install the specified WLS software release
  
  3. Apply any patches as specified to the WLS installation

  
Configuration File
------------------
The default environment setup file is assumed to be in the same directory as
the script. However, the -f parameter can be used to specify an alternate file.
This is also useful when doing multiple concurrent installations. Ensure this
file is reviewed and updated for the respective environment prior to starting
any installation. The file is self-documented making any edits fairly obvious.


Patching
--------
The patches to be applied should be in the original zip format in order to be
applied. The exception is for PSU patches which should have a '-psuX' appended
to its name before the extension, where the optional X is the PSU number.
For example, PSU7 for WLS 10.3.6 would be named "p17572726_1036_Generic-psu7.zip".


Usage
-----
 ${SCRIPT} [OPTION]
 
 OPTIONS
  -f [path/file]
    Full path and file name for environment setup file to be used.
  
  -nojdk
    Flag to skip an Oracle JDK installation (for when one already exists on the server).
    
  -h
    Display this help screen.    


Script Features
---------------
- installs Oracle JDK (JRockit 1.6, JDK 1.7)
- installs WebLogic Server 11g, 12c (10.3.5, 10.3.6 & 12.1.2)
- apply Linux low on entropy or urandom fix
- install WLS software
- apply a BSU patch on a FMW home (< 12.1.2)
- apply an OPatch on a FMW home (>= 12.1.2)
