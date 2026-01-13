me} удалена", show_alert=True)
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
