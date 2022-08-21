"""Library to communicate with the windfinder API"""

import json
import logging
import os
import re

import httpx as request

from src.windfindr import utils

_LOGGER = logging.getLogger(__name__)

__version__ = "2.0.1"

TIDES_API_URL = "https://api.windfinder.com/v2/spots/{}/tides/"

class Windfindr:  # pylint: disable=too-few-public-methods
    """Windfindr API"""

    def __init__(self, version="1.0", customer="wfweb", api_key=None):
        self._attr_version = version
        self._attr_customer = customer
        self._attr_api_key = api_key
        self._attr_token = None
        self._attr_client = None


    async def retrieve_token(self, cache = True):
        """Retrieve token"""

        if not self._attr_client:
            self._attr_client = request.AsyncClient()

        if not self._attr_token and cache:
            try:
                with open("token.txt", encoding="utf-8") as fr_token:
                    self._attr_token = fr_token.read()
            except FileNotFoundError as exc:
                _LOGGER.debug(exc)

        if not self._attr_token:
            _LOGGER.info("Retrieving new token")
            try:
                self._attr_token = re.search(
                    r"window\.API_TOKEN\s*=\s*(['\"])(\w+)\1",
                    (await self._attr_client.get("https://www.windfinder.com")).text,
                ).group(2)
                with open("token.txt", "w", encoding="utf-8") as fw_token:
                    fw_token.write(self._attr_token)
            except Exception as exc:
                _LOGGER.error("Unable to get API_TOKEN: {exception}", exception=exc)
                raise

        return self._attr_token


    async def tides(self, spot_id: str, limit = 36, cache = True):
        """Retrieve tides"""

        filename = f"result_tides_{spot_id}_{limit}.json"
        today = utils.get_today()

        if cache:
            try:
                with open(filename, encoding="utf-8") as fr_tides:
                    content = json.loads(fr_tides.read())
                    if today == utils.to_datetime(content["datetime"]):
                        return utils.get_result(content["result"])
            except (FileNotFoundError, json.decoder.JSONDecodeError) as exc:
                _LOGGER.debug(exc)

        await self.retrieve_token()

        req = await self._attr_client.get(
            TIDES_API_URL.format(spot_id),
            params={
                "customer": self._attr_customer,
                "version": self._attr_version,
                "token": self._attr_token,
                "limit": limit,
            },
        )

        with open(filename, "w", encoding="utf-8") as fw_tides:
            if req.status_code == 200:
                res_j = req.json()
                fw_tides.write(
                    json.dumps({"datetime": today.isoformat(), "result": res_j})
                )
                output = utils.get_result(res_j)

                if not output["available"]:
                    _LOGGER.info("No tide found for the spot: {spot}", spot = spot_id)

                return output
            if req.status_code == 401:
                self._attr_token = None
                os.remove("token.txt")
                return self.tides(spot_id, limit)

        _LOGGER.error("Error while requesting tides: {code}", code = req.status_code)

        return utils.get_result([])
