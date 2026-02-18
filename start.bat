@echo off
chcp 65001 >nul
cd /d d:\PytorchNode
python main.py
if errorlevel 1 (
    echo.
    echo 程序运行出错，请检查错误信息
    pause
)
