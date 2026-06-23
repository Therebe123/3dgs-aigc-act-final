@echo off
REM Member A: Export trained Splatfacto checkpoint to Gaussian PLY on Windows.
REM Set LOAD_CONFIG and OUTPUT_DIR before running, for example:
REM   set LOAD_CONFIG=outputs\object_A_controller\nerfstudio_splatfacto\controller\splatfacto\<timestamp>\config.yml
REM   set OUTPUT_DIR=outputs\object_A_controller\exports\controller_gaussian_splat
REM See: task1_3dgs_aigc/member_A/docs/runbook.md

cd /d "%~dp0..\..\..\"
call conda activate nerfstudio_gs

if "%LOAD_CONFIG%"=="" (
  echo ERROR: Set LOAD_CONFIG to the splatfacto config.yml path.
  exit /b 1
)
if "%OUTPUT_DIR%"=="" (
  echo ERROR: Set OUTPUT_DIR to the export directory.
  exit /b 1
)

ns-export gaussian-splat ^
  --load-config "%LOAD_CONFIG%" ^
  --output-dir "%OUTPUT_DIR%"
