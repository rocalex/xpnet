from typing import Tuple, List

from algosdk import encoding
from algosdk.future import transaction
from algosdk.v2client.algod import AlgodClient

from .account import Account
from .contracts import approval_program, clear_state_program
from .utils import fullyCompileContract, waitForTransaction, getAppGlobalState

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
        validators: List[Account],
        nft_whitelist: List[str],
        threshold: int,
        nft_id: int,
        token_id: int,
) -> int:
    """Create a XP app.

    Args:
        client: An algod client.
        sender: The account that will create the XP application.
        validators:
        nft_whitelist:
        threshold:
        nft_id:
        token_id:

    Returns:
        The ID of the newly created XP app.
    """
    approval, clear = getContracts(client)

    globalSchema = transaction.StateSchema(num_uints=7, num_byte_slices=2)
    localSchema = transaction.StateSchema(num_uints=0, num_byte_slices=0)

    app_args = [
        threshold,
        nft_id,
        token_id,
    ]

    txn = transaction.ApplicationCreateTxn(
        sender=sender.getAddress(),
        on_complete=transaction.OnComplete.NoOpOC,
        approval_program=approval,
        clear_program=clear,
        global_schema=globalSchema,
        local_schema=localSchema,
        accounts=[validator.getAddress() for validator in validators],
        foreign_assets=nft_whitelist,
        app_args=app_args,
        sp=client.suggested_params(),
    )

    signedTxn = txn.sign(sender.getPrivateKey())

    client.send_transaction(signedTxn)

    response = waitForTransaction(client, signedTxn.get_txid())
    assert response.applicationIndex is not None and response.applicationIndex > 0
    return response.applicationIndex


def closeXpApp(client: AlgodClient, appID: int, closer: Account):
    """Close an XP application.

    Args:
        client: An algod client.
        appID: The ID of the XP app.
        closer: The account initiating the close transaction. This must be
            either the seller or auction creator if you wish to close the
            auction before it starts. Otherwise, this can be any account.
    """
    appGlobalState = getAppGlobalState(client, appID)

    nftID = appGlobalState[b"nft_id"]

    accounts: List[str] = [encoding.encode_address(appGlobalState[b"seller"])]

    deleteTxn = transaction.ApplicationDeleteTxn(
        sender=closer.getAddress(),
        index=appID,
        accounts=accounts,
        foreign_assets=[nftID],
        sp=client.suggested_params()
    )
    signedDeleteTxn = deleteTxn.sign(closer.getPrivateKey())

    client.send_transaction(signedDeleteTxn)

    waitForTransaction(client, signedDeleteTxn.get_txid())


def validate_transfer():
    # TODO:
    pass


def validate_transfer_nft(
        client: AlgodClient,
        appID: int,
        sender: Account,
        receiver: Account,
        action_id: int,
        action_data: str
):
    """
    Transfer Foreign NFT

    Args:
        client:
        appID:
        sender:
        receiver:
        action_id:
        action_data:
    """
    suggestedParams = client.suggested_params()

    appCallTxn = transaction.ApplicationCallTxn(
        sender=sender.getAddress(),
        index=appID,
        on_complete=transaction.OnComplete.NoOpOC,
        app_args=[b"validate_transfer_nft", action_id, action_data],
        accounts=[receiver.getAddress()],
        sp=suggestedParams,
    )
    createNftTxn = transaction.AssetConfigTxn(
        sender=sender.getAddress(),
        total=1,
        decimals=0,
        sp=suggestedParams,
    )

    signedAppCallTxn = appCallTxn.sign(sender.getPrivateKey())
    signedCreateNftTxn = createNftTxn.sign(sender.getPrivateKey())

    client.send_transactions([signedAppCallTxn, signedCreateNftTxn])

    waitForTransaction(client, appCallTxn.get_txid())


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


def withdraw():
    # TODO:
    pass


def withdraw_nft(
        client: AlgodClient,
        appID: int,
        nftHolder: Account,
        nftID: int,
        fee: int
) -> None:
    """Withdraw Foreign NFT

    Args:
        client: An algod client.
        appID: The ID of the XP app.
        nftHolder:
        nftID:
        fee: Transaction fee
    """
    suggestedParams = client.suggested_params()

    appCallTxn = transaction.ApplicationCallTxn(
        sender=nftHolder.getAddress(),
        index=appID,
        on_complete=transaction.OnComplete.NoOpOC,
        app_args=[b"withdraw_nft", fee],
        foreign_assets=[nftID],
        sp=suggestedParams,
    )

    destroyNftTxn = transaction.AssetConfigTxn(
        sender=nftHolder.getAddress(),
        sp=suggestedParams,
        index=nftID,
        strict_empty_address_check=False
    )

    signedAppCallTxn = appCallTxn.sign(nftHolder.getPrivateKey())
    signedDestroyNftTxn = destroyNftTxn.sign(nftHolder.getPrivateKey())

    client.send_transactions([signedAppCallTxn, signedDestroyNftTxn])

    waitForTransaction(client, appCallTxn.get_txid())


def freeze_nft(
        client: AlgodClient,
        appID: int,
        funder: Account,
        nftHolder: Account,
        receiver: Account,
        nftID: int,
        fees: int
) -> None:
    suggestedParams = client.suggested_params()

    appCallTxn = transaction.ApplicationCallTxn(
        sender=funder.getAddress(),
        index=appID,
        on_complete=transaction.OnComplete.NoOpOC,
        app_args=[b"freeze_nft", fees],
        foreign_assets=[nftID],
        sp=suggestedParams,
    )

    transferNftTxn = transaction.AssetTransferTxn(
        sender=nftHolder.getAddress(),
        receiver=receiver.getAddress(),
        index=nftID,
        amt=1,
        sp=suggestedParams,
    )

    signedAppCallTxn = appCallTxn.sign(receiver.getPrivateKey())
    signedTransferNftTxn = transferNftTxn.sign(nftHolder.getPrivateKey())

    client.send_transactions([signedAppCallTxn, signedTransferNftTxn])

    waitForTransaction(client, appCallTxn.get_txid())


def freeze(client: AlgodClient, appID: int, ) -> None:
    # TODO:
    pass
