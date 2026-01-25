import asyncio
import datetime
from itertools import islice

# from itertools import batched
import aiohttp

from db import DbSession, SwapiPeople, close_orm, init_orm

MAX_REQUESTS = 5


async def get_people(person_id, http_session):
    response = await http_session.get(f"https://swapi.py4e.com/api/people/{person_id}/")
    json_data = await response.json()
    return json_data


async def insert_people(people_list):
    async with DbSession() as db_session:
        # for item in people_list:
        #     swapi_people_orm =  SwapiPeople(json=item)
        #     db_session.add(swapi_people_orm)
        # await db_session.commit()
        db_session.add_all([SwapiPeople(json=item) for item in people_list])
        await db_session.commit()

def batched(iterable, n, *, strict=False):
    # batched('ABCDEFG', 3) → ABC DEF G
    if n < 1:
        raise ValueError('n must be at least one')
    iterator = iter(iterable)
    while batch := tuple(islice(iterator, n)):
        if strict and len(batch) != n:
            raise ValueError('batched(): incomplete batch')
        yield batch


async def main():
    await init_orm()
    async with aiohttp.ClientSession() as http_session:
        for i_batch in batched(range(1, 10), MAX_REQUESTS):
            # coros = []
            # for i in i_batch:
            #     coros.append(get_people(i))
            coros = [get_people(i, http_session) for i in i_batch]
            results = await asyncio.gather(*coros)
            insert_people_coro = insert_people(results)
            insert_people_task = asyncio.create_task(insert_people_coro)

    # tasks = asyncio.all_tasks()
    # current_task = asyncio.current_task()
    # tasks.remove(current_task)
    # await asyncio.gather(*tasks)
    # for task in  tasks:
    #     await task
    #
    await close_orm()


start = datetime.datetime.now()
asyncio.run(main())
end = datetime.datetime.now()
print(end - start)
