import asyncio
import random
import time

import aiohttp

names = ['Michael', 'Kevin', 'Dwight', 'Jim', 'Ryan', 'Pam', 'Stanley', 'Angela', 'Oscar', 'Kelly']
servers = ['http://localhost:8000', 'http://localhost:8001']

response_pings = []
response_count = 0


async def send_request():
    text = 'text'
    global response_count

    for _ in range(100):
        name = random.choice(names)
        base_url = random.choice(servers)
        now = time.time()

        session = aiohttp.ClientSession()
        await session.post(base_url + '/send', json={'name': name, 'text': text})
        await session.close()

        response_count += 1
        response_pings.append(time.time() - now)


async def main():
    tasks = [send_request() for _ in range(50)]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())

    execution_time = time.time() - start_time
    average_ping = sum(response_pings) / len(response_pings)
    capacity = response_count / execution_time
    print(
        f'Resposes executed: {response_count}\nAverage ping: {average_ping}\n'
        f'Full time: {execution_time}\nCapacity: {capacity} RPS',
    )
