import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from aiogram.enums import ParseMode
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types.input_file import FSInputFile

from database.repo import CategoryRepo, ProductRepo, AnswerRepo

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

bot = Bot(token="8523362129:AAG1AmSpjCEYVx2V42IA2_jjugq_pGhAb8g")
dp = Dispatcher()

# Константы для ответов
PRICE_ANSWER = (
    "Заполнение декларации 500 руб.\n"
    "Консалтинг 10000 руб.\n"
    "Составление проекта договора – 5000 р.\n"
    "Юридическая экспертиза документа: 8000 р."
)

WORKING_HOURS_ANSWER = "🕐 Время работы: с 9:00 до 18:00, пн-пт"

CONTACTS_ANSWER = (
    "📞 Контакты:\n"
    "Телефон: +79089458176\n"
    "Email: info@company.com\n"
    "Адрес: г.Кемерово , Кузнецкий 17"
)

HELP_ANSWER = (
    "📋 Я понимаю следующие вопросы:\n\n"
    "• «Стоимость услуг компании?» или «Цены»\n"
    "• «Время работы компании» или «График работы»\n"
    "• «Контакты» или «Как связаться?»\n"
    "• «Помощь» или «Что ты умеешь?»\n\n"
    "💬 Для получения персонального ответа используйте команду /свой_вопрос\n\n"
)


class MyStates(StatesGroup):
    cat = State()
    product = State()
    q2 = State()
    waiting_for_question = State()  # Состояние ожидания вопроса от пользователя


cat_repo = CategoryRepo()
product_repo = ProductRepo()
answer_repo = AnswerRepo()


def normalize(text: str) -> str:
    """Нормализация текста для сравнения"""
    return text.strip().lower()


@dp.message(CommandStart())
async def start_bot(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    logger.info(f"User {message.from_user.id} started the bot")
    items = cat_repo.get_all()
    await state.set_state(MyStates.cat)
    
    welcome_text = (
        "👋 Здравствуйте! Я бот компании.\n\n"
        "Вы можете:\n"
        "• Просмотреть каталог товаров (выберите категорию ниже)\n"
        "• Задать вопросы о ценах, наличии, времени работы\n"
        "• Узнать контакты компании\n\n"
        "Используйте /help для списка доступных команд."
    )
    
    if items:
        inline_kb_list = [
            [
                InlineKeyboardButton(
                    text=i["name"],
                    callback_data=str(i["id"]),
                )
            ] for i in items
        ]
        await message.answer(
            welcome_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_kb_list),
        )
    else:
        await message.answer(
            welcome_text + "\n\n⚠️ Категории товаров пока не добавлены."
        )


@dp.callback_query(MyStates.cat)
async def choose_product_by_cat(callback: CallbackQuery, state: FSMContext):
    items = product_repo.get_by_category(int(callback.data))
    await state.set_state(MyStates.product)
    
    if not items:
        await callback.message.answer(
            "⚠️ В этой категории пока нет товаров.\n\n"
            "Используйте /start для возврата к списку категорий."
        )
        await state.set_state(MyStates.cat)
        return
    
    inline_kb_list = [
        [
            InlineKeyboardButton(
                text=i["name"],
                callback_data=str(i["id"]),
            )
        ] for i in items
    ]
    await callback.message.answer(
        "Выберите товар",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_kb_list),
    )


@dp.callback_query(MyStates.product)
async def choose_product_by_cat(callback: CallbackQuery, state: FSMContext):
    item = product_repo.get_by_id(int(callback.data))
    if not item:
        await callback.message.answer("❌ Товар не найден")
        return
    item = item[0]
    await state.clear()
    items = cat_repo.get_all()
    await state.set_state(MyStates.cat)
    
    product_info = (
        f"<b>📦 {item['name']}</b>\n\n"
        f"💰 <b>Цена:</b> {item['price']} руб.\n"
        f"📝 <b>Описание:</b> {item['description']}\n"
        f"📊 <b>В наличии:</b> {item['cnt']} шт."
    )
    
    await callback.message.answer(
        product_info,
        parse_mode=ParseMode.HTML,
    )
    
    if items:
        inline_kb_list = [
            [
                InlineKeyboardButton(
                    text=i["name"],
                    callback_data=str(i["id"]),
                )
            ] for i in items
        ]
        await callback.message.answer(
            "Выберите категорию товаров",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_kb_list),
        )


@dp.message(Command("help"))
async def help_command(message: Message):
    """Обработчик команды /help"""
    logger.info(f"User {message.from_user.id} requested help")
    await message.answer(HELP_ANSWER)


