"""
ClawPay Integration for ChaosClaw
=================================
Private payments via Railgun - no on-chain link between sender and recipient.

API: https://clawpay.dev
Network: BSC (Binance Smart Chain)
"""

import os
import requests
from dataclasses import dataclass
from typing import Optional
from eth_account import Account
from eth_account.messages import encode_defunct

CLAWPAY_API = os.environ.get("CLAWPAY_API_URL", "https://clawpay.dev")
SIGN_MESSAGE = "b402 Incognito EOA Derivation"


@dataclass
class TransferResult:
    success: bool
    transfer_id: Optional[str] = None
    error: Optional[str] = None


class ClawPayClient:
    """
    Private payments for AI agents via ClawPay/Railgun.
    
    Flow:
    1. Sign message to prove wallet ownership
    2. Get invoice address  
    3. Transfer tokens to invoice (on BSC)
    4. Execute private transfer
    
    Recipient sees funds from Railgun - no link to sender.
    
    Note: ClawPay is currently on BSC. Railgun is also on Ethereum.
    """
    
    def __init__(self, private_key: Optional[str] = None):
        self.private_key = private_key or os.environ.get("CHAOSCLAW_PRIVATE_KEY")
        self.api_url = CLAWPAY_API
        
        if self.private_key:
            self.account = Account.from_key(self.private_key)
            self.address = self.account.address
            self._signature = self._sign_message()
        else:
            self.account = None
            self.address = None
            self._signature = None
    
    def _sign_message(self) -> str:
        """Sign the ClawPay authorization message."""
        message = encode_defunct(text=SIGN_MESSAGE)
        signed = self.account.sign_message(message)
        return signed.signature.hex()
    
    def health_check(self) -> bool:
        """Check if ClawPay API is healthy."""
        try:
            resp = requests.get(f"{self.api_url}/health", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("status") == "ok"
            return False
        except:
            return False
    
    def get_invoice_address(self) -> Optional[str]:
        """
        Get the invoice address for receiving payments.
        Tokens sent here will be shielded via Railgun.
        """
        if not self._signature:
            return None
        
        try:
            resp = requests.get(
                f"{self.api_url}/invoice",
                params={"eoa": self.address, "signature": self._signature},
                timeout=30
            )
            data = resp.json()
            if data.get("success"):
                return data.get("invoiceAddress")
        except:
            pass
        return None
    
    def get_balance(self, token: str = "USDT") -> float:
        """Get shielded balance available for private transfers."""
        if not self._signature:
            return 0.0
        
        try:
            resp = requests.get(
                f"{self.api_url}/balance",
                params={
                    "eoa": self.address,
                    "signature": self._signature,
                    "token": token
                },
                timeout=30
            )
            data = resp.json()
            if data.get("success"):
                return float(data.get("balance", 0))
        except:
            pass
        return 0.0
    
    def transfer(
        self,
        recipient: str,
        amount: str,
        token: str = "USDT"
    ) -> TransferResult:
        """
        Execute a private transfer.
        
        Recipient will receive funds from Railgun contract,
        with NO on-chain link to ChaosClaw's address.
        
        Args:
            recipient: Destination address
            amount: Amount to send (e.g., "1.00")
            token: Token symbol (USDT or USDC)
        
        Returns:
            TransferResult with transfer_id or error
        """
        if not self._signature:
            return TransferResult(
                success=False,
                error="No wallet configured"
            )
        
        try:
            resp = requests.post(
                f"{self.api_url}/transfer",
                json={
                    "eoa": self.address,
                    "signature": self._signature,
                    "recipient": recipient,
                    "amount": amount,
                    "token": token
                },
                timeout=60
            )
            data = resp.json()
            
            if data.get("success"):
                return TransferResult(
                    success=True,
                    transfer_id=data.get("transferId")
                )
            else:
                return TransferResult(
                    success=False,
                    error=data.get("error", "Unknown error")
                )
        except Exception as e:
            return TransferResult(
                success=False,
                error=str(e)
            )
    
    def get_transfer_status(self, transfer_id: str) -> dict:
        """Check status of a pending transfer."""
        try:
            resp = requests.get(
                f"{self.api_url}/status/{transfer_id}",
                timeout=30
            )
            return resp.json()
        except:
            return {"success": False, "error": "Failed to check status"}
    
    def tip(self, recipient: str, amount: str = "0.10") -> TransferResult:
        """
        Send a small tip to another agent.
        Convenience method with sensible defaults.
        """
        return self.transfer(recipient, amount, "USDT")
    
    def get_wallet_info(self) -> dict:
        """Get wallet info for display."""
        return {
            "address": self.address,
            "configured": self.address is not None,
            "network": "BSC (Binance Smart Chain)",
            "api": self.api_url
        }


# Singleton for easy access
_client: Optional[ClawPayClient] = None


def get_clawpay_client() -> ClawPayClient:
    """Get or create the ClawPay client singleton."""
    global _client
    if _client is None:
        _client = ClawPayClient()
    return _client
