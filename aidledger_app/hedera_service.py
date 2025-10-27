"""
Hedera Hashgraph Integration Service for AidLedger
Handles HCS (Consensus Service) and HTS (Token Service) operations
Updated for hedera-sdk-py 2.50.0
"""

import json
import logging
from typing import Dict, Any, Optional
from django.conf import settings
from django.utils import timezone
from hedera import (
    Client, AccountId, PrivateKey, TopicCreateTransaction, 
    TopicMessageSubmitTransaction, TokenCreateTransaction, 
    TokenType, TokenSupplyType, TokenMintTransaction,
    TransferTransaction, TokenId, AccountBalanceQuery,
    TopicInfoQuery, Hbar, TopicId  # Add TopicId here
)

logger = logging.getLogger(__name__)


class HederaService:
    """Service class for Hedera Hashgraph operations"""
    
    def __init__(self):
        self.config = settings.HEDERA_CONFIG
        self.client = self._initialize_client()
        self.topic_id = None
        self.token_id = None
        
    def _initialize_client(self) -> Client:
        """Initialize Hedera client with testnet configuration"""
        try:
            client = Client.forTestnet()
            operator_id = AccountId.fromString(self.config['OPERATOR_ID'])
            operator_key = PrivateKey.fromString(self.config['OPERATOR_KEY'])
            client.setOperator(operator_id, operator_key)
            return client
        except Exception as e:
            logger.error(f"Failed to initialize Hedera client: {e}")
            raise
    
    def create_transparency_topic(self) -> str:
        """Create HCS topic for donation transparency"""
        try:
            topic_tx = (TopicCreateTransaction()
                       .setTopicMemo("AidLedger Donations Transparency")
                       .execute(self.client))
            
            topic_id = topic_tx.getReceipt(self.client).topicId
            self.topic_id = topic_id
            topic_id_str = topic_id.toString()
            logger.info(f"Created HCS topic: {topic_id_str}")
            return topic_id_str
        except Exception as e:
            logger.error(f"Failed to create HCS topic: {e}")
            raise
    
    def create_aidcoin_token(self) -> str:
        """Create AidCoin fungible token"""
        try:
            token_tx = (TokenCreateTransaction()
                       .setTokenName("AidCoin")
                       .setTokenSymbol("AID")
                       .setTokenType(TokenType.FUNGIBLE_COMMON)
                       .setSupplyType(TokenSupplyType.INFINITE)
                       .setInitialSupply(1000000)
                       .setTreasuryAccountId(self.client.getOperatorAccountId())
                       .setAutoRenewAccountId(self.client.getOperatorAccountId())
                       .execute(self.client))
            
            token_id = token_tx.getReceipt(self.client).tokenId
            self.token_id = token_id
            token_id_str = token_id.toString()
            logger.info(f"Created AidCoin token: {token_id_str}")
            return token_id_str
        except Exception as e:
            logger.error(f"Failed to create AidCoin token: {e}")
            raise
    
    def log_donation_to_hcs(self, donor_name: str, ngo_name: str, amount: float) -> str:
        """Log donation transaction to HCS topic"""
        try:
            if not self.topic_id:
                self.topic_id = self.config.get('TOPIC_ID')
                if not self.topic_id:
                    raise ValueError("Topic ID not configured")
            
            # Convert string topic_id back to TopicId object if needed
            if isinstance(self.topic_id, str):
                topic_id_obj = TopicId.fromString(self.topic_id)
            else:
                topic_id_obj = self.topic_id
            
            message_data = {
                "type": "donation",
                "donor": donor_name,
                "ngo": ngo_name,
                "amount": amount,
                "timestamp": str(timezone.now())
            }
            
            message_tx = (TopicMessageSubmitTransaction()
                         .setTopicId(topic_id_obj)
                         .setMessage(json.dumps(message_data))
                         .execute(self.client))
            
            txn_hash = message_tx.getReceipt(self.client).transactionId.toString()
            logger.info(f"Logged donation to HCS: {txn_hash}")
            return txn_hash
        except Exception as e:
            logger.error(f"Failed to log donation to HCS: {e}")
            raise
    
    def log_distribution_to_hcs(self, ngo_name: str, recipient_name: str, amount: float) -> str:
        """Log distribution transaction to HCS topic"""
        try:
            if not self.topic_id:
                self.topic_id = self.config.get('TOPIC_ID')
                if not self.topic_id:
                    raise ValueError("Topic ID not configured")
            
            # Convert string topic_id back to TopicId object if needed
            if isinstance(self.topic_id, str):
                topic_id_obj = TopicId.fromString(self.topic_id)
            else:
                topic_id_obj = self.topic_id
            
            message_data = {
                "type": "distribution",
                "ngo": ngo_name,
                "recipient": recipient_name,
                "amount": amount,
                "timestamp": str(timezone.now())
            }
            
            message_tx = (TopicMessageSubmitTransaction()
                         .setTopicId(topic_id_obj)
                         .setMessage(json.dumps(message_data))
                         .execute(self.client))
            
            txn_hash = message_tx.getReceipt(self.client).transactionId.toString()
            logger.info(f"Logged distribution to HCS: {txn_hash}")
            return txn_hash
        except Exception as e:
            logger.error(f"Failed to log distribution to HCS: {e}")
            raise
    
    def transfer_aidcoin(self, from_wallet: str, to_wallet: str, amount: int) -> str:
        """Transfer AidCoin tokens between wallets"""
        try:
            if not self.token_id:
                self.token_id = self.config.get('TOKEN_ID')
                if not self.token_id:
                    raise ValueError("Token ID not configured")
            
            # Convert string token_id back to TokenId object if needed
            if isinstance(self.token_id, str):
                token_id_obj = TokenId.fromString(self.token_id)
            else:
                token_id_obj = self.token_id
            
            transfer_tx = (TransferTransaction()
                          .addTokenTransfer(
                              token_id_obj,
                              AccountId.fromString(from_wallet),
                              -amount
                          )
                          .addTokenTransfer(
                              token_id_obj,
                              AccountId.fromString(to_wallet),
                              amount
                          )
                          .execute(self.client))
            
            txn_hash = transfer_tx.getReceipt(self.client).transactionId.toString()
            logger.info(f"Transferred {amount} AidCoin: {txn_hash}")
            return txn_hash
        except Exception as e:
            logger.error(f"Failed to transfer AidCoin: {e}")
            raise
    
    def get_account_balance(self, wallet_id: str) -> Dict[str, Any]:
        """Get account balance for a wallet"""
        try:
            balance_query = AccountBalanceQuery().setAccountId(AccountId.fromString(wallet_id))
            balance = balance_query.execute(self.client)
            
            return {
                "wallet_id": wallet_id,
                "hbar_balance": balance.hbars.toString(),
                "token_balances": [
                    {
                        "token_id": token.tokenId.toString(),
                        "balance": token.balance
                    }
                    for token in balance.tokens
                ]
            }
        except Exception as e:
            logger.error(f"Failed to get account balance: {e}")
            raise
    
    def verify_transaction(self, txn_hash: str) -> Dict[str, Any]:
        """Verify transaction using Hedera Mirror Node API"""
        try:
            import requests
            
            # Using Hedera Mirror Node API
            mirror_url = f"https://testnet.mirrornode.hedera.com/api/v1/transactions/{txn_hash}"
            response = requests.get(mirror_url)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": "Transaction not found", "status_code": response.status_code}
        except Exception as e:
            logger.error(f"Failed to verify transaction: {e}")
            return {"error": str(e)}


# Global instance
hedera_service = HederaService()