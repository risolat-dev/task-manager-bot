import os
import django
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from asgiref.sync import sync_to_async
from aiohttp import web

import logging

logging.basicConfig(level=logging.INFO)

# 1. Django muhitini sozlash
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
from tasks.models import Task

# 2. Bot sozlamalari (TOKEN-ni o'zgartiring)
API_TOKEN = os.getenv('BOT_TOKEN')
if not API_TOKEN:
    raise ValueError("Xatolik: .env faylida BOT_TOKEN topilmadi!")
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


# 3. FSM (Yangi vazifa qo'shish jarayoni uchun)
class TaskForm(StatesGroup):
    title = State()
    description = State()


# 4. Tugmalar (Keyboard)
def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.button(text="📋 Vazifalar")
    builder.button(text="📊 Statistika")
    builder.button(text="➕ Yangi vazifa")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


# --- Handlerlar ---

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        f"Assalomu alaykum, {message.from_user.full_name}!\n"
        "Men sizning Django bazangiz bilan ishlovchi Task Manager botman.",
        reply_markup=main_menu()
    )


# 📊 Statistika
@dp.message(F.text == "📊 Statistika")
async def show_stats(message: types.Message):
    total = await sync_to_async(Task.objects.count)()
    completed = await sync_to_async(Task.objects.filter(completed=True).count)()
    uncompleted = total - completed

    text = (
        f"📊 **Statistika:**\n\n"
        f"🔹 Jami: {total}\n"
        f"✅ Bajarildi: {completed}\n"
        f"⏳ Kutilmoqda: {uncompleted}"
    )
    await message.answer(text, parse_mode="Markdown")


# 📋 Vazifalar ro'yxati
@dp.message(F.text == "📋 Vazifalar")
async def list_tasks(message: types.Message):
    tasks = await sync_to_async(list)(Task.objects.filter(user_id=message.from_user.id))

    if not tasks:
        await message.answer("Hozircha vazifalar yo'q.")
        return

    for task in tasks:
        status = "✅" if task.completed else "⏳"
        builder = InlineKeyboardBuilder()
        if not task.completed:
            builder.button(text="Bajarildi deb belgilash ✅", callback_data=f"done_{task.id}")

        await message.answer(
            f"📌 **{task.title}**\n📝 {task.description or 'Izoh yo\'q'}\nHolati: {status}",
            reply_markup=builder.as_markup(),
            parse_mode="Markdown"
        )


# ➕ Yangi vazifa qo'shish (FSM boshlanishi)
@dp.message(F.text == "➕ Yangi vazifa")
async def add_task_start(message: types.Message, state: FSMContext):
    await message.answer("Vazifa nomini (Title) kiriting:")
    await state.set_state(TaskForm.title)


@dp.message(TaskForm.title)
async def process_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Vazifa haqida batafsil ma'lumot (Description) yozing:")
    await state.set_state(TaskForm.description)


@dp.message(TaskForm.description)
async def process_desc(message: types.Message, state: FSMContext):
    data = await state.get_data()
    # Bazaga saqlash
    await sync_to_async(Task.objects.create)(
        user_id=message.from_user.id,  # Foydalanuvchi ID sini saqlaymiz
        title=data['title'],
        description=message.text
    )
    await state.clear()
    await message.answer("🎉 Vazifa muvaffaqiyatli saqlandi!", reply_markup=main_menu())


# ✅ Callback: Vazifani bajarildi deb belgilash
@dp.callback_query(F.data.startswith("done_"))
async def mark_as_done(callback: types.CallbackQuery):
    try:
        task_id = int(callback.data.split("_")[1])
        task = await sync_to_async(Task.objects.get)(id=task_id)
        task.completed = True
        await sync_to_async(task.save)()

        await callback.answer("Vazifa bajarildi!")
        await callback.message.edit_text(f"📌 **{task.title}**\nHolati: ✅ Bajarildi", parse_mode="Markdown")
    except Task.DoesNotExist:
        await callback.answer("Kechirasiz, bu vazifa topilmadi yoki allaqachon o'chirilgan.", show_alert=True)


# Botni yurgizish

async def handle(request):
    return web.Response(text="Bot is live!")


async def main():
    # Veb-serverni fonda ishga tushirish
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()

    # Render bergan portda serverni yoqamiz
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    # Endi botning o'zini ishga tushiramiz
    print("Bot polling boshlandi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())