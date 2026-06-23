@echo off
REM Member A: Train Object A (controller) with Nerfstudio Splatfacto on Windows.
REM Run from repository root, or let this script cd there automatically.
REM See: task1_3dgs_aigc/member_A/docs/runbook.md

cd /d "%~dp0..\..\..\"
call conda activate nerfstudio_gs

ns-train splatfacto ^
  --max-num-iterations 30000 ^
  --output-dir outputs/object_A_controller/nerfstudio_splatfacto ^
  --experiment-name controller ^
  --vis viewer ^
  colmap ^
  --data data/object_A_controller ^
  --images-path images ^
  --colmap-path sparse/0 ^
  --downscale-factor 1
