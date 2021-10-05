from typing import Tuple

from algosdk import encoding
from algosdk.future import transaction
from algosdk.v2client.algod import AlgodClient

from .account import Account
from .contracts import approval_program, clear_state_program
from .utils import fullyCompileContract, waitForTransaction

APPROVAL_PROGRAM = b""
CLEAR_STATE_PROGRAM = b""


def getContracts(client: AlgodClient) -> Tuple[bytes, bytes]:
    """Get the compiled TEAL contracts for the auction.

    Args:
        client: An algod client that has the ability to compile TEAL programs.

    Returns:
        A tuple of 2 byte strings. The first is the approval program, and the
        second is the clear state program.
    """
    global APPROVAL_PROGRAM
    global CLEAR_STATE_PROGRAM

    if len(APPROVAL_PROGRAM) == 0:
        APPROVAL_PROGRAM = fullyCompileContract(client, approval_program())
        CLEAR_STATE_PROGRAM = fullyCompileContract(client, clear_state_program())

    return APPROVAL_PROGRAM, CLEAR_STATE_PROGRAM


def createXpApp(
        client: AlgodClient,
        sender: Account,
        threshold: int,
        action_cnt: int,
        nft_cnt: int,
        tx_fees: int,
        nft_token: int,
        token: int
) -> int:
    approval, clear = getContracts(client)

    globalSchema = transaction.StateSchema(num_uints=7, num_byte_slices=2)
    localSchema = transaction.StateSchema(num_uints=0, num_byte_slices=0)

    app_args = [
        threshold,
        action_cnt,
        nft_cnt,
        tx_fees,
        nft_token,
        token,
    ]

    txn = transaction.ApplicationCreateTxn(
        sender=sender.getAddress(),
        on_complete=transaction.OnComplete.NoOpOC,
        approval_program=approval,
        clear_program=clear,
        global_schema=globalSchema,
        local_schema=localSchema,
        app_args=app_args,
        sp=client.suggested_params(),
    )

    signedTxn = txn.sign(sender.getPrivateKey())

    client.send_transaction(signedTxn)

    response = waitForTransaction(client, signedTxn.get_txid())
    assert response.applicationIndex is not None and response.applicationIndex > 0
    return response.applicationIndex


def validate_action():
    # TODO:
    pass


def validate_transfer():
    # TODO:
    pass


def validate_transfer_nft():
    # TODO:
    pass


def validate_unfreeze():
    # TODO:
    pass


def validate_unfreeze_nft():
    # TODO:
    pass


def validate_whitelist_nft():
    # TODO:
    pass


def validate_add_validator():
    # TODO:
    pass


def validate_remove_validator():
    # TODO:
    pass


def validate_pause_bridge():
    # TODO:
    pass


def validate_unpause_bridge():
    # TODO:
    pass


def validate_set_threshold():
    # TODO:
    pass


def _withdraw_fees():
    # TODO:
    pass


def validate_withdraw_fees():
    # TODO:
    pass


def _withdraw():
    # TODO:
    pass


def withdraw():
    # TODO:
    pass


def _withdraw_nft():
    # TODO:
    pass


def withdraw_nft():
    # TODO:
    pass


def freeze_erc721():
    # TODO:
    pass


def freeze():
    # TODO:
    pass
