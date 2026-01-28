import asyncio
import datetime
import pprint
from error_unit import message_error

from local_unit import batched
from time import sleep
import aiohttp

from db import DbSession, SwapiPeople, close_orm, init_orm

MAX_REQUESTS = 15
BASE_URL = "https://swapi.py4e.com/api/people/"



async def get_field(url_in, http_session):
    
    if await message_error(url_in):
        response = await http_session.get(url_in)
        json_data = await response.json()
        json_data.update({'id': int(json_data.get('url').split('/')[-2])})        
        return json_data
    else:
        return dict()

async def get_ex(url, http_session):
    response = http_session.get(url)
    h_field = response.json()    
    return h_field.update({'homeworld': h_field.get('name')})


async def insert_people(people_list):
    async with DbSession() as db_session:
        count = 0
        for item in people_list:
            if item.get('birth_year'):
                field_dict = {
                'birth_year': item.get('birth_year'),
                'eye_color': item.get('eye_color'),
                'gender': item.get('gender'),
                'hair_color': item.get('hair_color'),
                'homeworld': item.get('homeworld'),
                'id': item.get('id'),
                'mass': item.get('mass'),
                'name': item.get('name'),
                'skin_color': item.get('skin_color')
                }
                #pprint.pprint(field_dict)
                swapi_people_orm =  SwapiPeople(**field_dict)
                db_session.add(swapi_people_orm)
            else:
                count += 1
        await db_session.commit()
        #db_session.add_all([SwapiPeople(json=item) for item in people_list])
        print(count)



async def main():
    await init_orm()
    async with aiohttp.ClientSession() as http_session:
        for i_batch in batched(range(1, 101), MAX_REQUESTS):
            coros = []
            for i in i_batch:
                coros.append(get_field(BASE_URL + str(i) + '/', http_session))
            #coros = [get_people(i, http_session) for i in i_batch]
            results = await asyncio.gather(*coros)
            insert_people_coro = insert_people(results)
            insert_people_task = asyncio.create_task(insert_people_coro)

    tasks = asyncio.all_tasks()
    
    current_task = asyncio.current_task()
    tasks.remove(current_task)
    await asyncio.gather(*tasks)
    # for task in  tasks:
    #     await task
    #
    await close_orm()


start = datetime.datetime.now()
asyncio.run(main())
end = datetime.datetime.now()
print(end - start)