@dp.message(Command("свой_вопрос"))
async def custom_answer_command(message: Message, state: FSMContext):
    """Обработчик команды 'свой вопрос'"""
    logger.info(f"User {message.from_user.id} started custom answer")
    await state.set_state(MyStates.waiting_for_question)
    await message.answer(
        "💬 Напишите ваш вопрос, и мы обязательно на него ответим!\n\n"
        "Ваш вопрос будет передан администратору для обработки."
    )


@dp.message(MyStates.waiting_for_question)
async def save_question(message: Message, state: FSMContext):
    """Сохранение вопроса пользователя в базу данных"""
    if not message.text:
        await message.answer("Пожалуйста, отправьте текстовое сообщение с вашим вопросом.")
        return
    
    try:
        question_text = message.text.strip()
        user_id = message.from_user.id
        
        # Сохраняем вопрос в базу данных
        answer_repo.add_question(question_text, user_id)
        
        await message.answer(
            "✅ Ваш вопрос принят! Мы обработаем его в ближайшее время и отправим вам ответ.\n\n"
            "Используйте /start для возврата в главное меню."
        )
        logger.info(f"Question saved from user {user_id}: {question_text[:50]}...")
        
        await state.clear()
    except Exception as e:
        logger.error(f"Error saving question: {e}")
        await message.answer(
            "❌ Произошла ошибка при сохранении вопроса. Попробуйте позже."
        )
        await state.clear()


@dp.message(F.text & ~F.text.startswith("/"))
async def handle_question(message: Message, state: FSMContext):
    """Обработчик текстовых сообщений с вопросами"""
    if not message.text:
        return
    
    text = normalize(message.text)
    logger.info(f"User {message.from_user.id} asked: {message.text}")
    
    # Вопросы о стоимости услуг
    if any(phrase in text for phrase in [
        "стоимость услуг", "стоимость услуг компании", "цены", 
        "сколько стоит", "прайс", "цена"
    ]):
        await message.answer(PRICE_ANSWER)
        return
    
    # Вопросы о времени работы
    if any(phrase in text for phrase in [
        "время работы", "график работы", "когда работаете", 
        "режим работы", "часы работы"
    ]):
        await message.answer(WORKING_HOURS_ANSWER)
        return
    
    # Вопросы о категориях
    if any(phrase in text for phrase in [
        "какие категории", "список категорий", "категории товаров",
        "что есть", "какие товары"
    ]):
        categories = cat_repo.get_all()
        if categories:
            cat_list = "📂 <b>Категории товаров:</b>\n\n"
            for cat in categories:
                products_count = len(product_repo.get_by_category(cat["id"]))
                cat_list += f"• {cat['name']} ({products_count} товаров)\n"
            await message.answer(cat_list, parse_mode=ParseMode.HTML)
        else:
            await message.answer("📦 Категории пока не добавлены.")
        return
    
    # Вопросы о наличии товара
    if any(phrase in text for phrase in [
        "есть ли", "наличие", "в наличии", "есть товар", "доступен"
    ]):
        # Пытаемся найти упоминание названия товара
        products = product_repo.get_all()
        found_products = []
        
        for product in products:
            if normalize(product["name"]) in text:
                found_products.append(product)
        
        if found_products:
            answer = "📦 <b>Наличие товаров:</b>\n\n"
            for product in found_products[:5]:
                status = "✅ В наличии" if product["cnt"] > 0 else "❌ Нет в наличии"
                answer += f"• <b>{product['name']}</b>: {status} ({product['cnt']} шт.)\n"
            await message.answer(answer, parse_mode=ParseMode.HTML)
        else:
            await message.answer(
                "🔍 Уточните название товара. Например: 'Есть ли товар [название]?'\n\n"
                "Или используйте /start для просмотра каталога."
            )
        return
    
    # Вопросы о контактах
    if any(phrase in text for phrase in [
        "контакты", "как связаться", "телефон", "адрес", 
        "где находитесь", "как доехать"
    ]):
        await message.answer(CONTACTS_ANSWER)
        return
    
    # Вопросы о помощи
    if any(phrase in text for phrase in [
        "помощь", "что ты умеешь", "что можешь", "команды"
    ]):
        await message.answer(HELP_ANSWER)
        return
    
    # Если вопрос не распознан
    await message.answer(
        "❓ Я не понял ваш вопрос.\n\n" + HELP_ANSWER
    )