import os

import httpx


RATELOC_ROOMS_URL = (
    "https://apixcug.rateloc.com/accommodation/rooms"
)


async def fetch_rooms_from_rateloc(
    payload: dict,
) -> dict:
    token = os.getenv("RATELOC_API_TOKEN")

    if not token:
        raise ValueError(
            "RATELOC_API_TOKEN environment variable is missing."
        )

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }

    async with httpx.AsyncClient(
        timeout=60.0
    ) as client:
        response = await client.post(
            RATELOC_ROOMS_URL,
            headers=headers,
            json=payload,
        )

        response.raise_for_status()

        return response.json()