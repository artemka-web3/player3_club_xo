import aiofiles
import json

async def read_users():
    try:
        async with aiofiles.open('../users.json', 'r',encoding="utf-8") as file:
            content = await file.read()
            return json.loads(content)
    except FileNotFoundError:
        print(f"File not found: {'../users.json'}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON in file: {'../users.json'}")
        return None

async def write_users_data(data):
    try:
        async with aiofiles.open('../users.json', 'w', encoding="utf-8") as file:
            await file.write(json.dumps(data, ensure_ascii=False))
    except Exception as e:
        print(f"Error writing to file {'../users.json'}: {e}")

async def does_exist(id):
    users = await read_users()
    if users != []:
        for user in users:
            if user['id'] == id:
                return True
    return False

async def update_wallet(user_id, wallet):
    users = await read_users()
    if users != []:
        for user in users:
            if user['id'] == user_id:
                user['wallet_addr'] = wallet
                await write_users_data(users)

async def update_points_earned(user_id, amount_to_add):
    users = await read_users()
    if users != []:
        for user in users:
            if user['id'] == user_id:
                user['points_earned'] += amount_to_add
                await write_users_data(users)

async def update_points_current(user_id, amount_to_add):
    users = await read_users()
    if users != []:
        for user in users:
            if user['id'] == user_id:
                user['points_current'] += amount_to_add
                await write_users_data(users)


async def get_points_current(user_id):
    users = await read_users()
    if users != []:
        for user in users:
            if user['id'] == user_id:
                return user['points_current']

async def get_points_earned(user_id):
    users = await read_users()
    if users != []:
        for user in users:
            if user['id'] == user_id:
                return user['points_earned']

async def get_wallet(user_id):
    try:
        users = await read_users()
        if users != []:
            for user in users:
                if user['id'] == user_id:
                    return user['wallet_addr']
    except Exception as e:
        print(e)



async def any_active_invites_by_user(id):
    users = await read_users()
    for user in users:
        if user["id"] == id:
            return bool(user['active_inv'])

async def set_active_inv(id, is_active):
    try:
        users = await read_users()    
        for user in users:
            if user["id"] == id:
                user['active_inv'] = is_active
                await write_users_data(users)
    except Exception  as e:
        print('Что-то пошло не так!')