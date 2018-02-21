@echo off
if _%1_==_payload_  goto :payload

:getadmin
    echo %~nx0: elevating self
    set vbs=%temp%\~ElevateMe.vbs
    echo Set UAC = CreateObject^("Shell.Application"^)                >> "%vbs%"
    echo UAC.ShellExecute "%~s0", "payload %~sdp0 %*", "", "runas", 0 >> "%vbs%"
    "%temp%\~ElevateMe.vbs"
    del "%temp%\~ElevateMe.vbs"
goto :eof

:payload
    echo %~nx0: running payload with parameters:
    echo %*
    echo ---------------------------------------------------
    cd /d %2
    shift
    shift
    rem put your code here
    call scripts\env.bat
    python rundb.pyc
    rem e.g.: perl myscript.pl %1 %2 %3 %4 %5 %6 %7 %8 %9
goto :eof