from base64 import b64decode

from algosdk.v2client.algod import AlgodClient
from pyteal import compileTeal, Expr, Mode


def fullyCompileContract(client: AlgodClient, contract: Expr) -> bytes:
    teal = compileTeal(contract, mode=Mode.Application, version=5)
    response = client.compile(teal)
    return b64decode(response["result"])
