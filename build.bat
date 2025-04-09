@echo off

::解决方案路径
set "SOLUTION_PATH=.\Project1.sln"
:: 编译配置 
set "BUILD_CONFIG=Release"         
:: 编译平台      
set "BUILD_PLATFORM=ARM64"
:: 编译日志路径 
set "MSBUILD_LOG=..\output\build_log.txt"      
:: 设置输出目录
set "OUTPUT_DIR=D:\Jenkins\output"

echo.
echo [VS2022 Auto compilation]
echo ===============================

:: 1.检查解决方案文件 
if not exist %SOLUTION_PATH% (
    echo Error: Solution file does not exist [%SOLUTION_PATH%]
    exit /b 1
)
echo The solution file is verified. Procedure

:: 2.加载VS2022环境变量
call "%ProgramFiles%\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" %BUILD_PLATFORM%
if %errorlevel% neq 0 (
    echo Error: The VS2022 environment failed to load
    exit /b 1
)
echo The VS2022 environment is successfully loaded. 

:: 3.查找MSBuild
set MSBUILD_PATH="%ProgramFiles%\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe"
if not exist %MSBUILD_PATH% (
    echo Error: MSBuild.exe not found
    exit /b 1
)
echo MSBuild path: %MSBUILD_PATH%

:: 4.执行编译
echo.
echo Start compiling [%SOLUTION_PATH%]
echo Log output to: %MSBUILD_LOG%
echo ===============================

%MSBUILD_PATH% %SOLUTION_PATH% ^
 /p:Configuration=%BUILD_CONFIG% ^
 /p:Platform=%BUILD_PLATFORM% ^
 /p:OutDir="%OUTPUT_DIR%" ^
 /t:Rebuild ^
 /flp:LogFile=%MSBUILD_LOG%;Verbosity=detailed ^
 /nr:false

:: 5.检查编译结果
if %errorlevel% equ 0 (
    echo.
    echo Compile successfully!
    echo Output directory: %BUILD_CONFIG%\%BUILD_PLATFORM%\
) else (
    echo.
    echo Compile failed! Error code: %errorlevel% 
    type %MSBUILD_LOG% | findstr /i error
    exit /b 1
)

