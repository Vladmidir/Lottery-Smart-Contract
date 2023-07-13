// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

// would have to import the oracle contract address
// Need to add the dependency to the brownie-config.yaml file.
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
//is it ok if I import v0.8 contract alogside v0.6?
import "@chainlink/contracts/src/v0.8/vrf/VRFV2WrapperConsumerBase.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract Lottery is Ownable, VRFV2WrapperConsumerBase {
    address payable[] public players;
    address payable public recentWinner;
    uint256 public recentRandom;
    uint256 public usdEntryFee;

    AggregatorV3Interface internal ethUsdPriceFeed;

    //enum - user defined type that can be represented with INTs
    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    LOTTERY_STATE public lottery_state;

    //arguments for requestRandomness()
    uint16 requestConfimations;
    uint32 callbackGasLimit;
    uint32 numWords;
    //event to emit when requesting random number
    event requestedRandomness(uint256 requestId);

    constructor(
        address _priceFeedAddress,
        address _vrfWrapper,
        address _linkToken,
        uint16 _requestConfimations,
        uint32 _callbackGasLimit,
        uint32 _numWords
    ) VRFV2WrapperConsumerBase(_linkToken, _vrfWrapper) {
        //call the VRFV2WrapperConsumerBase (parent) constructor
        usdEntryFee = 50;
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        lottery_state = LOTTERY_STATE.CLOSED; //since repsented by nums, could do lottery_state = 1;
        requestConfimations = _requestConfimations; //minimum = 3
        callbackGasLimit = _callbackGasLimit; //just random. Figure out how to decide on this one!
        numWords = _numWords;
    }

    /**
     * Enter the lottery
     */
    function enter() public payable {
        require(lottery_state == LOTTERY_STATE.OPEN);
        //50$ minimum
        require(msg.value >= getEntranceFee(), "Not enough ETH");
        players.push(payable(msg.sender)); // cast to payable
        //QUESTION: What is this casting address to payable all about?
        //ANSWER: Looks like we convert a regular address to a payable one.
        //QUESTION: Does that mean we can send money to that address? Or they can send us money?
        //QUESTION: Can I only cast addresses to payable? I doubt I can cans strings and ints.
        //ANSWER: Looks like I can only cast Address to AddressPayable
    }

    /**
     * Entrance cost in Wei
     */
    function getEntranceFee() public view returns (uint256) {
        //$ price for 1ETH, with 8 decimals
        (, int256 price, , , ) = ethUsdPriceFeed.latestRoundData();
        uint256 adjustedPrice = uint256(price);
        //(50 000 000 000 000 000 000 / 185 551 851 240) * 10^8
        uint256 costEnter = (uint256(usdEntryFee * 10 ** 18) / adjustedPrice) *
            10 ** 8; // add 8 zeroes to compensate for the 8 zeroes of the adjustedPrice.
        return costEnter;
    }

    /**
     * Simple state change
     */
    function startLottery() public onlyOwner {
        require(
            lottery_state == LOTTERY_STATE.CLOSED,
            "Can't start a new lottery yet!"
        );
        lottery_state = LOTTERY_STATE.OPEN;
    }

    /**
     *Request randomness
     */
    function endLottery() public onlyOwner {
        //uint256(
        //    keccak256(
        //        abi.encodePacked(
        //            nonce, //predictable
        //            msg.sender, //predictable
        //            block.difficulty, //can be manipulated by the miners
        //            block.timestamp //predictable
        //        )
        //    )
        //) % players.length;
        // ^ bad way of getting a random numeber.

        //#THE PROPER WAY:
        //We will get our random number from the Chainlink oracle.
        //For this we will have to pay some Chainlink gas (LINK token).
        //We did not have to do this for the price oracle, because the 'sponsors' paid the gas fee for us!
        lottery_state = LOTTERY_STATE.CALCULATING_WINNER;
        //Inherited function!
        uint256 requestId = requestRandomness(
            callbackGasLimit,
            requestConfimations,
            numWords
        );
        //NOTE: Emiting an event saves it in the transaction (like a print statement inside a transaction)
        emit requestedRandomness(requestId);
    }

    //Overwriting the callback function of the VRF contract
    //QUESTION: What happens if I don't add `override`? ANSWER: Error happens
    function fulfillRandomWords(
        uint256 _requestId, //EMITED the requestId
        uint256[] memory _randomWords
    ) internal override {
        require(
            lottery_state == LOTTERY_STATE.CALCULATING_WINNER,
            "You aren't there yet!"
        );
        require(_randomWords.length > 0, "random not found");
        //Calculate the winner and transfer funds
        uint256 indexOfWinner = _randomWords[0] % players.length;
        recentWinner = players[indexOfWinner];
        recentWinner.transfer(address(this).balance);
        //Reset
        players = new address payable[](0);
        lottery_state = LOTTERY_STATE.CLOSED;
        recentRandom = _randomWords[0];
    }
}
