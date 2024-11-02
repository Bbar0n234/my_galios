import os
import sys
import warnings
warnings.filterwarnings("ignore", message="missing ScriptRunContext")

# Проверяем, если программа запущена через PyInstaller
if getattr(sys, 'frozen', False):
    # Получаем путь к временной директории, где PyInstaller распаковывает файлы
    base_path = sys._MEIPASS
else:
    # Если не через PyInstaller, просто используем текущую директорию
    base_path = os.path.abspath(".")

app_path = os.path.join(base_path, "app.py")

if __name__ == '__main__':
    os.system(f"streamlit run {app_path}")