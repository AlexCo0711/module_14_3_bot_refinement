# Домашнее задание по теме "Инлайн клавиатуры".

# импорт необходимых библиотек и методов
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
# блок из aiogram для работы с клавиатурой и объект кнопки
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import config


bot = Bot(token=config.TOKEN)
# переменная dp объекта «Dispatcher», у него наш бот в
# качестве аргументов. В качестве «Storage» будет «MemoryStorage»
dp = Dispatcher(bot, storage=MemoryStorage())
# Клавиатуры:

# Онлайн "главная" клавиатура:
kb_main = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Расчитать'),
            KeyboardButton(text='Информация')
        ],
        [KeyboardButton(text='Купить')]
    ], resize_keyboard=True, one_time_keyboard=True
)

# Инлайн клавиатуры:
# клавиатура выбора расчёта
kb_info = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories'),
            InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
        ]
    ]
)

# клавиаура выбора продукта:
kb_product = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Product1', callback_data='product_buying'),
            InlineKeyboardButton(text='Product2', callback_data='product_buying'),
            InlineKeyboardButton(text='Product3', callback_data='product_buying'),
            InlineKeyboardButton(text='Product4', callback_data='product_buying'),
        ]
    ]
)

# объявление класса состояния UserState наследованный от StatesGroup
class UserState(StatesGroup):
    # объявление объектов класса age, growth, weight, man (возраст, рост, вес, пол)
    age = State()
    growth = State()
    weight = State()

# обработчик начала общения с ботом (команды /start)
@dp.message_handler(commands=['start'])
# функция старта
async def start(message):
    # дополнение методом reply_markup для отображения клавиатуры kb
    await message.answer('Привет! Я бот помогающий вашему здоровью.\n'
                         'Нажмите одну из кнопок для продолжения', reply_markup=kb_main)


# обработчик ожидания нажатия кнопки «Расчитать»
@dp.message_handler(text=['Расчитать'], state=None)
# функция получения возраста пользователя
async def main_menu(message: types.Message, state: FSMContext):
    # ожидание нажатия кнопок выбора
    await message.answer('Выберите опцию:', reply_markup=kb_info)
    # ожидание останова данной функци
    await call.answer()


# обработчик ожидания нажатия кнопки «Формулы расчёта»
@dp.callback_query_handler(text=['formulas'])
# функция вывода расчётной формулы
async def get_formula(call: types.CallbackQuery):
    await call.message.answer('Формула расчёта Миффлина-Сан Жеора:\n'
                              '(10*вес + 6.25*рост + 5*возраст + 5) - для мужчин\n'
                              '(10*вес + 6.25*рост + 5*возраст - 161) - для женщин')
    # ожидание останова данной функци
    await call.answer()


# обработчик ожидания нажатия кнопки «Расчитать»
@dp.callback_query_handler(text=['calories'])
# функция получения возраста пользователя
async def set_age(call: types.CallbackQuery):
    # ожидание сообщения Calories и вывод текста
    await call.message.answer('Ваш возраст (полных лет):')
    # ожидание останова данной функци
    await call.answer()
    # ожидание ввода возраста
    await UserState.age.set()


# обработчик ожидания окончания статуса UserState.age
@dp.message_handler(state=UserState.age)
# функция получения роста пользователя
async def set_growth(message: types.Message, state: FSMContext):
    # ожидание сохранение сообщения возраста от пользователя в базе данных состояния
    await state.update_data(age_=message.text)
    # ожидание вывода текста
    await message.answer('Введите свой рост (см):')
    # ожидание ввода роста
    await UserState.growth.set()


# обработчик ожидания окончания статуса UserState.growth
@dp.message_handler(state=UserState.growth)
# функция получения веса пользователя
async def set_weight(message: types.Message, state: FSMContext):
    # ожидание сохранение сообщения роста от пользователя в базе данных состояния
    await state.update_data(growth_=message.text)
    # ожидание вывода текста
    await message.answer('Введите свой вес (кг):')
    # ожидание ввода веса
    await UserState.weight.set()


# обработчик ожидания окончания статуса UserState.weight и выбора пола пользователя
@dp.message_handler(state=UserState.weight)
# функция получения пола пользователя
async def set_weight(message: types.Message, state: FSMContext):
    # ожидание сохранение сообщения веса от пользователя в базе данных состояния
    await state.update_data(weight_=message.text)
    # сохранение полученных данных в переменной data
    data = await state.get_data()
    # подсчет согласно формуле Миффлина-Сан Жеора для мужчин
    calories = int(data['weight_']) * 10 + int(data['growth_']) * 6.25 - int(data['age_']) * 5 + 5
    # ожидание вывода текста результатов расчета
    await message.answer(f'Расчет проводится для пользователя мужского пола.\n'
                         f'Ваша норма калорий {calories} день', reply_markup=kb_main)
    await state.finish()


# обработчик кнопок Информация
@dp.message_handler(text=['Информация'])
# функция кнопок
async def inform(message):
    await message.answer("Бот поможет расчитать суточный рацион в калориях\n"
                         "для вашего возраста, роста, веса и пола", reply_markup=kb_main)

# обработчик ожидания нажатия кнопки «Купить»
@dp.message_handler(text=['Купить'])
# функция кнопок
async def get_buying_list(message):
    # цикл перебора вариантов продуктов
    for i in range (1, 5):
        # открытие файла изображения продукта
        with open(f'{i}.jpg', 'rb') as img:
            # ожидание отображения продукта
            await message.answer_photo(img)
        # ожидание вывода продукта
        await message.answer(f"Название: Product{i} | Описание: описание {i} | "
                                f"Цена: {i * 100}")
    await message.answer (text='Выберите продукт для покупки:', reply_markup=kb_product)

# обработчик ожидания нажатия кнопки выбранного продукта
@dp.callback_query_handler(text=['product_buying'])
async def send_confirm_message(call):
    with open("5.jpg", 'rb') as img0:
        await call.message.answer_photo(img0)
    await call.message.answer('Вы успешно приобрели продукт!')


# обработчик перехвата любых сообщений
@dp.message_handler()
# функция перехвата сообщений
async def all_messages(message):
    await message.answer('Введите команду /start, чтобы начать общение.')

if __name__ == '__main__':
    # запуск бота (dp - аргумент через что стартовать)
    executor.start_polling(dp, skip_updates=True)
