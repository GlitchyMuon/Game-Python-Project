@echo off
echo ImageMagick is fixing libpng warning
set fn = $PATH\convert.exe
for /f "tokens=*" %%i in ('dir/s/b *.png') do "%fn%" "%%i" -strip "%%i"
pause