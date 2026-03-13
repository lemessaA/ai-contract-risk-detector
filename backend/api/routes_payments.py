"""
M-Pesa Payment API Routes
Handles M-Pesa payment processing and callbacks
"""
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
import logging
from datetime import datetime

router = APIRouter(prefix="/api/payments", tags=["payments"])

# In-memory storage for demo (use database in production)
payment_store: Dict[str, Dict[str, Any]] = {}

class MPesaCallbackRequest(BaseModel):
    MerchantRequestID: str
    CheckoutRequestID: str
    ResultCode: str
    ResultDesc: str
    Amount: str
    MpesaReceiptNumber: Optional[str] = None
    Balance: Optional[str] = None
    TransactionDate: Optional[str] = None
    PhoneNumber: Optional[str] = None

class PaymentStatusResponse(BaseModel):
    success: bool
    transactionId: str
    status: str
    message: str
    timestamp: str
    amount: Optional[float] = None
    phoneNumber: Optional[str] = None

@router.post("/mpesa/initiate")
async def initiate_mpesa_payment(
    phoneNumber: str,
    amount: float,
    accountReference: str,
    transactionDesc: str
):
    """Initiate M-Pesa payment (frontend would call this)"""
    try:
        # In a real implementation, this would integrate with M-Pesa API
        # For now, return a mock response
        transaction_id = f"MPESA_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Store payment info
        payment_store[transaction_id] = {
            "phoneNumber": phoneNumber,
            "amount": amount,
            "accountReference": accountReference,
            "transactionDesc": transactionDesc,
            "timestamp": datetime.now().isoformat(),
            "status": "pending"
        }
        
        return JSONResponse({
            "success": True,
            "transactionId": transaction_id,
            "message": "Payment initiated successfully",
            "checkoutRequestID": transaction_id
        })
        
    except Exception as e:
        logging.error(f"Payment initiation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Payment initiation failed"
        )

@router.post("/mpesa/callback")
async def mpesa_callback(request: Request, callback_data: MPesaCallbackRequest):
    """Handle M-Pesa payment callback"""
    try:
        logging.info(f"M-Pesa callback received: {callback_data.dict()}")
        
        # Find the transaction
        transaction_id = callback_data.CheckoutRequestID
        
        if transaction_id in payment_store:
            transaction = payment_store[transaction_id]
            
            # Update transaction status
            if callback_data.ResultCode == "0":
                # Payment successful
                transaction.update({
                    "status": "completed",
                    "mpesaReceipt": callback_data.MpesaReceiptNumber,
                    "transactionDate": callback_data.TransactionDate,
                    "completedAt": datetime.now().isoformat()
                })
                
                logging.info(f"Payment successful: {transaction_id}")
                
            else:
                # Payment failed
                transaction.update({
                    "status": "failed",
                    "errorCode": callback_data.ResultCode,
                    "errorMessage": callback_data.ResultDesc,
                    "failedAt": datetime.now().isoformat()
                })
                
                logging.error(f"Payment failed: {transaction_id} - {callback_data.ResultDesc}")
        
        # M-Pesa expects a specific response format
        callback_response = {
            "ResultCode": "0",
            "ResultDesc": "Callback received successfully"
        }
        
        return JSONResponse(
            content=callback_response,
            status_code=200
        )
        
    except Exception as e:
        logging.error(f"Callback processing error: {str(e)}")
        return JSONResponse(
            content={"ResultCode": "1", "ResultDesc": "Callback processing failed"},
            status_code=500
        )

@router.get("/mpesa/status/{transaction_id}")
async def get_payment_status(transaction_id: str):
    """Get payment status"""
    try:
        if transaction_id not in payment_store:
            raise HTTPException(
                status_code=404,
                detail="Transaction not found"
            )
        
        transaction = payment_store[transaction_id]
        
        return PaymentStatusResponse(
            success=transaction["status"] == "completed",
            transactionId=transaction_id,
            status=transaction["status"],
            message=f"Payment {transaction['status']}",
            timestamp=transaction["timestamp"],
            amount=transaction.get("amount"),
            phoneNumber=transaction.get("phoneNumber")
        )
        
    except Exception as e:
        logging.error(f"Status check error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to check payment status"
        )

@router.get("/mpesa/transactions")
async def list_transactions():
    """List all transactions (for demo purposes)"""
    try:
        transactions = []
        for trans_id, trans_data in payment_store.items():
            transactions.append({
                "transactionId": trans_id,
                **trans_data
            })
        
        return JSONResponse({
            "success": True,
            "transactions": transactions,
            "count": len(transactions)
        })
        
    except Exception as e:
        logging.error(f"Transaction list error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to list transactions"
        )

@router.post("/mpesa/validate")
async def validate_payment(phoneNumber: str, amount: float):
    """Validate payment details before processing"""
    try:
        # Validate phone number (Kenyan format)
        cleaned_phone = phoneNumber.replace(/[\s+]/g, '').replace(/^0+/, '')
        
        if not cleaned_phone.startswith(('1', '7')) or len(cleaned_phone) != 9:
            return JSONResponse({
                "valid": False,
                "message": "Invalid M-Pesa phone number. Must be 9 digits starting with 01, 07, or 1"
            })
        
        # Validate amount
        if amount < 10:
            return JSONResponse({
                "valid": False,
                "message": "Minimum payment amount is KES 10"
            })
        
        return JSONResponse({
            "valid": True,
            "message": "Payment details are valid"
        })
        
    except Exception as e:
        logging.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Validation failed"
        )
