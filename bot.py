import logging
import crypto
from config import *
from aiogram import Bot, Dispatcher, executor, types
from keyboards import *
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from fsm import *
import games.tictactoe as xo
import user_manager as um
import refs



logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)





@dp.message_handler(commands=['start'], state="*")
async def main_menu(message: types.Message, state: FSMContext):
    await state.reset_state()
    users = await um.read_users()
    if await um.does_exist(message.from_user.id):
        await message.answer("Добро пожаловать в Player3 Club Place! \nЕсли у вас возникли вопросы, пожалуйста, обратитесь сюда - @artdmin.\n\nНаши ресурсы:\nВебсайт https://example.xyz \nТелеграм канал https://t.me/player3_club", reply_markup=main_menu_keyb)
    else:
        start_command = message.text
        referer_id = str(start_command[7:])
        if str(referer_id) != '':
            if str(referer_id) != str(message.from_user.id):
                new_user =  {
                    "id": message.from_user.id,
                    "wallet_addr": '0x0',
                    'points_current': 1000,
                    'points_earned': 0,
                    'active_inv':  False,
                    'referer_id': int(referer_id)
                }
                users.append(new_user)
                try:
                    await bot.send_message(int(referer_id), 'По вашей реферальной ссылке зарегистрировался новый пользователь. Спасибо за вашу помощь в развитии проекта!')
                except:
                    pass
            else:
                new_user =  {
                    "id": message.from_user.id,
                    "wallet_addr": '0x0',
                    'points_current': 1000,
                    'points_earned': 0,
                    'active_inv':  False,
                    'referer_id': ''
                }
                users.append(new_user)
                await message.answer("Нельзя регистрироваться по своей же реф. ссылке!")
        else:
            new_user =  {
                "id": message.from_user.id,
                "wallet_addr": '0x0',
                'points_current': 1000,
                'points_earned': 0,
                'active_inv':  False,
                'referer_id': ''
            }
            users.append(new_user)
        await um.write_users_data(users)
        await message.answer("Добро пожаловать в Player3 Club Place! \nЕсли у вас возникли вопросы, пожалуйста, обратитесь сюда - @artdmin.\n\nНаши ресурсы:\nВебсайт https://example.xyz \nТелеграм канал https://t.me/player3_club", reply_markup=main_menu_keyb)

@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    await message.answer("Если у вас возникли вопросы, пожалуйста, обратитесь сюда - @artdmin.\n\nНаши ресурсы:\nВебсайт https://example.xyz \nТелеграм канал https://t.me/player3_club ")

@dp.callback_query_handler(lambda callback: callback.data == "link_wallet")
async def link_wallet(callback: types.CallbackQuery,  state: FSMContext):
    await callback.answer()
    await callback.message.answer("Пожалуйста, скиньте адрес своего Polygon кошелька. Я привяжу его к вашему аккаунту!")
    await state.set_state(LinkWallet.wallet_addr)

@dp.message_handler(state=LinkWallet.wallet_addr)
async def get_waller_addr(message: types.Message, state: FSMContext):
    wallet_addr = message.text
    await um.update_wallet(message.from_user.id,  wallet_addr)
    await message.answer('Кошелек успешно привязан')
    await state.reset_state()


@dp.message_handler(commands=['profile'])
async def profile(message: types.Message):
    users = await um.read_users()
    if await um.does_exist(message.from_user.id):
        await message.answer(f"{message.from_user.full_name}\n@{message.from_user.username}\nТокенов выиграно: {await um.get_points_earned(message.from_user.id)}\nТокенов на данный момент: {await um.get_points_current(message.from_user.id)}\nАдрес кошелька: `{await um.get_wallet(message.from_user.id)}`\nКол-во приглашенных пользователей: {await refs.get_traffic(message.from_user.id)}\n\nВаша реферальная ссылка: `https://t.me/{BOT_NICK}?start={message.from_user.id}`", parse_mode=ParseMode.MARKDOWN, reply_markup=main_menu_keyb)
    else:
        new_user =  {
            "id": message.from_user.id,
            "wallet_addr": '0x0',
            'points_current': 1000,
            'points_earned': 0,
            'active_inv':  False,
            'referer_id': ''
        }
        users.append(new_user)
        await um.write_users_data(users)


