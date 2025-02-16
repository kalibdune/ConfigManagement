# Вариант № 14
Разработать инструмент командной строки для визуализации графа
зависимостей, включая транзитивные зависимости. Сторонние средства для
получения зависимостей использовать нельзя.
Зависимости определяются для **git-репозитория**. Для описания графа
зависимостей используется представление **Graphviz**. Визуализатор должен
выводить результат на экран в виде кода.
Построить граф зависимостей для коммитов, в узлах которого содержатся
сообщения. Граф необходимо строить только для тех коммитов, где фигурирует
файл с заданным хеш-значением.
Конфигурационный файл имеет формат **json** и содержит:
- Путь к программе для визуализации графов.
- Путь к анализируемому репозиторию.
- Путь к файлу-результату в виде кода.
- Файл с заданным хеш-значением в репозитории.
Все функции визуализатора зависимостей должны быть покрыты тестами.


# Запуск работы
```bash
git clone <URL репозитория>
cd <директория проекта>
```

# Создайте виртуальное окружение
python -m venv venv

```bash
# Активируйте виртуальное окружение
python -m venv venv
# Для Windows:
venv\Scripts\activate
# Для MacOS/Linux:
source venv/bin/activate
```

## Запуск
```bash
python visualize_deps.py <config_path>
```

# 3. Структура проекта
Проект содержит следующие файлы и директории, связанные с тестированием:
```bash
main.py           # Файл с реализацией команд
test.py      # Файл с тестами для команд
```

# 4. Запуск тестов
В этом руководстве описывается, как запустить тесты для команд эмулятора оболочки. Мы будем использовать модуль Python `unittest` для тестирования.
```bash
python -m unittest test.py
```