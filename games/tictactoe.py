import aiofiles
import json
import user_manager as um

async def read_games():
    try:
        async with aiofiles.open('xos.json', 'r', encoding="utf-8") as file:
            content = await file.read()
            return json.loads(content)
    except FileNotFoundError:
        print(f"File not found: {'xos.json'}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON in file: {'xos.json'}")
        return None

async def write_games_data(data):
    try:
        async with aiofiles.open('xos.json', 'w', encoding="utf-8") as file:
            await file.write(json.dumps(data, ensure_ascii=False))
    except Exception as e:
        print(f"Error writing to file {'xos.json'}: {e}")

async def get_game_by_id(id):
    games = await read_games()
    for game in games:
        if game["id"] == id:
            return game
        
    return None

async def get_game_board_by_id(id):
    games = await read_games()
    for game in games:
        if game["id"] == id:
            return game['board']
        
    return None

async def del_game_by_id(id):
    games = await read_games()
    for game in games:
        if game["id"] == id:
            del game['id']
            await write_games_data(games)

async def update_winner(id, winner):
    games = await read_games()
    for game in games:
        if game["id"] == id:
            game['winner'] = winner
            await write_games_data(games)

async def update_player2(id, player2):
    games = await read_games()
    for game in games:
        if game["id"] == id:
            game['player2'] = player2
            await write_games_data(games)
    
async def update_status(id, status):
    games = await read_games()
    for game in games:
        if game["id"] == id:
            game['status'] = status
            await write_games_data(games)
    
async def update_move(id, mover):
    games = await read_games()
    for game in games:
        if game["id"] == id:
            game['whos_move'] = mover
            await write_games_data(games)

async def update_board(id, board):
    games = await read_games()
    for game in games:
        if game["id"] == id:
            game['board'] = board
            await write_games_data(games)


async def any_game_started(user_id):
    games = await read_games()
    if games is not None:
        user_games = [game["status"] for game in games if game["player1"] == user_id or game["player2"] == user_id]
        if 'ongoing' in user_games:
            return True
    else:
        return []




async def check_winner(game_id):
    game = await get_game_by_id(game_id)
    for i in range(3):
        # Проверка по горизонтали
        if game['board'][i][0] == game['board'][i][1] == game['board'][i][2] != ' ':
            return True
        # Проверка по вертикали
        if game['board'][0][i] == game['board'][1][i] == game['board'][2][i] != ' ':
            return True

    # Проверка по диагоналям
    if game['board'][0][0] == game['board'][1][1] == game['board'][2][2] != ' ' or game['board'][0][2] == game['board'][1][1] == game['board'][2][0] != ' ':
        return True

    return False

# Проверка на ничью
async def is_board_full(game_id):
    game = await get_game_by_id(game_id)
    for row in game["board"]:
        if ' ' in row:
            return False
    return True

async def delete_last_game(player):
    games = await read_games()
    filtered_games = [game for game in games if game["player1"] == player or game["player2"] == player]
    max_game = max(filtered_games, key=lambda x: x["id"], default=None)
    if max_game['status'] != 'ended':
        games.remove(max_game)

    await write_games_data(games)

async def get_last_game(player):
    games = await read_games()
    filtered_games = [game for game in games if game["player1"] == player or game["player2"] == player]
    max_game = max(filtered_games, key=lambda x: x["id"], default=None)
    if max_game['status'] != 'ended':
        return games[max_game['id']]
    return None


async def deposit_to_reward_pool(player1,  player2):
    await um.update_points_current(player1,  -5)
    await um.update_points_current(player2,  -5)

async def take_reward(winner, reward):
    await um.update_points_current(winner, reward)
    await um.update_points_earned(winner, reward)

async def draw(player1, player2):
    await um.update_points_current(player1, 5)
    await um.update_points_current(player2, 5)