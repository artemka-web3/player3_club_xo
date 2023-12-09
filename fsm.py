from aiogram.dispatcher.filters.state import State, StatesGroup

class LinkWallet(StatesGroup):
    wallet_addr = State()


class PlayingXO(StatesGroup):
    invite_person = State()