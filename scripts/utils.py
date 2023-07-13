from brownie import (
    accounts,
    config,
    network,
    MockV3Aggregator,
    VRFCoordinatorV2Mock,
    LinkToken,
    VRFV2Wrapper,
    Contract,
)

FORKED_LOCAL_ENVIRONMNETS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]


def get_account(index=None, id=None):
    # for dev purposes
    if index:
        return accounts[index]

    if id:
        return accounts.load(id)

    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMNETS
    ):
        return accounts[0]

    # for test networks
    return accounts.add(config["wallets"]["from_key"])


# maps string to brownie.network.contract.ProjectContract object
contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,  # QUESTION:Does mock mean - simulate the contract on the local network?
    "vrf_coordinator": VRFCoordinatorV2Mock,
    "link_token": LinkToken,
    "vrf_wrapper": VRFV2Wrapper,
}


def get_contract(contract_name):
    """
    Grab the contract addresses from the brownie-config
    if defined, otherwise, deploy a mock version of that contract,
    and return that mock contract.

        Args:
            contract_name(str)

        Returns:
            brownie.network.contract.ProjectContract: The most recently deployed
            version of this contract.
    """
    # Contract type returns the Contract object!
    contract_type = contract_to_mock[contract_name]

    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if (  # QUESTION: What is this condition doing? ANSWER: Checks if we have any contract deployed.
            len(contract_type) <= 0  # equal to MockV3Aggregator.length
        ):
            deploy_mocks()
        contract = contract_type[-1]
        # ^ equal to: MockV3Aggregator[-1]
    else:
        # grab the contract from config
        # QUESTION: Does network.show_active() return the name of the network. ANSWER: Yes.
        contract_address = config["networks"][network.show_active()][contract_name]
        # address - just got
        # ABI - from MockV3Aggregator
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )  # MockV3Aggregator._name # MockV3Aggregator.abi

    return contract


def deploy_mocks():
    """Set up all the mock contracts required for local testing"""
    print("Deploying mocks...")
    account = get_account()
    # 1. Deploy the VRFCoordinatorV2Mock. This contract is a mock of the VRFCoordinatorV2 contract.
    # 2. Deploy the MockV3Aggregator contract.
    # 3. Deploy the LinkToken contract.
    # 4. Deploy the VRFV2Wrapper contract.
    # 5. Call the VRFV2Wrapper setConfig function to set wrapper specific parameters.
    # 6. Fund the VRFv2Wrapper subscription.
    # Fund it from 'account' using the `fund_with_link()`
    # 7. Call the the VRFCoordinatorV2Mock addConsumer function to add the wrapper contract to your subscription.
    # 8. Deploy your VRF consumer contract.
    coordinator = VRFCoordinatorV2Mock.deploy(
        100000000000000000,
        1000000000,
        {"from": account},  # constructor(uint96 _baseFee, uint96 _gasPriceLink)
    )
    aggregator = (
        MockV3Aggregator.deploy(  # constructor(uint8 _decimals, int256 _initialAnswer)
            8, 200000000000, {"from": account}
        )
    )
    link = LinkToken.deploy({"from": account})
    wrapper = VRFV2Wrapper.deploy(  # constructor(address _link, address _linkEthFeed, address _coordinator)
        link.address, aggregator.address, coordinator.address, {"from": account}
    )

    # configure the wrapper
    wrapper.setConfig(  # setConfig(uint32 _wrapperGasOverhead, uint32 _coordinatorGasOverhead, uint8 _wrapperPremiumPercentage, bytes32 _keyHash, uint8 _maxNumWords)
        60000,
        52000,
        10,
        0xD89B2BF150E3B9E13446986E571FB9CAB24B13CEA0A43EA20A6049A85CC807CC,
        10,
        {"from": account},
    )

    coordinator.fundSubscription(
        1, 10000000000000000000, {"from": account}
    )  # fundSubscription(uint64 _subId, uint96 _amount)
    print("Deployed mocks!")


def fund_with_link(
    contract_address, account=None, link_token=None, amount=10000000000000000000
):  # 10 Link
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_address, amount, {"from": account})
    # ^ Could also use Interfaces! Link to demo - (https://youtu.be/zwxeYCIu0dE?t=5500)
    tx.wait(1)
    print("Funded contract!")
    return tx
