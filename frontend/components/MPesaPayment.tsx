'use client';

import React, { useState, useEffect } from 'react';
import { PhoneIcon, CreditCardIcon, CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline';
import QRCode from 'qrcode';
import MPesaService, { MPesaPaymentRequest, PaymentConfirmation } from '../services/mpesaService';

interface MPesaPaymentProps {
  onPaymentSuccess?: (confirmation: PaymentConfirmation) => void;
  onPaymentError?: (error: string) => void;
  amount: number;
  description: string;
  disabled?: boolean;
}

const MPesaPayment: React.FC<MPesaPaymentProps> = ({
  onPaymentSuccess,
  onPaymentError,
  amount,
  description,
  disabled = false
}) => {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [showQR, setShowQR] = useState(false);
  const [paymentStep, setPaymentStep] = useState<'idle' | 'processing' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');
  const [qrCode, setQrCode] = useState('');

  const mpesaService = new MPesaService();

  useEffect(() => {
    // Generate QR code for mobile payment
    if (phoneNumber && amount >= 10) {
      const qrData = JSON.stringify({
        type: 'mpesa',
        phone: phoneNumber,
        amount: amount,
        description: description
      });
      try {
        const qrDataUrl = QRCode.toDataURL(qrData, {
          errorCorrectionLevel: 'M',
          type: 'png',
          quality: 0.92,
          margin: 1,
          color: {
            dark: '#000000',
            light: '#FFFFFF'
          }
        });
        setQrCode(qrDataUrl);
      } catch (error) {
        console.error('QR Code generation error:', error);
        setQrCode('');
      }
    }
  }, [phoneNumber, amount, description]);

  const handlePayment = async () => {
    // Validate phone number
    if (!mpesaService.validatePhoneNumber(phoneNumber)) {
      setErrorMessage('Please enter a valid M-Pesa phone number (Kenyan number starting with 01, 07, or 1)');
      return;
    }

    if (amount < 10) {
      setErrorMessage('Minimum payment amount is KES 10');
      return;
    }

    setIsProcessing(true);
    setPaymentStep('processing');
    setErrorMessage('');

    try {
      const paymentRequest: MPesaPaymentRequest = {
        phoneNumber: phoneNumber,
        amount: mpesaService.formatAmount(amount),
        accountReference: `CONTRACT-${Date.now()}`,
        transactionDesc: description,
        callBackURL: `${window.location.origin}/api/payments/mpesa/callback`
      };

      const result = await mpesaService.initiatePayment(paymentRequest);

      if (result.success) {
        setPaymentStep('success');
        // Check payment status after a delay
        setTimeout(async () => {
          if (result.transactionId) {
            const confirmation = await mpesaService.checkPaymentStatus(result.transactionId);
            onPaymentSuccess?.(confirmation);
          }
        }, 5000); // Wait 5 seconds for payment processing
      } else {
        setPaymentStep('error');
        setErrorMessage(result.message || 'Payment failed');
        onPaymentError?.(result.message || 'Payment failed');
      }
    } catch (error) {
      setPaymentStep('error');
      setErrorMessage('Payment service unavailable. Please try again.');
      onPaymentError?.('Payment service unavailable');
    } finally {
      setIsProcessing(false);
    }
  };

  const resetPayment = () => {
    setPhoneNumber('');
    setPaymentStep('idle');
    setErrorMessage('');
    setShowQR(false);
    setQrCode('');
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-lg">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">M-Pesa Payment</h2>
        <p className="text-gray-600 mb-4">
          Pay for contract analysis services using M-Pesa mobile money
        </p>
      </div>

      {/* Payment Amount Display */}
      <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
        <div className="text-center">
          <div className="text-3xl font-bold text-green-600">KES {amount}</div>
          <div className="text-sm text-gray-600">{description}</div>
        </div>
      </div>

      {/* Phone Number Input */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          <PhoneIcon className="h-4 w-4 inline mr-2" />
          M-Pesa Phone Number
        </label>
        <input
          type="tel"
          value={phoneNumber}
          onChange={(e) => setPhoneNumber(e.target.value)}
          placeholder="2547XXXXXXXX"
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
          disabled={isProcessing || disabled}
        />
        <p className="text-xs text-gray-500 mt-1">
          Enter your M-Pesa registered phone number
        </p>
      </div>

      {/* QR Code Display */}
      {qrCode && (
        <div className="mb-6 text-center">
          <button
            onClick={() => setShowQR(!showQR)}
            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            {showQR ? 'Hide QR Code' : 'Show QR Code'}
          </button>
          
          {showQR && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-2">Scan with M-Pesa app:</p>
              <div className="flex justify-center">
                <QRCode value={qrCode} size={200} />
              </div>
            </div>
          )}
        </div>
      )}

      {/* Error Display */}
      {errorMessage && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center">
            <XCircleIcon className="h-5 w-5 text-red-500 mr-2" />
            <span className="text-red-700">{errorMessage}</span>
          </div>
        </div>
      )}

      {/* Payment Status */}
      {paymentStep === 'processing' && (
        <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600 border-t-transparent border-r-transparent mr-3"></div>
            <span className="text-blue-700">Processing payment...</span>
          </div>
          <p className="text-sm text-blue-600 mt-2">
            Please check your phone for M-Pesa prompt
          </p>
        </div>
      )}

      {paymentStep === 'success' && (
        <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center">
            <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2" />
            <span className="text-green-700">Payment initiated successfully!</span>
          </div>
          <p className="text-sm text-green-600 mt-2">
            Check your M-Pesa app to complete the payment
          </p>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex space-x-3">
        <button
          onClick={handlePayment}
          disabled={isProcessing || disabled || !phoneNumber || amount < 10}
          className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-bold py-3 px-4 rounded-lg flex items-center justify-center"
        >
          {isProcessing ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white border-t-transparent border-r-transparent mr-2"></div>
              Processing...
            </>
          ) : (
            <>
              <CreditCardIcon className="h-5 w-5 mr-2" />
              Pay KES {amount}
            </>
          )}
        </button>

        {paymentStep !== 'idle' && (
          <button
            onClick={resetPayment}
            className="px-4 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </button>
        )}
      </div>

      {/* M-Pesa Info */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <h3 className="font-semibold text-gray-900 mb-2">Payment Information</h3>
        <ul className="text-sm text-gray-600 space-y-1">
          <li>• Minimum payment: KES 10</li>
          <li>• Payment via M-Pesa STK Push</li>
          <li>• You'll receive a prompt on your phone</li>
          <li>• Enter your M-Pesa PIN to confirm</li>
          <li>• Payment confirmation may take up to 30 seconds</li>
        </ul>
      </div>
    </div>
  );
};

export default MPesaPayment;
