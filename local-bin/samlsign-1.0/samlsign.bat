@echo off
setlocal

REM We need a JVM
if not defined JAVA_HOME  (
  echo Error: JAVA_HOME is not defined.
  exit /b
)

if not defined JAVACMD (
  set JAVACMD="%JAVA_HOME%\bin\java.exe"
)

if not exist %JAVACMD% (
  echo Error: JAVA_HOME is not defined correctly.
  echo Cannot execute %JAVACMD%
  exit /b
)

set ENDORSED=.\endorsed

if defined CLASSPATH (
  set LOCALCLASSPATH=%CLASSPATH%
)

REM Don't know where the jar ends up when samlsign is an extension
REM Run from top of distribution ?

call %IDP_HOME%\tools\bat\cpappend.bat target\samlsign-1.0.jar

for %%i in (.\lib\*.jar) do (
        call .\cpappend.bat %%i
)

if exist %JAVA_HOME%\lib\tools.jar (
    set LOCALCLASSPATH=%LOCALCLASSPATH%;%JAVA_HOME%\lib\tools.jar
)

if exist %JAVA_HOME%\lib\classes.zip (
    set LOCALCLASSPATH=%LOCALCLASSPATH%;%JAVA_HOME%\lib\classes.zip
)


%JAVACMD% -Xmx256m -cp "%LOCALCLASSPATH%" -Djava.endorsed.dirs="%ENDORSED%"  org.opensaml.util.samlsign.SAMLSign %*