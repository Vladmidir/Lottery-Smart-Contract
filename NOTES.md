1. Users can enter the lottery with ETH based on the USD fee (oracle data)
2. An admin will choose when the lottery is over
3. The lottery will select a random winner (not so decentrilized). 
    - could potentially be fixed with DAOs or Chainlink Keepers.

### How do we test this?
1. `development` with mocks (local machine)
2. `testnet` (sepolia)
3. `mainnet-fork` (custom) # A fork is the fork of the main (ETH) net.


### Request - recieve data cycle:
- Request the data (`requestRandomness`) from the Chainlink oracle
- Chainlink returns the data in the *callback*, `fulfillRandomWords` function

### Questions
- What is a Mock Contract? Why do we need mocks for local development?
    ANSWER: We need mocks to fill for the dependencies of the imported contracts!
- Why can't deploy the original contracts locally instead of mocks? 

### Do next
- <s>Fix the bug. Local network mocks don't work! 
    VRFV2WrapperConsumerBase.sol does not have the required dependencies!
    VRFV2CoordinatorV2Mock aint doing it!</s>
- <s>Set up the 'local oracle' for testing
    - Emmit an event </s>
- <s>Write unit tests</s>
- Learn what CALLBACK_GAS_LIMIT means
    - WHY: When I set the CALLBACK_GAS_LIMIT too high, everything fails and I don't get a random number
    - ANSWER: That is the maximum gas we are willing to spend.
    By best guess to why this breaks is that the number overflows uint32 if set too high.
    This is very strange considering the fact that 1 000 000 000 should fit within uint32. Leave it for now. Very strange tho...
- Write integration tests

### Important Notes
I had to modify the ChainSpecificUtil.sol file at `C:\Users\drew_\.brownie\packages\smartcontractkit\chainlink@2.2.0\contracts\src\v0.8` by adding the `getL1CalldataGasCost` function from the [GitHub version of this file](https://github.com/smartcontractkit/chainlink/blob/develop/contracts/src/v0.8/ChainSpecificUtil.sol). For some reason, the `brownie pm` installation of the dependencies did not include that function in the file.
