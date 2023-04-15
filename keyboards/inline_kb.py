
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Кнопки для вибору майстра
masters_kb = InlineKeyboardMarkup(row_width=2)
masters_kb.add(InlineKeyboardButton('Майстер 1', callback_data='master_1'),
              InlineKeyboardButton('Майстер 2', callback_data='master_2'),
              InlineKeyboardButton('Майстер 3', callback_data='master_3'),
              InlineKeyboardButton('Майстер 4', callback_data='master_4'))