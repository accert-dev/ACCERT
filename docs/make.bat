@ECHO OFF
SETLOCAL

pushd %~dp0

REM Command file for Sphinx documentation

if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)
set SOURCEDIR=source
set BUILDDIR=build

REM Check if sphinx-build is available
%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 (
	echo.
	echo The 'sphinx-build' command was not found. Make sure you have Sphinx
	echo installed, then set the SPHINXBUILD environment variable to point
	echo to the full path of the 'sphinx-build' executable. Alternatively you
	echo may add the Sphinx directory to PATH.
	echo.
	echo If you don't have Sphinx installed, grab it from
	echo https://www.sphinx-doc.org/
	exit /b 1
)

REM Define pre-build scripts
set PRE_BUILD_SCRIPTS=generate_sp_docs.py generate_main_docs.py

REM Define build command based on the first argument
if "%1" == "" goto help

REM Run pre-build scripts
echo Running pre-build scripts...
for %%S in (%PRE_BUILD_SCRIPTS%) do (
	if exist "%%S" (
		echo Running %%S...
		python "%%S"
		if errorlevel 1 (
			echo Error running %%S. Aborting build.
			exit /b 1
		)
	) else (
		echo Script %%S not found. Skipping.
	)
)

REM Proceed with Sphinx build
echo Building documentation...
%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
if errorlevel 1 (
	echo Sphinx build failed.
	exit /b 1
)
echo Sphinx build completed successfully.

goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%

:end
popd
ENDLOCAL
