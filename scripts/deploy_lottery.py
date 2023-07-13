from scripts.utils import get_contract, get_account, fund_with_link
from brownie import Lottery, config, network
import time

REQUEST_CONFIRMATIONS = 3
CALLBACK_GAS_LIMIT = (
    300000  # WHAT DOES THIS DO?! I could not pass the tests because of this value set too high!!!!
    # ANSWER: That is the maximum gas we are willing to spend.
    # By best guess to why this breaks is that the number overflows uint32 if set too high.
    # This is very strange considering the fact that 1 000 000 000 should fit within uint32.
)
NUM_WORDS = 1


def deploy_lottery():
    account = get_account()
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract(
            "vrf_wrapper"  # EDIT: Change from "vfr_coordinator" to "vrf_wrapper"
        ).address,
        get_contract("link_token").address,
        REQUEST_CONFIRMATIONS,
        CALLBACK_GAS_LIMIT,
        NUM_WORDS,
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
        # QUESTION: ^ What is that line doing?
        # ANSWER: It sets the verify key either to what we have in config, or False otherwise.
    )
    print("Deployed lottery!")
    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    starting_tx = lottery.startLottery({"from": account})
    starting_tx.wait(1)  # wait for 1 block (deployment) before starting
    print("Lottery is started!")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 100000000  # add some eth just in case
    tx = lottery.enter({"from": account, "value": value})
    tx.wait(1)
    print("You entered the lottery!")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    # fund the contract
    # then end the lottery. EDIT: No need to do this,
    # because we already funded the subscription in deploy_mocks()
    ### UNDO THE EDIT

    tx = fund_with_link(lottery.address)
    tx.wait(1)
    ending_tx = lottery.endLottery({"from": account})
    ending_tx.wait(1)
    time.sleep(10)  # wait for the callback
    print(f"{lottery.recentWinner()} is the new winner!")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
