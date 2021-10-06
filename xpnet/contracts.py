from pyteal import Approve, compileTeal, Or, Reject
from pyteal import Cond, Mode, OnComplete, Int, Seq, Bytes
from pyteal import Txn, App, Btoi


def approval_program():
    threshold_key = Bytes("threshold")
    action_cnt_key = Bytes("action_cnt")
    nft_cnt_key = Bytes("nft_cnt")
    tx_fees_key = Bytes("tx_fees")
    nft_token_key = Bytes("nft_token")
    token_key = Bytes("token")

    on_create = Seq(
        App.globalPut(threshold_key, Btoi(Txn.application_args[0])),
        App.globalPut(action_cnt_key, Btoi(Txn.application_args[1])),
        App.globalPut(nft_cnt_key, Btoi(Txn.application_args[2])),
        App.globalPut(tx_fees_key, Btoi(Txn.application_args[3])),
        App.globalPut(nft_token_key, Txn.application_args[4]),
        App.globalPut(token_key, Txn.application_args[5]),
        Approve()
    )

    on_call_method = Txn.application_args[0]
    tx_fees = Btoi(Txn.application_args[1])

    # Freeze NFT, requires approval to transfer
    on_freeze_nft = Seq(
        App.globalPut(action_cnt_key, App.globalGet(action_cnt_key) + Int(1)),
        App.globalPut(tx_fees_key, App.globalGet(tx_fees_key) + tx_fees),
        Approve()
    )

    # Withdraw Foreign NFT
    on_withdraw_nft = Seq(
        App.globalPut(action_cnt_key, App.globalGet(action_cnt_key) + Int(1)),
        App.globalPut(tx_fees_key, App.globalGet(tx_fees_key) + tx_fees),
        Approve()
    )

    on_call = Cond(
        [on_call_method == Bytes("freeze_nft"), on_freeze_nft],
        [on_call_method == Bytes("withdraw_nft"), on_withdraw_nft]
    )

    on_delete = Seq(
        # TODO: 
        Reject()
    )

    program = Cond(
        [Txn.application_id() == Int(0), on_create],
        [Txn.on_completion() == OnComplete.NoOp, on_call],
        [
            Txn.on_completion() == OnComplete.DeleteApplication,
            on_delete,
        ],
        [
            Or(
                Txn.on_completion() == OnComplete.OptIn,
                Txn.on_completion() == OnComplete.CloseOut,
                Txn.on_completion() == OnComplete.UpdateApplication,
            ),
            Reject(),
        ],
    )
    return program


def clear_state_program():
    return Approve()


if __name__ == "__main__":
    with open("xpnet_approval.teal", "w") as f:
        compiled = compileTeal(
            approval_program(), mode=Mode.Application, version=5)
        f.write(compiled)

    with open("xpnet_clear_state.teal", "w") as f:
        compiled = compileTeal(clear_state_program(),
                               mode=Mode.Application, version=5)
        f.write(compiled)
