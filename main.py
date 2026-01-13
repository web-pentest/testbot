import asyncio
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8380347594:AAHspMSedFuGf4C--xOvd6d56KJv8617Q6s"
ADMIN_ID = 0 # ТВОЙ ID ИЗ СКРИНШОТА (уже вставил)
ADMIN_PASS = "Business"

bot = Bot(token=TOKEN)
dp = Dispatcher()

users_db = {} 
likes_db = {} 

FACULTIES = ["💊 Фармация", "📊 Экономика", "🚚 Логистика", "🏦 Банк", "🛍 Торговля", "⚖️ Юрист", "✈️ Туризм", "💄 Красота"]
GOALS = ["❤️ Найти любовь", "🤝 Дружба", "📚 Учеба"]

class Registration(StatesGroup):
    waiting_for_password = State()
    name = State()
    age = State()
    faculty = State()
    hobbies = State()
    goal = State()
    photo = State()

# --- КЛАВИАТУРЫ ---
def main_menu(user_id):
    buttons = [
        [KeyboardButton(text="🔍 Поиск"), KeyboardButton(text="👤 Моя анкета")],
        [KeyboardButton(text="ℹ️ Помощь")]
    ]
    # Если зашел админ — добавляем ему спец-кнопку
    if user_id == ADMIN_ID:
        buttons.append([KeyboardButton(text="🛠 Админ-панель")])
        
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# --- ЛОГИКА СТАРТА ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    if message.from_user.id == ADMIN_ID:
        await message.answer(f"👋 Привет, создатель! Ты узнан автоматически.", reply_markup=main_menu(message.from_user.id))
    else:
        await message.answer("🔐 v1.0 - КГП LOVE\n\nВведите пароль для доступа к анкетам:")
        await state.set_state(Registration.waiting_for_password)

@dp.message(Registration.waiting_for_password)
async def check_pass(message: types.Message, state: FSMContext):
    if message.text == ADMIN_PASS:
        await message.answer("✅ Доступ открыт! Как тебя зовут?")
        await state.set_state(Registration.name)
    else:
        await message.answer("❌ Неверный пароль.")

# --- ПРОЦЕСС РЕГИСТРАЦИИ ---
@dp.message(Registration.name)
async def reg_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("🔢 Сколько тебе лет?")
    await state.set_state(Registration.age)

@dp.message(Registration.age)
async def reg_age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=f)] for f in FACULTIES], resize_keyboard=True)
    await message.answer("🎓 Выбери свой факультет:", reply_markup=kb)
    await state.set_state(Registration.faculty)

@dp.message(Registration.faculty)
async def reg_fac(message: types.Message, state: FSMContext):
    await state.update_data(faculty=message.text)
    await message.answer("🎨 Расскажи о своих хобби:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Registration.hobbies)

@dp.message(Registration.hobbies)
async def reg_hob(message: types.Message, state: FSMContext):
    await state.update_data(hobbies=message.text)
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=g)] for g in GOALS], resize_keyboard=True)
    await message.answer("🎯 Какая цель твоего знакомства?", reply_markup=kb)
    await state.set_state(Registration.goal)

