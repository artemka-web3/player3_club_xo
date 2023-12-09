from aiogram import types

main_menu_keyb = types.InlineKeyboardMarkup(row_width=2)
main_menu_keyb.add(types.InlineKeyboardButton(text="Играть в 'крестики нолики'", callback_data='play_xo'))
main_menu_keyb.add(types.InlineKeyboardButton(text="Привязать кошелек для вывода денег", callback_data='link_wallet'))


def create_invitational_kb(game_id, inviter_id):
    invitational_keyboard = types.InlineKeyboardMarkup(row_width=2)
    invitational_keyboard.add(types.InlineKeyboardButton(text="Откажусь", callback_data=f"decline-xo_{game_id}_{inviter_id}"))
    invitational_keyboard.add(types.InlineKeyboardButton(text="Соглашусь", callback_data=f"accept-xo_{game_id}_{inviter_id}"))
    return invitational_keyboard

def tictactoe_kb_inl(game_id, board):     
    tictactoe_kb = types.InlineKeyboardMarkup(row_width=3)
   
    tictactoe_kb.add(types.InlineKeyboardButton(text=board[0][0] if board[0][0].strip() != '' else 'пусто', callback_data=f"move_1_{game_id}"), types.InlineKeyboardButton(text=board[0][1] if board[0][1].strip() != '' else 'пусто', callback_data=f"move_2_{game_id}"), types.InlineKeyboardButton(text=board[0][2] if board[0][2].strip() != '' else 'пусто', callback_data=f"move_3_{game_id}"))
    tictactoe_kb.add(types.InlineKeyboardButton(text=board[1][0] if board[1][0].strip() != '' else 'пусто', callback_data=f"move_4_{game_id}"), types.InlineKeyboardButton(text=board[1][1] if board[1][1].strip() != '' else 'пусто', callback_data=f"move_5_{game_id}"), types.InlineKeyboardButton(text=board[1][2] if board[1][2].strip() != '' else 'пусто', callback_data=f"move_6_{game_id}"))
    tictactoe_kb.add(types.InlineKeyboardButton(text=board[2][0] if board[2][0].strip() != '' else 'пусто', callback_data=f"move_7_{game_id}"), types.InlineKeyboardButton(text=board[2][1] if board[2][1].strip() != '' else 'пусто', callback_data=f"move_8_{game_id}"), types.InlineKeyboardButton(text=board[2][2] if board[2][2].strip() != '' else 'пусто', callback_data=f"move_9_{game_id}"))
    return tictactoe_kb


