from xpnet.operations import createXpApp
from xpnet.testing.resources import getTemporaryAccount, createDummyAsset
from xpnet.testing.setup import getAlgodClient


def main():
    client = getAlgodClient()

    print("Alice is generating temporary accounts...")
    creator = getTemporaryAccount(client)
    seller = getTemporaryAccount(client)

    print("Alice is generating an example NFT...")
    nftAmount = 1
    nftID = createDummyAsset(client, nftAmount, seller)
    print("The NFT ID is:", nftID)

    print(
        "Alice is creating xpnet smart contract."
    )
    appID = createXpApp(
        client=client,
        sender=creator,
        action_cnt=0,
        nft_token=nftID,
        nft_cnt=nftAmount,
        threshold=0,
        token=0,
        tx_fees=0
    )

    print("Alice is setting up and funding NFT auction...")


if __name__ == '__main__':
    main()
