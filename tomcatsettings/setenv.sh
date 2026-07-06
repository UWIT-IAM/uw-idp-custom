#!/bin/bash

# Environment variables for Tomcat, linked from ${TOMCAT_HOME}/bin/setenv.sh
#
# The CATALINA_OPTS are things used by Tomcat only. Mostly Java memory options.
#
# The JAVA_OPTS variable sets the location of the IdP configuration files; this is
# necessary, otherwise the Shibboleth webapp will expect them in /opt/shibboleth-idp.
# This has to be in JAVA_OPTS since it is used by the webapp, not Tomcat itself.
#
# The CATALINA_OUT variable sets the location of the catalina.out file, which is
# the Tomcat output written to stdout/stderr. This is output from Tomcat itself
# rather than from any of the individual webapps.

export CATALINA_OPTS=-server -XX:+UseParallelGC -Xss24m -Xms4g -Xmx4g -XX:MaxGCPauseMillis=400
export JAVA_OPTS=-Didp.home=/data/local/idp
export CATALINA_OUT=/data/logs/tomcat/catalina.out
