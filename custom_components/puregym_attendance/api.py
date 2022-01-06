"""Sample API Client."""
import asyncio
import logging
import socket
import requests
import aiohttp
import async_timeout

TIMEOUT = 10

_LOGGER: logging.Logger = logging.getLogger(__package__)

HEADERS = {"Content-type": "application/json; charset=UTF-8"}


class PuregymAttendanceApiClient:
    """Add two numbers"""
    def __init__(
        self, username: str, password: str, session: aiohttp.ClientSession
    ) -> None:
        """Sample API Client."""
        self._username = username
        self._passeword = password
        self._session = session

    async def async_get_data(self) -> dict:
        """Add two numbers"""
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': 'PureGym/1523 CFNetwork/1312 Darwin/21.0.0'}
        authed = False
        home_gym_id = None
        session = requests.session()
        data = {
            'grant_type': 'password',
            'username': self._username,
            'password': self._passeword,
            'scope': 'pgcapi',
            'client_id': 'ro.client'
        }

        response = session.post('https://auth.puregym.com/connect/token',
                headers=headers, data=data)
        if response.status_code == 200:
            auth_json = response.json()
            authed = True
            headers['Authorization'] = 'Bearer '+auth_json['access_token']
        else:
            _LOGGER.error(response.raise_for_status())

        if not authed:
            _LOGGER.error("Permission Error")

        response = session.get('https://capi.puregym.com/api/v1/member', headers=headers)
        if response.status_code == 200:
            home_gym_id = response.json()['homeGymId']
        else:
            _LOGGER.error('Response %s', str(response.status_code))
        response = session.get(f'https://capi.puregym.com/api/v1/gyms/{str(home_gym_id)}/attendance',
                headers=headers)
        return response.json()['totalPeopleInGym']

    async def async_set_title(self, value: str) -> None:
        """Get data from the API."""
        url = "https://jsonplaceholder.typicode.com/posts/1"
        await self.api_wrapper("patch", url, data={"title": value}, headers=HEADERS)

    async def api_wrapper(
        self, method: str, url: str, data: dict = None, headers: dict = None
    ) -> dict:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(TIMEOUT, loop=asyncio.get_event_loop()):
                if method == "get":
                    response = await self._session.get(url, headers=headers)
                    return await response.json()

                elif method == "put":
                    await self._session.put(url, headers=headers, json=data)

                elif method == "patch":
                    await self._session.patch(url, headers=headers, json=data)

                elif method == "post":
                    await self._session.post(url, headers=headers, json=data)

        except asyncio.TimeoutError as exception:
            _LOGGER.error(
                "Timeout error fetching information from %s - %s",
                url,
                exception,
            )

        except (KeyError, TypeError) as exception:
            _LOGGER.error(
                "Error parsing information from %s - %s",
                url,
                exception,
            )
        except (aiohttp.ClientError, socket.gaierror) as exception:
            _LOGGER.error(
                "Error fetching information from %s - %s",
                url,
                exception,
            )
        except Exception as exception:  # pylint: disable=broad-except
            _LOGGER.error("Something really wrong happend! - %s", exception)
