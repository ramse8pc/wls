beahome = '/home/oracle/weblogic12.1.1';
pathseparator = '/';
adminusername = 'weblogic';
adminpassword = 'magic12c';
adminservername='AdminServer';
adminserverurl='t3://172.31.0.113:7001';
domainname = 'base_domain';
domaindirectory = beahome + pathseparator + 'user_projects' + pathseparator + 'domains' + pathseparator + domainname;
domaintemplate = beahome + pathseparator + 'wlserver_12.1' + pathseparator + 'common' + pathseparator + 'templates' + pathseparator + 'domains' + pathseparator + 'wls.jar';
jvmdirectory = '/home/oracle/jrrt-4.0.1-1.6.0';

print 'CREATE DOMAIN';
readTemplate(domaintemplate);
setOption('DomainName', domainname);
setOption('OverwriteDomain', 'true');
setOption('ServerStartMode', 'prod');
cd('/Security/base_domain/User/weblogic');
cmo.setName(adminusername);
cmo.setUserPassword(adminpassword);
cd('/');
writeDomain(domaindirectory);

# When using startServer command on WebLogic12c, we have to perform the following steps (1 and 2):
# Starting weblogic server ...
# WLST-WLS-1326447719560: Exception in thread "Main Thread" java.lang.AssertionError: JAX-WS 2.2 API is required, but an older version was found in the JDK.
# WLST-WLS-1326447719560: Use the endorsed standards override mechanism (http://java.sun.com/javase/6/docs/technotes/guides/standards/).
# WLST-WLS-1326447719560: 1) locate the bundled Java EE 6 endorsed directory in $WL_HOME/endorsed.
# WLST-WLS-1326447719560: 2) copy those JAR files to $JAVA_HOME/jre/lib/endorsed OR add the endorsed directory to the value specified by system property java.endorsed.dirs.
print 'START ADMIN SERVER';
startServer(adminservername, domainname, adminserverurl, adminusername, adminpassword, domaindirectory);

print 'CONNECT TO ADMIN SERVER';
connect(adminusername, adminpassword, adminserverurl);

print 'START EDIT MODE';
edit();
startEdit();

#print 'CHANGE NODEMANAGER USERNAME AND PASSWORD';
#cd('/SecurityConfiguration/' + domainname);
#cmo.setNodeManagerUsername(adminusername);
#set('NodeManagerPasswordEncrypted', encrypt(adminpassword, domaindirectory));
#cd('/');

print 'DISABLE HOSTNAME VERIFICATION';
cd('/Servers/' + adminservername + '/SSL/' + adminservername);
cmo.setHostnameVerificationIgnored(true);
cmo.setHostnameVerifier(None);
cmo.setTwoWaySSLEnabled(false);
cmo.setClientCertificateEnforced(false);
cd('/');

print 'SAVE AND ACTIVATE CHANGES';
save();
activate(block='true');

print 'SHUTDOWN THE ADMIN SERVER';
shutdown(block='true');

print 'START ADMIN SERVER';
startServer(adminservername, domainname, adminserverurl, adminusername, adminpassword, domaindirectory);

print 'CONNECT TO ADMIN SERVER';
connect(adminusername, adminpassword, adminserverurl);

print 'START EDIT MODE';
edit();
startEdit();

print 'CREATE MACHINE: machine1';
machine1 = cmo.createUnixMachine('machine1');
machine1.setPostBindUIDEnabled(true);
machine1.setPostBindUID('oracle');
machine1.getNodeManager().setListenAddress('172.31.0.175');
machine1.getNodeManager().setNMType('ssl');

print 'CREATE MACHINE: machine2';
machine2 = cmo.createUnixMachine('machine2');
machine2.setPostBindUIDEnabled(true);
machine2.setPostBindUID('oracle');
machine2.getNodeManager().setListenAddress('172.31.0.113');
machine2.getNodeManager().setNMType('ssl');

print 'CREATE CLUSTER: CLUSTER';
cluster = cmo.createCluster('cluster');
cluster.setClusterMessagingMode('unicast');

print 'CREATE MANAGED SERVER: server1';
server1 = cmo.createServer('server1');
server1.setListenPort(7002);
server1.setListenAddress('172.31.0.175');
server1.setAutoRestart(true);
server1.setAutoKillIfFailed(true);
server1.setRestartMax(2);
server1.setRestartDelaySeconds(10);
server1.getServerStart().setJavaHome(jvmdirectory);
server1.getServerStart().setJavaVendor('Oracle');
server1.getServerStart().setArguments('-jrockit -Xms1024m -Xmx1024m -Xns256m -Xgc:throughput');

