# backend/app.py (ОБНОВЛЕННЫЙ И УПРОЩЕННЫЙ КОД)

# Просто импортируем функцию create_app из пакета backend
from . import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)