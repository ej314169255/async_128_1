import aiohttp
from aiohttp import ClientError


async def message_error(try_url) -> str:
    data = ''
    result_message = ''

    try:
        async with aiohttp.ClientSession() as session:
            # Assuming raise_for_status=True is set (default behavior in session constructor may vary)
            async with session.get(try_url, raise_for_status=True) as response:
                data = await response.json()
    except aiohttp.ClientConnectorError as e:
        # Handle specific connection errors (e.g., DNS failure, connection refused)
        result_message = f"Connection Error: {e}"
    except aiohttp.ClientResponseError as e:
        # Handle specific HTTP status code errors (e.g., 404 Not Found, 500 Internal Server Error)
        result_message = f"HTTP Error: {e.status} - {e.message}"
        # You might also be able to access the response content: print(await e.response.text())
    except ClientError as e:
        # Catch any other aiohttp client error
        result_message = f"An unexpected aiohttp error occurred: {e}"
    except Exception as e:
        # Catch any other non-aiohttp exception
        result_message = f"An unexpected error occurred: {e}"

    return data