print 'CREATE MANAGED SERVER: server2';
server2 = cmo.createServer('server2');
server2.setListenPort(7003);
server2.setListenAddress('172.31.0.113');
server2.setAutoRestart(true);
server2.setAutoKillIfFailed(true);
server2.setRestartMax(2);
server2.setRestartDelaySeconds(10);
server2.getServerStart().setJavaHome(jvmdirectory);
server2.getServerStart().setJavaVendor('Oracle');
server2.getServerStart().setArguments('-jrockit -Xms1024m -Xmx1024m -Xns256m -Xgc:throughput');

print 'ADD MANAGED SERVERS TO CLUSTER';
server1.setCluster(cluster);
server2.setCluster(cluster);

print 'ADD MANAGED SERVERS TO MACHINE';
server1.setMachine(machine1);
server2.setMachine(machine2);

print 'SAVE AND ACTIVATE CHANGES';
save();
activate(block='true');

print 'START EDIT MODE';
startEdit();

print 'CREATE FILESTORE FOR SERVER1';
filestore1 = cmo.createFileStore('FileStore1');
filestore1.setDirectory(beahome + pathseparator + 'deploy');
targets = filestore1.getTargets();
targets.append(server1);
filestore1.setTargets(targets);

print 'CREATE JMS SERVER FOR SERVER1';
jmsserver1 = cmo.createJMSServer('JMSServer1');
jmsserver1.setPersistentStore(filestore1);
jmsserver1.setTargets(targets);

targets.remove(server1);
targets.append(server2);

print 'CREATE FILESTORE FOR SERVER2';
filestore2 = cmo.createFileStore('FileStore2');
filestore2.setDirectory(beahome + pathseparator + 'deploy');
filestore2.setTargets(targets);

print 'CREATE JMS SERVER FOR SERVER2';
jmsserver2 = cmo.createJMSServer('JMSServer2');
jmsserver2.setPersistentStore(filestore2);
jmsserver2.setTargets(targets);

targets.remove(server2);
targets.append(cluster);

print 'CREATE JMS SYSTEM MODULE';
module = cmo.createJMSSystemResource('SystemModule');
module.setTargets(targets);

print 'CREATE SUBDEPLOYMENT';
module.createSubDeployment('SubDeployment');
cd('/JMSSystemResources/SystemModule/SubDeployments/SubDeployment');
set('Targets',jarray.array([ObjectName('com.bea:Name=JMSServer1,Type=JMSServer'), ObjectName('com.bea:Name=JMSServer2,Type=JMSServer')], ObjectName));
cd('/');

resource = module.getJMSResource();

print 'CREATE CONNECTION FACTORY';
resource.createConnectionFactory('ConnectionFactory');
connectionfactory = resource.lookupConnectionFactory('ConnectionFactory');
connectionfactory.setJNDIName('jms/ConnectionFactory');
connectionfactory.setDefaultTargetingEnabled(true);
connectionfactory.getTransactionParams().setTransactionTimeout(3600);
connectionfactory.getTransactionParams().setXAConnectionFactoryEnabled(true);

print 'CREATE UNIFORM DISTRIBUTED QUEUE';
resource.createUniformDistributedQueue('DistributedQueue');
distributedqueue = resource.lookupUniformDistributedQueue('DistributedQueue');
distributedqueue.setJNDIName('jms/CompanyQueue');
distributedqueue.setLoadBalancingPolicy('Round-Robin');
distributedqueue.setSubDeploymentName('SubDeployment');

print 'CREATE DATA SOURCE';
datasource = cmo.createJDBCSystemResource('DataSource');
datasource.setTargets(targets);
jdbcResource = datasource.getJDBCResource();
jdbcResource.setName('DataSource');
names = ['jdbc/exampleDS'];
dataSourceParams = jdbcResource.getJDBCDataSourceParams();
dataSourceParams.setJNDINames(names);
dataSourceParams.setGlobalTransactionsProtocol('LoggingLastResource');
driverParams = jdbcResource.getJDBCDriverParams();
driverParams.setUrl('jdbc:oracle:thin:@hostname:1521:sid');
driverParams.setDriverName('oracle.jdbc.OracleDriver');
driverParams.setPassword('password');
driverProperties = driverParams.getProperties();
driverProperties.createProperty('user');
userProperty = driverProperties.lookupProperty('user');
userProperty.setValue('username');
connectionPoolParams = jdbcResource.getJDBCConnectionPoolParams();
connectionPoolParams.setTestTableName('SQL SELECT 1 FROM DUAL');
connectionPoolParams.setConnectionCreationRetryFrequencySeconds(100);

print 'SAVE AND ACTIVATE CHANGES';
save();
activate(block='true');

print 'SHUTDOWN THE ADMIN SERVER';
shutdown(block='true');
