# ############################################################
# NAME: createDomain.py
#
# DESC: Jython WLST script to create basic domain (Node Manager
#       plus AdminServer).
#
# LOG:
# yyyy/mm/dd [user]: [version] [notes]
# 2014/01/17 cgwong: [v1.0.0] Initial creation.
# 2014/01/21 cgwong: [v1.0.1] Updated LDAP provider name to MonsantoAD.
# 2014/03/20 cgwong: [v1.0.2] Updated variable names.
# ############################################################

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.Writer;

def createFile(directory_name, file_name, content):
	dedirectory = java.io.File(directory_name);
	defile = java.io.File(directory_name + '/' + file_name);

	writer = None;
	try:
		dedirectory.mkdirs();
		defile.createNewFile();
		writer = java.io.FileWriter(defile);
		writer.write(content);
	finally:
		try:
			print 'WRITING FILE ' + file_name;
			if writer != None:
				writer.flush();
				writer.close();
		except java.io.IOException, e:
			e.printStackTrace();

print 'CREATE PATHS';
domain_name = os.getenv('DOMAIN_NAME');
java_home = os.getenv('JAVA_HOME');
mw_home = os.getenv('MW_HOME');
wls_home = os.getenv('WL_HOME');
fmw_home = os.getenv('FMW_HOME');
cfg_home = os.getenv('CFG_BASE');

domain_home = cfg_home + '/domains/' + domain_name;
domain_application_home = cfg_home + '/webapps/' + domain_name;
nm_home = domain_home + '/nodemanager';

weblogic_template = wls_home + '/common/templates/wls/wls.jar';

print 'CREATE DOMAIN';
readTemplate(weblogic_template);
setOption('DomainName', domain_name);
setOption('OverwriteDomain', 'true');
setOption('JavaHome', java_home);
setOption('ServerStartMode', 'prod');
cd('/Security/base_domain/User/weblogic');
cmo.setName(aserver_username);
cmo.setUserPassword(aserver_password);
cd('/');

print "SAVE DOMAIN";
writeDomain(domain_home);
closeTemplate();

print 'READ DOMAIN';
readDomain(domain_home);

print "SET NODE MANAGER CREDENTIALS";
cd("/SecurityConfiguration/" + domain_name);
cmo.setNodeManagerUsername(nm_username);
cmo.setNodeManagerPasswordEncrypted(nm_password);

print "DISABLE HOSTNAME VERIFICATION";
cd('/Server/' + aserver_name);
create(aserver_name,'SSL');
cd('SSL/' + aserver_name);
cmo.setHostnameVerificationIgnored(true);
cmo.setHostnameVerifier(None);
cmo.setTwoWaySSLEnabled(false);
cmo.setClientCertificateEnforced(false);

print "SET UP LDAP CONFIGURATION"
cd('/SecurityConfiguration/'+ domain_name +'/Realms/myrealm');
create('MonsantoAD', 'weblogic.security.providers.authentication.ActiveDirectoryAuthenticator', 'AuthenticationProvider');

# change the order of the authentication provider (only works in online mode)
#try:
#	set('AuthenticationProviders',jarray.array([ObjectName('Security:Name=myrealmMonsantoAD'), ObjectName('Security:Name=myrealmDefaultAuthenticator'), ObjectName('Security:Name=myrealmDefaultIdentityAsserter')], ObjectName));
#except java.lang.Exception, e:
#	dumpStack();

cd('AuthenticationProviders/DefaultAuthenticator');
set('ControlFlag', 'SUFFICIENT');
cd('../../');

cd('AuthenticationProviders/MonsantoAD');
set('ControlFlag', 'SUFFICIENT');
set('PropagateCauseForLoginException', 'true');
set('Principal', 'cn=' + ldap_principal + ',ou=Non-User Accounts,ou=1000,ou=Locations,dc=na,dc=ds,dc=monsanto,dc=com');
set('CredentialEncrypted', ldap_principal_password);
set('Host', ldap_host);
set('UserBaseDN', 'dc=ds,dc=monsanto,dc=com');
set('AllUsersFilter', '(&(cn=*)(objectclass=user))');
set('UserFromNameFilter', '(&(cn=%u)(objectclass=user))');
set('UserObjectClass', 'user');
set('UserNameAttribute', 'cn');
set('GroupBaseDN', 'dc=ds,dc=monsanto,dc=com');
set('AllGroupsFilter', '(&(cn=*)(objectclass=group))');
set('GroupFromNameFilter', '(&(cn=%g)(objectclass=group))');
set('GuidAttribute', 'objectguid');
set('StaticGroupObjectClass', 'group');
set('StaticGroupDNsfromMemberDNFilter', '(&(member=%M)(objectclass=group))');
set('StaticMemberDNAttribute', 'member');

print 'SAVE CHANGES';
updateDomain();
closeDomain();

print 'CREATE FILES';
directory_name = domain_home + '/servers/'+ aserver_name +'/security';
file_name = 'boot.properties';
content = 'username=' + aserver_username + '\npassword=' + aserver_password;
createFile(directory_name, file_name, content);

directory_name = domain_application_home;
file_name = 'readme.txt';
content = 'This directory contains deployment files and deployment plans.\nTo set-up a deployment, create a directory with the name of the application.\nSubsequently, create two sub-directories called app and plan.\nThe app directory contains the deployment artifact.\nThe plan directory contains the deployment plan.';
createFile(directory_name, file_name, content);

directory_name = nm_home;
file_name = 'nodemanager.properties';
if nm_mode == 'plain':
	content='DomainsFile=' + nm_home + '/nodemanager.domains\nLogLimit=0\nPropertiesVersion=12.1.2\nAuthenticationEnabled=true\nNodeManagerHome=' + nm_home + '\nJavaHome=' + java_home +'\nLogLevel=INFO\nDomainsFileEnabled=true\nStartScriptName=startWebLogic.sh\nListenAddress=\nNativeVersionEnabled=true\nListenPort=5556\nLogToStderr=true\nSecureListener=false\nLogCount=1\nStopScriptEnabled=false\nQuitEnabled=false\nLogAppend=true\nStateCheckInterval=500\nCrashRecoveryEnabled=true\nStartScriptEnabled=true\nLogFile=' + nm_home + '/nodemanager.log\nLogFormatter=weblogic.nodemanager.server.LogFormatter\nListenBacklog=50';
else:
	content='DomainsFile=' + nm_home + '/nodemanager.domains\nLogLimit=0\nPropertiesVersion=12.1.2\nAuthenticationEnabled=true\nNodeManagerHome=' + nm_home + '\nJavaHome=' + java_home +'\nLogLevel=INFO\nDomainsFileEnabled=true\nStartScriptName=startWebLogic.sh\nListenAddress=\nNativeVersionEnabled=true\nListenPort=5556\nLogToStderr=true\nSecureListener=false\nLogCount=1\nStopScriptEnabled=false\nQuitEnabled=false\nLogAppend=true\nStateCheckInterval=500\nCrashRecoveryEnabled=true\nStartScriptEnabled=true\nLogFile=' + nm_home + '/nodemanager.log\nLogFormatter=weblogic.nodemanager.server.LogFormatter\nListenBacklog=50';
createFile(directory_name, file_name, content);
