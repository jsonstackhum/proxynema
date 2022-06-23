#!/bin/bash
echo "Создание виртуального окружения"
python3 -m venv env
echo "Активация окружения"
source env/bin/activate
echo "Установка зависимостей"
pip install -Ur requirements.txt
echo "Компилирование в исполняемый файл"
pyinstaller proxynema.py --onefile
echo "Деактивация окружения"
deactivate
echo "Копирование data-файлов"
cp geckodriver https_proxy.txt my_proxy.txt dist/
echo "Установка завершена. Запускайте файл proxynema из директории dist: ./proxynema" 
