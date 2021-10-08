from pyteal import Approve, compileTeal, Or, Reject, Assert, And, For, ScratchVar, TealType, Return, Subroutine, If
from pyteal import Cond, Mode, OnComplete, Int, Seq, Bytes
from pyteal import Txn, App, Btoi


def approval_program():
    threshold_key = Bytes("threshold")
    action_cnt_key = Bytes("action_cnt")
    nft_cnt_key = Bytes("nft_cnt")
    tx_fees_key = Bytes("tx_fees")
    nft_id_key = Bytes("nft_id")
    token_id_key = Bytes("token_id")

    i = ScratchVar(TealType.uint64)

    @Subroutine(TealType.uint64)
    def validateAction(action_id, action, action_data):
        return Seq(
            # TODO:
            Return(Int(0)),  # ValidationRes.Execute
            # Return(Int(1)),  # ValidationRes.Noop
        )

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

        # for (uint i = 0; i < _nft_whitelist.length; i++) {
        # 	nft_whitelist[address(_nft_whitelist[i])] = 2;
        # }
        For(i.store(Int(0)), i.load() < Txn.assets.length(), i.store(i.load() + Int(1))).Do(
            App.globalPut(Txn.assets[i.load()], Int(2))
        ),

        # threshold = _threshold;
        # nft_token = _nft_token;
        # token = _token;
        App.globalPut(threshold_key, Btoi(Txn.application_args[0])),
        App.globalPut(nft_id_key, Txn.application_args[1]),
        App.globalPut(token_id_key, Txn.application_args[2]),
        Approve()
    )

    on_call_method = Txn.application_args[0]

    # Transfer Foreign NFT
    on_validate_transfer_nft = Seq(
        If(validateAction() == Int(0)).Then(
            Seq(
                App.globalPut(nft_cnt_key, App.globalGet(nft_cnt_key) + Int(1)),
                Approve(),
            )
        ),
        Reject()
    )

    # Freeze NFT, requires approval to transfer
    tx_fee = Btoi(Txn.application_args[1])
    on_freeze_nft = Seq(
        App.globalPut(action_cnt_key, App.globalGet(action_cnt_key) + Int(1)),
        App.globalPut(tx_fees_key, App.globalGet(tx_fees_key) + tx_fee),
        Approve()
    )

    # Withdraw Foreign NFT
    on_withdraw_nft = Seq(
        App.globalPut(action_cnt_key, App.globalGet(action_cnt_key) + Int(1)),
        App.globalPut(tx_fees_key, App.globalGet(tx_fees_key) + tx_fee),
        Approve()
    )

    on_call = Cond(
        [on_call_method == Bytes("validate_transfer_nft"), on_validate_transfer_nft],
        [on_call_method == Bytes("freeze_nft"), on_freeze_nft],
        [on_call_method == Bytes("withdraw_nft"), on_withdraw_nft],
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
