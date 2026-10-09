<div align="center">

<img src="icon.ico" alt="MyLauncher" width="120" height="120">

# MyLauncher

**Современный игровой лаунчер для Windows**  
Все программы, игры и утилиты в одном месте.

[![Версия](https://img.shields.io/github/v/release/Mystiq-Tech-IS/my-launcher?style=for-the-badge&color=89B4FA&label=%D0%92%D0%B5%D1%80%D1%81%D0%B8%D1%8F)](https://github.com/Mystiq-Tech-IS/my-launcher/releases/latest)
[![Платформа](https://img.shields.io/badge/Windows-10%2F11-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/Mystiq-Tech-IS/my-launcher/releases/latest)
[![Лицензия](https://img.shields.io/badge/%D0%9B%D0%B8%D1%86%D0%B5%D0%BD%D0%B7%D0%B8%D1%8F-MIT-A6E3A1?style=for-the-badge)](LICENSE)

[**📥 Скачать**](https://github.com/Mystiq-Tech-IS/my-launcher/releases/latest) · [**🐛 Баг-репорт**](https://github.com/Mystiq-Tech-IS/my-launcher/issues/new) · [**💡 Предложить идею**](https://github.com/Mystiq-Tech-IS/my-launcher/issues/new)

</div>

---

## ✨ Возможности

### 🎮 Организация программ
- **Плитки программ** с иконками, обложками и статусом
- **Категории**: Все, Недавние, Игры, Работа, Система, Прочее
- **Избранное** с фильтром одной кнопкой
- **Подкатегории** внутри категорий
- **Drag & drop** для перестановки карточек

### 🚀 Быстрый запуск
- **Spotlight-поиск** (`Ctrl+Alt+Space`) — запуск любой программы за 2 секунды
- **Глобальные хоткеи** для любой программы
- **Пресеты запуска** — одна кнопка запускает несколько программ
- **Цифры 1–9** для запуска первых плиток

### 🎨 Внешний вид
- **Тёмная и светлая темы**
- **6 пресетов акцента** + кастомный HEX
- **Кастомный фон**: частицы, градиент, изображение, GIF или видео
- **Прозрачность окна** от 60% до 100%
- **Масштабирование** плиток и иконок

### ⚙️ Дополнительно
- **Мониторинг системы** — CPU / RAM / GPU в реальном времени
- **Discord Rich Presence** — статус в профиле
- **Спутники запуска** — Steam запускает Discord
- **Плагины** — расширение функционала
- **Статистика** — топ программ, категории, графики за 30 дней

---

## 📥 Установка

### Готовая сборка (рекомендуется)

1. Скачай **[MyLauncher.exe](https://github.com/Mystiq-Tech-IS/my-launcher/releases/latest)** из последнего релиза.
2. Положи в любую папку (например, `C:\MyLauncher\`).
3. Запусти двойным кликом.

> **⚠ Windows SmartScreen может предупредить:** «Windows защитила ваш компьютер».
> Это нормально для новых программ без платной цифровой подписи.
> Нажми **«Подробнее» → «Выполнить в любом случае»**.

### Из исходников

```bash
git clone https://github.com/Mystiq-Tech-IS/my-launcher.git
cd my-launcher
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py