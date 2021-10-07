from pyteal import Approve, compileTeal, Or, Reject, Assert, And
from pyteal import Cond, Mode, OnComplete, Int, Seq, Bytes
from pyteal import Txn, App, Btoi


def approval_program():
    threshold_key = Bytes("threshold")
    action_cnt_key = Bytes("action_cnt")
    nft_cnt_key = Bytes("nft_cnt")
    tx_fees_key = Bytes("tx_fees")
    nft_id_key = Bytes("nft_id")
    token_id_key = Bytes("token_id")

    on_create = Seq(
        # Validators must not be empty
        Assert(Txn.accounts.length() == 0),
        # Invalid threshold
        Assert(
            And(
                Txn.application_args[0] <= 0,
                Txn.application_args[0] > Txn.accounts.length()
            )
        ),

        # uint256 private action_cnt = 0;
        # uint256 private nft_cnt = 0x0;
        # uint256 private tx_fees = 0x0;
        App.globalPut(action_cnt_key, Int(0)),
        App.globalPut(tx_fees_key, Int(0)),
        App.globalPut(nft_cnt_key, Int(0)),

        # threshold = _threshold;
        # nft_token = _nft_token;
        # token = _token;
        App.globalPut(threshold_key, Btoi(Txn.application_args[0])),
        App.globalPut(nft_id_key, Txn.application_args[1]),
        App.globalPut(token_id_key, Txn.application_args[2]),
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
