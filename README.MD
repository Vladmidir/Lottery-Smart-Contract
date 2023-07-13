# Solidity Lottery Smart Contract
This is a Lottery Smart Contract implementation using the Chainlink VRF V2 to retrieve a random number.



## Table of contents
- [Overview](#overview)
    - [Inspiration](#inspiration)
    - [Functionality](#functionality)
- [My process](#my-process)
    - [Challenges](#challanges)
        - [Deploying mocks](#deploying-mocks)
    - [What I Learned](#what-i-learned)
    - [Future development](#future-development)


## Overview

### Inspiration
This is an updated version of the Lottery Smart Contract from the [Solidity course by Patrick Collins](https://youtu.be/zwxeYCIu0dE).

My full course repo can be found [here](https://github.com/Vladmidir/Solidity-Brownie-Course).

### Functionality
The Smart Contract allows the user to Enter the Lottery by paying the specified fee. The owner of the contract can then End the Lottery. When the Lottery ends, the contract requests a random number using VRF V2 by Chainlink.

The project folder also includes Unit and Integration tests.

## My process
### Challenges
I have decided to deviate from the tutorial and implement the newer version of the VRF. For this I had to read some chainlink documentation to gain in depth understanding of how the VRF V2 works. After that, I was able to successfuly set up the mock contracts required to test the Lottery contract locally.

#### Deploying mocks
Here is the function from [utils.py](./scripts/utils.py) that deploys all the required mocks.
```py
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
```

One thing I have failed to implement is the automatic contract source code publishing with Brownie. I have followed the exact steps from the lesson, but could not get it to work.

### What I learned
With this project, I have learned a lot of core topics in Smart Contract development.
To list some of them:
- How to set up different kinds of tests (local, testnet, mainnet-fork)
- How to write unit and integration tests
- How to get a truly random number delivered to the blockchain
- How to configure networks in the `brownie-config.yaml`
- How to manage contract state using `enum`

### Future development
This project has provided me with a solid foundation in Brownie and Solidity Smart Contract development in general. I now feel ready to build my own dApp. The only thing I am yet to learn is how to connect front-end to the blockchain. 


I also want to explore other APIs and libraries made by platforms like Chainlink and OpenZeppelin. These are very helpful in creating larger and more secure contracts. 

Finally, I want to add that this contract is fairly straightforward. I will likely have to research Smart Contract Design Patterns in order to successfuly build larger dApps.