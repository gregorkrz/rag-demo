"""
Flare Network Provider Module

This module provides a FlareProvider class for interacting with the Flare Network.
It handles account management, transaction queuing, and blockchain interactions.
"""

from dataclasses import dataclass
from eth_account import Account
from eth_typing import ChecksumAddress
import structlog
from web3 import Web3
from web3.types import TxParams


@dataclass
class TxQueueElement:
    """
    Represents a transaction in the queue with its associated message.

    Attributes:
        msg (str): Description or context of the transaction
        tx (TxParams): Transaction parameters
    """

    msg: str
    tx: TxParams


logger = structlog.get_logger(__name__)


class FlareProvider:
    """
    Manages interactions with the Flare Network including account
    operations and transactions.

    Attributes:
        address (ChecksumAddress | None): The account's checksum address
        private_key (str | None): The account's private key
        tx_queue (list[TxQueueElement]): Queue of pending transactions
        w3 (Web3): Web3 instance for blockchain interactions
        logger (BoundLogger): Structured logger for the provider
    """

    def __init__(self, web3_provider_url: str) -> None:
        """
        Initialize the Flare Provider.

        Args:
            web3_provider_url (str): URL of the Web3 provider endpoint
        """
        self.address: ChecksumAddress | None = None
        self.private_key: str | None = None
        self.tx_queue: list[TxQueueElement] = []
        self.w3 = Web3(Web3.HTTPProvider(web3_provider_url))
        self.logger = logger.bind(router="flare_provider")

    def reset(self) -> None:
        """
        Reset the provider state by clearing account details and transaction queue.
        """
        self.address = None
        self.private_key = None
        self.tx_queue = []
        self.logger.debug("reset", address=self.address, tx_queue=self.tx_queue)

    def add_tx_to_queue(self, msg: str, tx: TxParams) -> None:
        """
        Add a transaction to the queue with an associated message.

        Args:
            msg (str): Description of the transaction
            tx (TxParams): Transaction parameters
        """
        tx_queue_element = TxQueueElement(msg=msg, tx=tx)
        self.tx_queue.append(tx_queue_element)
        self.logger.debug("add_tx_to_queue", tx_queue=self.tx_queue)

    def send_tx_in_queue(self) -> str:
        """
        Send the most recent transaction in the queue.

        Returns:
            str: Transaction hash of the sent transaction

        Raises:
            ValueError: If no transaction is found in the queue
        """
        if self.tx_queue:
            tx_hash = self.sign_and_send_transaction(self.tx_queue[-1].tx)
            self.logger.debug("sent_tx_hash", tx_hash=tx_hash)
            self.tx_queue.pop()
            return tx_hash
        msg = "Unable to find confirmed tx"
        raise ValueError(msg)

    def generate_account(self) -> ChecksumAddress:
        """
        Generate a new Flare account.

        Returns:
            ChecksumAddress: The checksum address of the generated account
        """
        account = Account.create()
        self.private_key = account.key.hex()
        self.address = self.w3.to_checksum_address(account.address)
        self.logger.debug(
            "generate_account", address=self.address, private_key=self.private_key
        )
        return self.address

    def sign_and_send_transaction(self, tx: TxParams) -> str:
        """
        Sign and send a transaction to the network.

        Args:
            tx (TxParams): Transaction parameters to be sent

        Returns:
            str: Transaction hash of the sent transaction

        Raises:
            ValueError: If account is not initialized
        """
        if not self.private_key or not self.address:
            msg = "Account not initialized"
            raise ValueError(msg)
        signed_tx = self.w3.eth.account.sign_transaction(
            tx, private_key=self.private_key
        )
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        self.w3.eth.wait_for_transaction_receipt(tx_hash)
        self.logger.debug("sign_and_send_transaction", tx=tx)
        return "0x" + tx_hash.hex()

    def check_balance(self) -> float:
        """
        Check the balance of the current account.

        Returns:
            float: Account balance in FLR

        Raises:
            ValueError: If account does not exist
        """
        if not self.address:
            msg = "Account does not exist"
            raise ValueError(msg)
        balance_wei = self.w3.eth.get_balance(self.address)
        self.logger.debug("check_balance", balance_wei=balance_wei)
        return float(self.w3.from_wei(balance_wei, "ether"))

    def create_send_flr_tx(self, to_address: str, amount: float) -> TxParams:
        """
        Create a transaction to send FLR tokens.

        Args:
            to_address (str): Recipient address
            amount (float): Amount of FLR to send

        Returns:
            TxParams: Transaction parameters for sending FLR

        Raises:
            ValueError: If account does not exist
        """
        if not self.address:
            msg = "Account does not exist"
            raise ValueError(msg)
        tx: TxParams = {
            "from": self.address,
            "nonce": self.w3.eth.get_transaction_count(self.address),
            "to": self.w3.to_checksum_address(to_address),
            "value": self.w3.to_wei(amount, unit="ether"),
            "gas": 21000,
            "maxFeePerGas": self.w3.eth.gas_price,
            "maxPriorityFeePerGas": self.w3.eth.max_priority_fee,
            "chainId": self.w3.eth.chain_id,
            "type": 2,
        }
        return tx


provider = FlareProvider("https://coston2-api.flare.network/ext/C/rpc")
provider.address = "0x4eF1190cA09A6692030bf6A6E1447fE8f357D440"
provider.private_key = "465b2ae9d8bfa9ebddf57bd177de4f26309f063dd65ad2c12d268c0ada726fef"


print(provider.check_balance())
# add 'hello world to the transaction'
#provider.add_tx_to_queue("Hello world", provider.create_send_flr_tx("0x4eF1190cA09A6692030bf6A6E1447fE8f357D440", 0.0))
#provider.add_tx_to_queue("Hello world", provider.create_send_flr_tx("0x4eF1190cA09A6692030bf6A6E1447fE8f357D440", 0.0))
#provider.send_tx_in_queue()

