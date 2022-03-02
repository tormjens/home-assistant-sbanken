""" Sbanken API."""
from __future__ import annotations
import logging
import string
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import urllib.parse
from .const import InvalidAuth

_LOGGER = logging.getLogger(__name__)


class SbankenApi:
    def create_session(self, client_id: string, secret: string) -> OAuth2Session:
        try:

            oauth2_client = BackendApplicationClient(
                client_id=urllib.parse.quote(client_id)
            )
            session = OAuth2Session(client=oauth2_client)
            session.fetch_token(
                token_url="https://auth.sbanken.no/identityserver/connect/token",
                client_id=urllib.parse.quote(client_id),
                client_secret=urllib.parse.quote(secret),
            )
            return session
        except Exception:
            raise InvalidAuth

    def get_customer_information(self, session: OAuth2Session):
        response = (
            session.get("https://publicapi.sbanken.no/apibeta/api/v2/Customers/")
        ).json()

        if "isError" not in response:
            return response["item"]
        raise RuntimeError(
            "{} {}".format(response["errorType"], response["errorMessage"])
        )

    def get_accounts(self, session: OAuth2Session):
        response = session.get(
            "https://publicapi.sbanken.no/apibeta/api/v2/Accounts/"
        ).json()
        if "isError" not in response:
            return response["items"]

        raise RuntimeError(
            "{} {}".format(response["errorType"], response["errorMessage"])
        )

    def get_account(self, session: OAuth2Session, accountId):
        response = session.get(
            "https://publicapi.sbanken.no/apibeta/api/v2/Accounts/{}".format(accountId)
        ).json()

        if "isError" not in response:
            return response
        else:
            raise RuntimeError(
                "{} {}".format(response["errorType"], response["errorMessage"])
            )

    def get_transactions(
        self, session: OAuth2Session, accountId, number_of_transactions: int
    ):
        response = session.get(
            "https://publicapi.sbanken.no/apibeta/api/v2/Transactions/"
            + accountId
            + "?length="
            + str(number_of_transactions)
        ).json()

        if "isError" not in response:
            return response["items"]
        else:
            raise RuntimeError(
                "{} {}".format(response["errorType"], response["errorMessage"])
            )

    def get_payments(self, session: OAuth2Session, accountId, number_of_payments: int):
        response = session.get(
            "https://publicapi.sbanken.no/apibeta/api/v2/Payments/"
            + accountId
            + "?length="
            + str(number_of_payments)
        ).json()

        if "isError" not in response:
            return response["items"]
        else:
            raise RuntimeError(
                "{} {}".format(response["errorType"], response["errorMessage"])
            )

    def get_standingOrders(self, session: OAuth2Session, accountId):
        response = session.get(
            "https://publicapi.sbanken.no/apibeta/api/v2/StandingOrders/" + accountId
        ).json()

        if "isError" not in response:
            return response["items"]
        else:
            raise RuntimeError(
                "{} {}".format(response["errorType"], response["errorMessage"])
            )

    def transfer(
        self,
        session: OAuth2Session,
        from_account_id: str,
        to_account_id: str,
        amount: float,
        message: str,
    ) -> bool:
        data = {
            "fromAccountId": from_account_id,
            "toAccountId": to_account_id,
            "message": message,
            "amount": amount,
        }
        response = session.post(
            "https://publicapi.sbanken.no/apibeta/api/v2/Transfers/", json=data
        )
        return response.status_code == 204
