@echo off
for %%m in (fw.bin) do (
if %%~zm EQU 1479168 goto :s1479168
if %%~zm EQU 1544704 goto :s1544704
goto :ends
)

:s1479168
copy /b 0m + fw.bin + 2 fw.exe
goto :end

:s1544704
cls
color 0C
echo Error! Firmware file size must be 1479168 Bytes or less, learn readme for details
echo Ошибка! Файл прошивки не должен превышать размер в 1479168 байт. Подробности в readme
pause
goto :end

:ends
cls
color 0C
echo Error! Firmware file fw.bin not found. Rename firmware image file to fw.bin and place it in this directory.
echo Ошибка! Файл прошивки fw.bin не найден. Переименуйте файл прошивки в fw.bin и поместите в этот каталог.
pause

:end
color 07
