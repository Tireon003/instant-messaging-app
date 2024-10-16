from aiogram import Router
from aiogram.types import ReplyKeyboardRemove, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter

from bot.states import RegistrationStates
from bot.api import AuthApi


router = Router()


@router.message(Command("start"), StateFilter(RegistrationStates.receiving_notifications))
async def start_command(message: Message):
    await message.answer(
        text="Данный телеграм-аккаунт ранее уже был использован для регистрации!",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(Command("start"), StateFilter(None))
async def start_command(message: Message, state: FSMContext):
    await message.reply("Давайте начнем регистрацию!")
    await message.answer(
        text="Введите код подтверждения регистрации...",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(RegistrationStates.waiting_for_code)


@router.message(RegistrationStates.waiting_for_code)
async def handle_registration_code(message: Message, state: FSMContext):
    code = message.text.strip()
    completed = await AuthApi.complete_user_registration(
        code=code,
        tg_chat_id=message.chat.id,
    )
    if completed:
        await message.answer(
            text="Успешная регистрация! Теперь вы будете получаеть уведомления о пропущенных сообщениях.",
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.set_state(RegistrationStates.receiving_notifications)
    else:
        await message.answer(
            text="Неверный код подтверждения регистрации! Попробуйте снова...",
        )
