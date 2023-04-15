import pytz
import os
from datetime import datetime, timedelta
from aiogram.types import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import exceptions, executor
from aiogram.utils.markdown import hbold, hitalic, hcode

# Часовий пояс (за замовчуванням - Kyiv)
TIMEZONE = os.getenv('TIMEZONE', 'Europe/Kiev')
tz = pytz.timezone(TIMEZONE)

# Функція для отримання зайнятого часу
def get_busy_times(date):
# Поточна дата та час
    now = datetime.now(tz=tz)
    date = datetime.strptime(date_str, '%d.%m')
# Якщо вказана дата - поточна дата, то зайняті часи - часи, які вже минули
    if date.date() == now.date():
        busy_times = [datetime.now(tz=tz) - timedelta(minutes=1)]
    else:
        busy_times = []

# Додавання прикладових зайнятих часів
    busy_times.append(datetime(date.year, date.month, date.day, 10, 0, tzinfo=tz))
    busy_times.append(datetime(date.year, date.month, date.day, 14, 30, tzinfo=tz))

    return busy_times




# Функція для отримання вільного часу
def get_free_time(date):
    free_times = []
    # Задаємо години роботи салону
    work_hours = {'start': 9, 'end': 18}

    # Отримуємо список вже зайнятих часів
    busy_times = get_busy_times(date)

    # Генеруємо список вільних часів
    for hour in range(work_hours['start'], work_hours['end']):
        for minute in [0, 30]:
            time = datetime(date.year, date.month, date.day, hour, minute, tzinfo=tz)
            if time not in busy_times:
                free_times.append(time)
    return free_times

# Якщо вказана дата - поточна дата, то зайняті часи - часи, які вже минули
    if date.date() == now.date():
        busy_times = [datetime.now(tz=tz) - timedelta(minutes=1)]
    else:
        busy_times = []


#Функція для форматування вільних часів

# def format_free_times(free_times):
#     if not free_times:
#         all_bussy = 'На жаль, на вказану дату вільних часів немає.'
#         return all_bussy
#
#
#     text = 'Виберіть час:\n'
#     for i, time in enumerate(free_times):
#         text += f"{i + 1}. {time.strftime('%H:%M')}\n"
#     return text


#Функція для відправки повідомлення про запис клієнту

# async def send_appointment_info(user_id: int, date: datetime, master: str, client_name: str, client_phone: str) -> None:
#     try:
#         # Отримуємо інформацію про час з введеного користувачем об'єкту datetime
#         time_info = date.strftime('%d.%m.%Y %H:%M')
#
#         # Формуємо повідомлення про запис
#         message = (
#             f"{hbold('Ваш запис на стрижку успішно збережено!')}\n\n"
#             f"{hbold('Дата та час:')} {time_info}\n"
#             f"{hbold('Майстер:')} {hitalic(master)}\n"
#             f"{hbold('Салон краси:')} {hitalic(SALON_INFO['назва'])}\n"
#             f"{hbold('Адреса:')} {hitalic(SALON_INFO['адреса'])}\n\n"
#             f"{hbold('Ваші дані:')} \n"
#             f"{hbold('Ім\'я:')} {hitalic(client_name)}\n"
#             f"{hbold('Номер телефону:')} {hitalic(client_phone)}\n\n"
#             f"{hitalic('Дякуємо, що обрали наш салон краси!')}"
#         )
#
#         # Відправляємо повідомлення клієнту
#         await bot.send_message(chat_id=user_id, text=message, parse_mode=ParseMode.HTML)
#
#         # Надсилаємо повідомлення нагадування за 2 години до запису
#         reminder_time = date - timedelta(hours=2)
#         await bot.send_message(chat_id=user_id, text=f"{hbold('Нагадування!')}\n\n"
#                                                      f"Через 2 години у Вас запис на стрижку у салоні краси {SALON_INFO['назва']}.\n"
#                                                      f"Дата та час: {reminder_time.strftime('%d.%m.%Y %H:%M')}\n"
#                                                      f"Майстер: {master}\n"
#                                                      f"Адреса: {SALON_INFO['адреса']}\n"
#                                                      f"Телефон: {SALON_INFO['телефон']}",
#                                parse_mode=ParseMode.HTML)
#
#     except exceptions.BotBlocked:
#         logging.warning(f"Користувач з ID '{user_id}' заблокував бота")
#     except exceptions.ChatNotFound:
#         logging.warning(f"Не вдалося знайти чат з ID '{user_id}'")
#     except exceptions.RetryAfter as e:
#         logging.error(f"Помилка Telegram API. Спробуйте знову через {e.timeout} секунд")
#     except exceptions.TelegramAPIError:
#         logging.exception(f"Помилка відправки повідомлення користувачу з ID '{user_id}'")
