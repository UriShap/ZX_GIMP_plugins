#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gimpfu import *


def zx_check(image, drawable):
  pdb.gimp_context_push()
  pdb.gimp_image_undo_group_start(image)
  pdb.gimp_selection_none(image)
  maxY = pdb.gimp_drawable_height(drawable)
  maxX = pdb.gimp_drawable_width(drawable)
  y=0		
  while y <= maxY-8:
	x=0
	while x <= maxX-8:
		color1 = pdb.gimp_drawable_get_pixel(drawable, x, y)[1]
		color2 = color1
		marked = False
		for j in range (y, y+8):
			for i in range (x, x+8):
				color0 = pdb.gimp_drawable_get_pixel(drawable, i, j)[1]
				if color0 != color1:
					if color0 != color2:
						if color1 == color2:
							color2 = color0
							maxc1=max(color1[0], color1[1], color1[2])
							maxc2=max(color2[0], color2[1], color2[2])
							if maxc1 !=0 and maxc2 !=0 and maxc1 != maxc2:
								pdb.gimp_image_select_rectangle (image, 0, x, y, 8, 8)
								marked=True
								break
						else:
							pdb.gimp_image_select_rectangle (image, 0, x, y, 8, 8)
							marked=True
							break
			if marked:
				break
		x=x+8
 	y=y+8
  pdb.gimp_image_undo_group_end(image)
  pdb.gimp_context_pop()

register(
          "python-fu-zx-checker", # Имя регистрируемой функции
          "Проверка соответствия изображения формату ZX Spectrum-а", # Информация о дополнении
          "Проверяет наличие не более 2-х цветов на знакоместо 8*8 c учётом яркости", # Короткое описание выполняемых скриптом действий
          "Юрий Шаповалов", # Информация об авторе
          "Юрий Шаповалов (urishap@mail.ru)", # Информация о копирайте (копилефте?)
          "25.05.2022", # Дата изготовления
          "ZX Check", # Название пункта меню, с помощью которого дополнение будет запускаться
          "*", # Типы изображений с которыми может работать дополнение
          [
              (PF_IMAGE, "image", "Исходное изображение", None), # Указатель на изображение
              (PF_DRAWABLE, "drawable", "Исходный слой", None), # Указатель на слой              
          ],
          [], # Список переменных которые вернет дополнение
          zx_check, 
	  menu="<Image>/ZX/") # Имя исходной функции и меню в которое будет помещён пункт запускающий дополнение
main()