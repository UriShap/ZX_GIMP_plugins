#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gimpfu import *

def zx_new_project(zxtype):
  pdb.gimp_context_push()
  image = pdb.gimp_image_new(256, 192, RGB)
  layer = pdb.gimp_layer_new(image, 256, 192, RGB_IMAGE, "ZX scr", 100, NORMAL_MODE)
  pdb.gimp_image_insert_layer(image, layer, None, 0)
  pdb.gimp_edit_clear(layer)
  if zxtype==1:
	pdb.gimp_item_set_name(layer, "ZX paper")
        layer2 = pdb.gimp_layer_new(image, 256, 192, RGB_IMAGE, "ZX ink", 100, NORMAL_MODE)
	mask = pdb.gimp_layer_create_mask(layer2, ADD_MASK_BLACK)
	pdb.gimp_layer_add_mask(layer2, mask)
  	pdb.gimp_image_insert_layer(image, layer2, None, 0)
	pdb.gimp_context_swap_colors()
  	pdb.gimp_edit_clear(layer2)
	pdb.gimp_context_swap_colors()

  pdb.gimp_image_grid_set_foreground_color(image, (128,64,0))
  pdb.gimp_image_grid_set_spacing(image, 8, 8)

  display = pdb.gimp_display_new(image)

  pdb.gimp_context_pop()

register(
          "python-fu-zx-new-project", # Имя регистрируемой функции
          "Создание нового проекта для ZX Spectrum", # Информация о дополнении
          "Создаёт изображение 256х192, настраивает сетку 8*8", # Короткое описание выполняемых скриптом действий
          "Юрий Шаповалов", # Информация об авторе
          "Юрий Шаповалов (urishap@mail.ru)", # Информация о копирайте (копилефте?)
          "25.05.2022", # Дата изготовления
          "ZX New Project", # Название пункта меню, с помощью которого дополнение будет запускаться
          "", # Типы изображений с которыми может работать дополнение
          [
	      (PF_TOGGLE, "zxtype", "Разделить ink и paper по слоям", 1)
	  ],
          [
              (PF_IMAGE, "image", "Созданное изображение"), # Указатель на изображение
              (PF_DRAWABLE, "layer", "Созданный слой"), # Указатель на слой              
              (PF_DISPLAY, "display", "Отображение")
	  ], # Список переменных которые вернет дополнение
          zx_new_project, menu="<Image>/ZX/") # Имя исходной функции и меню в которое будет помещён пункт запускающий дополнение

main()