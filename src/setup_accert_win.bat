@echo off

rem Step 1: Gather workbench_path from workbench.sh
set workbench_path=
for /f "delims=" %%a in (workbench.sh) do (
  set "line=%%a"
  if "!line:workbench_path="=="!line!" goto continue
  set workbench_path=!line:*=!
)
:continue

rem Step 2: Check that workbench_path was retrieved
if "%workbench_path%" == "" (
  echo ERROR: workbench_path not found in workbench.sh
  exit /b 1
)

rem Step 3: Check that retrieved path has subfolders
if not exist "%workbench_path%\*" (
  echo ERROR: "%workbench_path%" does not contain any subfolders
  exit /b 1
)

rem Step 4: Find conda
set "conda_path=%workbench_path%\rte\conda"

rem Step 5: Set ACCERT_DIR to current directory
set "ACCERT_DIR=%cd%"

rem Step 6: Use the pip in conda/bin to install requirement.txt located in the parent folder of this shell script
%conda_path%\Scripts\pip.exe install -r ..\requirement.txt

rem Step 7: Create another file called 'install.conf' in current folder with the following contents:
echo [INSTALL] > install.conf
echo PASSWD = yourpassword >> install.conf
echo ^# NOTE: ALL OTHER information should be set up later >> install.conf
echo ^# INSTALL_PATH = /usr/local >> install.conf
echo ^# DATADIR =/mysql/data >> install.conf
echo ^# INSTALL_PACKAGE = >> install.conf
echo ^# EXP_DIR = >> install.conf

rem Step 8: cd into the parent folder of ACCERT_DIR
cd ..

rem Step 9: Copy docprint and sonvalidxml into ACCERT using following commands:
copy "%ACCERT_DIR%\src\etc\accert_wb.py" "%workbench_path%\rte\accert.py"
if not exist bin mkdir bin
copy "%workbench_path%\bin\sonvalidxml" "bin\sonvalidxml"
copy "%workbench_path%\bin\docprint" "bin\docprint"

rem Step 10: Confirm the install process is finished
echo Installation process is finished.

rem Step 11: Remind the user to change the password in install.conf
echo Please change the "yourpassword" of 'install.conf' to your MySQL root password.
pause
