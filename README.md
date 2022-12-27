# ZX_GIMP_plugins
Набор плагинов для графического редактора GIMP для работы с графикой ZX-spectrum
- files-zxspecrum-my.py - позволяет загружать и сохранять (экспорт) файлы в формате .scr (поддерживает "невидимые" пиксели (рисуются оранжевым цветом))
- zx-cheker.py - (добавляет меню ZX -> ZX Check) Проверяет изображение на конфликт цветов в знакоместах.
- zx-new-project.py - (добавляет меню ZX -> ZX New Project) создаёт холст 256х192 пикселя и настраивает сетку 8х8. Можно выбрать создание обычного слоя или двух слоёв (эмуляция атрибутов ink и paper) и альфа-маски слоя ink (битовое изображение).
- zx.pal и zx.gpl - палитры с цветами спектрума (+ "невидимый")

Для установки плагинов и палитры нужно просто их добавить в соответствующие каталоги.
Расположение каталогов можно посмотреть в GIMP-е в меню "Правка - Пеараметры - Каталоги - <нужный каталог>"
(для винды это, как правило C:/Users/<имя пользователя>/AppData/Roaming/GIMP/<версия gimp>/plug-ins и C:/Users/<имя пользователя>/AppData/Roaming/GIMP/<версия gimp>/palettes соответственно)
