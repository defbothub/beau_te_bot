import logging
import pytz
import os
from datetime import datetime, timedelta
from data.config import API_TOKEN, SALON_INFO
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
from keyboards.inline_kb import masters_kb

logging.basicConfig(level=logging.INFO)

# ініціалізація

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Часовий пояс (за замовчуванням - Kyiv)
TIMEZONE = os.getenv('TIMEZONE', 'Europe/Kiev')
tz = pytz.timezone(TIMEZONE)


# cтворення стану для запису на стрижку

class AppointmentForm(StatesGroup):
    name = State()
    phone = State()
    date = State()
    master = State()
    time = State()


# Команда для початку запису на стрижку

@dp.message_handler(commands=['start'])
async def start_appointment(message: types.Message):
    await message.answer(f"Вітаємо в {SALON_INFO['назва']}!\n"
                         f"Для запису на стрижку натисніть кнопку нижче та виберіть вільний час.\n"
                         f"Наша адреса: {SALON_INFO['адреса']}\n"
                         f"Наш телефон: {SALON_INFO['телефон']}",
                         )
    await bot.send_message(message.from_user.id, "Введіть ім'я.")
    await AppointmentForm.name.set()


@dp.message_handler(state=AppointmentForm.name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
        await AppointmentForm.next()
        print(message.text)
        await message.answer("Введіть свій номер телефону")


# Обробник введення номеру телефону

@dp.message_handler(state=AppointmentForm.phone)
async def process_phone(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone'] = message.text
        await AppointmentForm.next()
        print(message.text)
        await message.answer("Введіть дату запису (наприклад, 27.03)")


# Обробник введення дати
@dp.message_handler(state=AppointmentForm.date)
async def process_date(message: types.Message, state: FSMContext):
    date_str = message.text
    try:
        # Перевіряємо, чи введена коректна дата
        date = datetime.strptime(date_str, '%d.%m.%y')
        if date < datetime.now():
            raise ValueError
    except ValueError:
        await message.answer("Будь ласка, введіть коректну дату у форматі ДД.ММ.PP (наприклад, 27.03.23)")
    else:
        async with state.proxy() as data:
            data['date'] = date
        busy_times = await get_busy_time(data['date'])
        await AppointmentForm.next()
        await message.answer("Оберіть майстра.", reply_markup=masters_kb)


# Функція для отримання зайнятого часу
async def get_busy_time(date):
    # Поточна дата та час
    now = datetime.now(tz=tz)
    # Якщо вказана дата - поточна дата, то зайняті часи - часи, які вже минули
    if date.date() == now.date():
        busy_times = [datetime.now(tz=tz) - timedelta(minutes=1)]
    else:
        busy_times = []
    return busy_times


# Функція для отримання вільного часу
async def get_free_time(date):
    free_times = []
    #date_str = data['date']
    # Задаємо години роботи салону
    work_hours = {'start': 9, 'end': 18}
    # Отримуємо список вже зайнятих часів
    busy_times = await get_busy_time(date)
    # Генеруємо список вільних часів
    for hour in range(work_hours['start'], work_hours['end']):
        for minute in [0, 30]:
            date_str = "09-03-23"
            date = datetime.strptime(date_str, "%d-%m-%y").date()
            now = datetime.combine(date, datetime.min.time())
            time = datetime(now.year, now.month, now.day, hour, minute, tzinfo=tz)
            if time not in busy_times:
                free_times.append(time)
    return free_times

# Функція форматування списку майстрів у вигляді кнопок
def format_masters(masters):
    keyboard = InlineKeyboardMarkup()
    for master in masters:
        button = InlineKeyboardButton(text=master, callback_data=f"master_{master}")
        keyboard.add(button)
    return keyboard


# Функція форматування вільних часів у вигляді кнопок
async def format_free_times(times):
    keyboard_time = InlineKeyboardMarkup()
    for time in times:
        button = InlineKeyboardButton(text=time, callback_data=f"time_{time}")
        keyboard_time.add(button)
    return keyboard_time


# Обробник введення майстра
@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('master_'),
                           state=AppointmentForm.master)
async def process_master(callback_query: types.CallbackQuery, state: FSMContext):
    master = callback_query.data.split('_')[1]
    async with state.proxy() as data:
        data['master'] = master
        # Відправляємо запит на вільні дати та часи для вибраного майстра
        free_times = get_free_time(master)
        if not free_times:
            await callback_query.message.answer(
                f"На жаль, у {master} немає вільного часу. Будь ласка, виберіть іншого майстра.")
            # Очищаємо стан
            await state.finish()
            return
        # Форматуємо список вільних дат та часів у вигляді кнопок
        keyboard_time = format_free_times(free_times)
        # Відправляємо список вільних дат та часів клієнту
        await callback_query.message.answer("Виберіть зручний для вас час:", reply_markup=keyboard_time)
        # Зберігаємо майстра у стані
        await AppointmentForm.master.set()


# Обробник введення часу
@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('time_'), state=AppointmentForm.time)
async def process_time(callback_query: types.CallbackQuery, state: FSMContext):
    time = callback_query.data.split('_')[1]
    async with state.proxy() as data:
        data['time'] = time
        salon_info = SALON_INFO
        date_time_str = f"{data['date']} {time}"
        date_time = datetime.strptime(date_time_str, '%d.%m.%y %H:%M')
        # Відправляємо підтвердження запису
        message_text = f"Ваша заявка на {date_time.strftime('%d.%m.%y %H:%M')} прийнята.\n" \
                       f"{salon_info['назва']}\n" \
                       f"{salon_info['адреса']}\n" \
                       f"{salon_info['телефон']}\n" \
                       f"Будь ласка, з'явіться у вказаний час."
        await callback_query.message.answer(message_text, parse_mode=ParseMode.HTML)
        await bot.send_message(chat_id=user_id, text=message_text, parse_mode=ParseMode.HTML)
        # Очистити стан
        await state.finish()


if __name__ == "__main__":
    executor.start_polling(dispatcher=dp, skip_updates=True)