@dp.message(Registration.goal)
async def reg_goal(message: types.Message, state: FSMContext):
    await state.update_data(goal=message.text)
    await message.answer("📸 Скинь свое лучшее фото:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Registration.photo)

@dp.message(Registration.photo, F.photo)
async def reg_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    users_db[message.from_user.id] = {
        **data, 
        "photo": message.photo[-1].file_id, 
        "username": message.from_user.username
    }
    await message.answer("🎉 Ура! Твоя анкета создана!", reply_markup=main_menu(message.from_user.id))
    await state.clear()

# --- ПРОСМОТР СВОЕЙ АНКЕТЫ ---
@dp.message(F.text == "👤 Моя анкета")
async def my_profile(message: types.Message):
    uid = message.from_user.id
    if uid not in users_db:
        return await message.answer("🤔 Твоей анкеты еще нет. Нажми /start")
    
    p = users_db[uid]
    caption = (
        f"✨ ТВОЯ АНКЕТА ✨\n"
        f"━━━━━━━━━━━━━━\n"
        f"👤 Имя: {p['name']}, {p['age']}\n"
        f"🎓 Факультет: {p['faculty']}\n"
        f"🎯 Цель: {p['goal']}\n"
        f"🎭 Хобби: {p['hobbies']}\n"
        f"━━━━━━━━━━━━━━"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🗑 Удалить анкету", callback_data="del_my")]])
    await message.answer_photo(p['photo'], caption=caption, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "del_my")
async def del_my(callback: types.CallbackQuery):
    users_db.pop(callback.from_user.id, None)
    await callback.message.answer("❌ Твоя анкета удалена. Чтобы создать новую, нажми /start")
    await callback.answer()

# --- ПОИСК ---
@dp.message(F.text == "🔍 Поиск")
async def view_profiles(message: types.Message):
    others = [uid for uid in users_db if uid != message.from_user.id]
    if not others:
        return await message.answer("😔 Пока никого нет. Будь первым!")
    
    target_id = random.choice(others)
    p = users_db[target_id]
    
    caption = (
        f"💖 **КАК ТЕБЕ?**\n"
        f"━━━━━━━━━━━━━━\n"
        f"👤 {p['name']}, {p['age']}\n"
        f"🎓 {p['faculty']}\n"
        f"🎯 {p['goal']}\n"
        f"🎭 {p['hobbies']}"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="❤️ Лайк", callback_data=f"like_{target_id}"),
        InlineKeyboardButton(text="👎 Дальше", callback_data="next")
    ]])
    await message.answer_photo(p['photo'], caption=caption, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "next")
async def next_profile(callback: types.CallbackQuery):
    await callback.message.delete()
    await view_profiles(callback.message)

@dp.callback_query(F.data.startswith("like_"))
async def handle_like(callback: types.CallbackQuery):
    target_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    
    if user_id not in likes_db: likes_db[user_id] = []
    likes_db[user_id].append(target_id)

    # Проверка на взаимность
    if target_id in likes_db and user_id in likes_db[target_id]:
        await bot.send_message(user_id, f"🔥 ВЗАИМНО! Пиши скорее: @{users_db[target_id]['username']}")
        await bot.send_message(target_id, f"🔥 ВЗАИМНО! Пиши скорее: @{users_db[user_id]['username']}")
    else:
        try:
            await bot.send_message(target_id, "🔔 Кто-то оценил твою анкету! Нажми 'Поиск', чтобы найти его.")
        except: pass

    await callback.answer("Лайк отправлен!")
    await view_profiles(callback.message)

# --- АДМИН ПАНЕЛЬ (ИСПРАВЛЕННАЯ) ---
@dp.message(F.text == "Админ-панель")
async def admin_panel_cmd(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔️ Доступ только для создателя.")
    
    if not users_db:
        return await message.answer("📭 База анкет пуста.")

    text = "🛡 УПРАВЛЕНИЕ АНКЕТАМИ\n\n"
    kb_list = []
    for uid, data in users_db.items():
        text += f"🆔 XXXINLINECODEXXX2XXXINLINECODEXXX — {data['name']}\n"
        # Индекс 2 в callback_data теперь совпадает с логикой split
        kb_list.append([InlineKeyboardButton(text=f"❌ Удалить {data['name']}", callback_data=f"adm_del_{uid}")])
    
    await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_list), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("adm_del_"))
async def admin_delete(callback: types.CallbackQuery):
    try:
        # split("_") даст ['adm', 'del', 'ID'] -> ID под индексом 2
        target_id = int(callback.data.split("_")[2]) 
        if target_id in users_db:
            name = users_db[target_id]['name']
            del users_db[target_id]
            await callback.answer(f"✅ Анкета {name} удалена", show_alert=True)
            await callback.message.edit_text("🔄 База обновлена. Открой админку заново.")
        else:
            await callback.answer("Ошибка: Пользователь уже удален.")
    except Exception as e:
        await callback.answer("Произошла системная ошибка.")
        print(f"Error: {e}")

@dp.message(F.text == "ℹ️ Помощь")
async def help_info(message: types.Message):
    await message.answer("🤖 КГП LOVE BOT\n\nЕсли бот завис — напиши /start.\nПо всем вопросам: @sudo_pacman_s")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
