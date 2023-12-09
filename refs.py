import aiofiles
import json
import user_manager as um

async def read_refs():
    try:
        async with aiofiles.open('../refs.json', 'r', encoding="utf-8") as file:
            content = await file.read()
            return json.loads(content)
    except FileNotFoundError:
        print(f"File not found: {'../refs.json'}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON in file: {'../refs.json'}")
        return None

async def get_traffic(referer_id):
    users = await um.read_users()
    amount = 0
    for user in users:
        if user['referer_id'] == referer_id:
            amount += 1
    return amount
