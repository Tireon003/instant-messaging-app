from aiogram import Router, F
from aiogram.types import ReplyKeyboardRemove, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from bot.states import RegistrationStates
from bot.api import AuthApi


router = Router()


@router.message(Command("start"))
async def start_command(message: Message, state: FSMContext) -> None:
    is_chat_id_binded = await AuthApi.check_if_chat_id_binded(message.chat.id)
    if is_chat_id_binded:
        await message.answer(
            text="Ваш telegram-аккаунт уже привязан.",
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.set_state(RegistrationStates.receiving_notifications)
    else:
        await message.reply("Давайте начнем регистрацию!")
        await message.answer(
            text="Введите код подтверждения регистрации...",
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.set_state(RegistrationStates.waiting_for_code)


@router.message(RegistrationStates.waiting_for_code)
async def handle_registration_code(
    message: Message, state: FSMContext
) -> None:
    code = message.text
    if code:
        completed = await AuthApi.complete_user_registration(
            code=code,
            tg_chat_id=message.chat.id,
        )
    else:
        completed = False
    if completed:
        await message.answer(
            text="Успешная регистрация! Теперь вы будете получаеть "
            "уведомления о пропущенных сообщениях.",
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.set_state(RegistrationStates.receiving_notifications)
    else:
        await message.answer(
            text="Неверный код подтверждения регистрации! Попробуйте снова...",
        )


@router.message(F.text)
async def handle_unknown_command(message: Message) -> None:
    await message.answer(
        text="Данной команды не существует.",
        reply_markup=ReplyKeyboardRemove(),
    )