@dp.callback_query_handler(lambda callback: callback.data == 'play_xo')
async def start_playing_xo(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    if not await um.any_active_invites_by_user(callback.from_user.id):
        games = await xo.read_games()
        if games != []:
            game_id = games[-1]['id'] + 1
        else:
            game_id = 0
        new_game = {
            "id": game_id,
            "status": "pending",
            "player1": callback.from_user.id,
            "player2": "",
            "winner": "",
            "reward": 10,
            'board': [],
            "whos_move": callback.from_user.id,
        }
        games.append(new_game)
        await xo.write_games_data(games)
        await state.update_data(game_id = game_id)
        await callback.message.answer('Кого вы хотите пригласить поиграть? Введите id пользователя получив его здесь - https://t.me/getmy_idbot.\n\nЧтобы получить id в этом боте, нужно отправить ссылку на телеграм пользователя которого вы хотите пригласить!')
        await state.set_state(PlayingXO.invite_person)

    else:
        await callback.message.answer('У вас уже есть активные приглашения')
    


@dp.message_handler(state = PlayingXO.invite_person)
async def invite_player(message: types.Message, state: FSMContext):
    game_id = 0
    async with state.proxy() as data:
        game_id = data['game_id']
    invitedUser = await bot.get_chat(message.text.replace("@", ''))
    if not await um.any_active_invites_by_user(invitedUser):
        if await um.does_exist(int(message.text)):
            if await um.get_points_current(message.from_user.id) < 5:
                await message.answer("У вас недостаточно средств для игры. Пополните баланс на сайте!")
                await xo.delete_last_game(message.from_user.id)
                await state.reset_state()
            elif await um.get_points_current(int(message.text)) < 5:
                await message.answer("У приглашенного пользователя недостаточно средств для игры!")
                await bot.send_message(int(message.text), "Вам стоит пополнить счет на сайте! У вас недостаточно средств для игры! Весь процесс сброшен. Вызовите /start для выхода в меню!")
                await xo.delete_last_game(message.from_user.id)
                await state.reset_state()
            elif await um.get_points_current(int(message.text)) > 5 and await um.get_points_current(message.from_user.id) > 5:
                try:
                    await bot.send_message(invitedUser.id, f'Вы были приглашены поиграть в крестики нолики с пользователем @{message.from_user.username}', reply_markup=create_invitational_kb(game_id, message.from_user.id))
                    await message.answer('Приглашение было успешно отправлено, вы будете уведомлены как только пользователь ответит!')
                    await state.reset_state()
                    await um.set_active_inv(message.from_user.id, True)
                except Exception as e:
                    await message.answer(f"Предупредите {message.text.replace('@', '')} о том, что надо разблокировать бота или начать с ним переписку. Иначе я не могу получить доступ к общению с этим пользователем! Повторите процесс заново!")
                    await xo.del_game_by_id(game_id)
        else:
            await message.answer(f"Предупредите {message.text.replace('@', '')} о том, что надо начать с ним переписку. Иначе я не могу получить доступ к общению с этим пользователем! Повторите процесс заново!")
            await xo.delete_last_game(message.from_user.id)
            await state.reset_state()


@dp.callback_query_handler(lambda callback: 'decline-xo_' in callback.data)
async def decline_inv(callback: types.CallbackQuery):
    await callback.answer()
    if not await um.does_exist(callback.from_user.id):
        users = await um.read_users()
        new_user =  {
            "id": callback.from_user.id,
            "wallet_addr": '0x0',
            'points_current': 1000,
            'points_earned': 0,
            'active_inv':  False
        }
        users.append(new_user)
        await um.write_users_data(users)
    inviter = int(callback.data.split('_')[2])
    if await um.any_active_invites_by_user(inviter):
        game_id = callback.data.split('_')[1]
        await xo.del_game_by_id(game_id) 
        await um.set_active_inv(inviter, False)
        await callback.message.answer('Приглашение отклонено')
        await bot.send_message(inviter, "Приглашение было отклонено")
    else: 
        await bot.send_message(callback.from_user.id, f"По всей видимости приглашение было отозвано")

@dp.callback_query_handler(lambda callback: 'accept-xo_' in callback.data)
async def accept_inv(callback: types.CallbackQuery):
    await callback.answer()
    if not await um.does_exist(callback.from_user.id):
        users = await um.read_users()
        new_user =  {
            "id": callback.from_user.id,
            "wallet_addr": '0x0',
            'points_current': 1000,
            'points_earned': 0,
            'active_inv':  False
        }
        users.append(new_user)
        await um.write_users_data(users)

    inviter = int(callback.data.split('_')[2])
    if await um.any_active_invites_by_user(inviter):
        inviter_user = await bot.get_chat(inviter)
        game_id = int(callback.data.split('_')[1])
        await um.set_active_inv(inviter, False)
        await xo.update_move(game_id, inviter)
        await xo.update_player2(game_id, callback.from_user.id)
        await xo.update_status(game_id, 'ongoing')
        board = [
            [' ', ' ', ' '],
            [' ', ' ', ' '],
            [' ', ' ', ' ']
        ]
        await xo.update_board(game_id, board)
        await send_board(game_id)
        await xo.deposit_to_reward_pool(inviter, int(callback.from_user.id))
        await bot.send_message(callback.from_user.id, f"Игра началась! Ходит игрок @{inviter_user.username}. Вы игрок O")
        await bot.send_message(inviter, f"Игра началась! Ваш ход! Вы игрок X", reply_markup=tictactoe_kb_inl(game_id, board))
    else:
        await bot.send_message(callback.from_user.id, f"По всей видимости приглашение было отозвано")

@dp.message_handler(commands=['cancel_inv'])
async def cancel_inv(message: types.Message):
    try:
        if await um.any_active_invites_by_user(message.from_user.id):
            await um.set_active_inv(message.from_user.id, False)
            await message.answer('Приглашения отозваны')
        else:
            await message.answer('У вас не было активных приглашений')
    except Exception as e:
        await message.answer('Что-то пошло не так')


@dp.message_handler(commands=['quick_stop'])
async def quick_stop(message: types.Message):
    last_game = await xo.get_last_game(message.from_user.id)
    await bot.send_message(last_game['player1'], 'Игра остановлена!')
    await bot.send_message(last_game['player2'], 'Игра остановлена!')
    await xo.draw(last_game['player1'], last_game['player2'])
    await xo.delete_last_game(int(message.from_user.id))




async def quick_restart(player1, player2):
    chat_player1 = await bot.get_chat(player1)
    username = chat_player1.username
    board = [
        [' ', ' ', ' '],
        [' ', ' ', ' '],
        [' ', ' ', ' ']
    ]
    games = await xo.read_games()
    game_id = games[-1]['id'] + 1
    if await um.get_points_current(player1) < 5:
        player1_chat = await bot.get_chat(player1)
        player1_username = player1_chat.username
        await bot.send_message(player1, "Игра завершена так как у вас недостаточно средств. Пополните баланс на сайте!")
        await bot.send_message(player2, f"Игра завершена так как у @{player1_username} недостаточно средств")
    elif await um.get_points_current(player2) < 5:
        player2_chat = await bot.get_chat(player1)
        player2_username = player2_chat.username
        await bot.send_message(player2, "Игра завершена так как у вас недостаточно средств. Пополните баланс на сайте!")
        await bot.send_message(player1, f"Игра завершена так как у @{player2_username} недостаточно средств")
    
    elif await um.get_points_current(player1) > 5 and await um.get_points_current(player2) > 5:
        await xo.deposit_to_reward_pool(player1, player2)
        new_game = {
            "id": game_id,
            "status": "ongoing",
            "player1": player1,
            "player2": player2,
            "winner": "",
            "reward": 10,
            'board': board,
            "whos_move": player1,
        }
        games.append(new_game)
        await xo.write_games_data(games)
        await send_board(game_id)
        await bot.send_message(player2, f"Игра началась! Ходит игрок @{username}. Вы игрок O")
        await bot.send_message(player1, f"Игра началась! Ваш ход! Вы игрок X", reply_markup=tictactoe_kb_inl(game_id, board))

async def send_board(game_id):
    board = await xo.get_game_board_by_id(game_id)
    board_str = '\n'.join([' | '.join(row) for row in board])
    game = await xo.get_game_by_id(game_id)
    await bot.send_message(game['player1'], f"```\n{board_str}\n```", parse_mode=ParseMode.MARKDOWN)
    await bot.send_message(game['player2'], f"```\n{board_str}\n```", parse_mode=ParseMode.MARKDOWN)



@dp.callback_query_handler(lambda callback: 'move' in callback.data)
async def make_move(callback: types.CallbackQuery):
    await callback.answer()
    try:
        game_id = int(callback.data.split('_')[2])
        game = await xo.get_game_by_id(game_id)

        if callback.from_user.id == game['whos_move']:
            if callback.from_user.id == game['player1']:
                current_player = 'X'
            else:
                current_player = 'O'
            cell = callback.data.split('_')[1]
            board = game['board']
            current_player_chat = await bot.get_chat(int(game['whos_move']))
            current_player_username = current_player_chat.username

            move = int(cell) - 1
            row = move // 3
            col = move % 3

            if board[row][col] == ' ':
                board[row][col] = current_player
                await xo.update_board(game_id, board)
                await send_board(game_id)

                if await xo.check_winner(game_id):
                    if current_player == "X":
                        await bot.send_message(game['player1'], f"Вы победили!")
                        await bot.send_message(game['player2'], f"Игрок @{current_player_username} победил!")
                        await xo.update_winner(game_id, game['player1'])
                        await xo.take_reward(game['player1'], 10)
                    else:
                        await bot.send_message(game['player1'], f"Игрок @{current_player_username} победил!")
                        await bot.send_message(game['player2'], f" Вы победили!")
                        await xo.update_winner(game_id, game['player2'])
                        await xo.take_reward(game['player2'], 10)

                    await xo.update_status(game_id, 'ended')
                    await quick_restart(game['player1'], game['player2'])

                elif await xo.is_board_full(game_id):
                    await bot.send_message(game['player1'], f"Ничья")
                    await bot.send_message(game['player2'], f"Ничья")
                    await xo.draw(game['player1'], game['player2'])
                    await xo.update_status(game_id, 'ended')
                    await xo.update_winner(game_id, 'both')
                    await quick_restart(game['player1'], game['player2'])

                else:
                    current_player = 'O' if current_player == 'X' else 'X'
                    if current_player == 'X':
                        await bot.send_message(game['player1'], f"Ваш ход!", reply_markup=tictactoe_kb_inl(game_id, board))
                        await bot.send_message(game['player2'], f"Ходит игрок {current_player}.")
                    else:
                        await bot.send_message(game['player1'], f"Ходит игрок {current_player}.")
                        await bot.send_message(game['player2'], f"Ваш ход!", reply_markup=tictactoe_kb_inl(game_id, board))
                if game['whos_move'] == game['player1']:
                    await xo.update_move(game_id, game['player2'])
                elif game['whos_move'] == game['player2']:
                    await xo.update_move(game_id, game['player1']) 
            else:
                await callback.message.answer("Эта ячейка уже занята. Выберите другую.", reply_markup=tictactoe_kb_inl(game_id, board))
        else:
            await callback.message.answer('Сейчас не ваш ход!')
    except Exception as e:
        await callback.message.answer('Что-то пошло не так!')



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
