/**
 * M-Pesa Payment Service
 * Handles M-Pesa mobile money payments for contract analysis services
 */

export interface MPesaPaymentRequest {
  phoneNumber: string;
  amount: number;
  accountReference: string;
  transactionDesc: string;
  callBackURL?: string;
}

export interface MPesaPaymentResponse {
  success: boolean;
  transactionId?: string;
  message: string;
  errorCode?: string;
  errorMessage?: string;
}

export interface PaymentConfirmation {
  transactionId: string;
  phoneNumber: string;
  amount: number;
  timestamp: string;
  status: 'completed' | 'pending' | 'failed';
}

class MPesaService {
  private baseURL: string;
  private consumerKey: string;
  private consumerSecret: string;
  private passKey: string;
  private shortCode: string;

  constructor() {
    // M-Pesa Dar es Salaam API configuration
    this.baseURL = process.env.NEXT_PUBLIC_MPESA_BASE_URL || 'https://sandbox.safaricom.co.ke/mpesa/';
    this.consumerKey = process.env.NEXT_PUBLIC_MPESA_CONSUMER_KEY || '';
    this.consumerSecret = process.env.NEXT_PUBLIC_MPESA_CONSUMER_SECRET || '';
    this.passKey = process.env.NEXT_PUBLIC_MPESA_PASSKEY || '';
    this.shortCode = process.env.NEXT_PUBLIC_MPESA_SHORTCODE || '174379';
  }

  /**
   * Initiate M-Pesa STK Push payment
   */
  async initiatePayment(paymentRequest: MPesaPaymentRequest): Promise<MPesaPaymentResponse> {
    try {
      // Step 1: Get OAuth token
      const token = await this.getOAuthToken();
      
      // Step 2: Initiate STK Push
      const timestamp = new Date().toISOString().replace(/[-:T.Z]/g, '').substring(0, 14);
      const password = this.generatePassword(timestamp);
      
      const stkPushRequest = {
        BusinessShortCode: this.shortCode,
        Password: password,
        Timestamp: timestamp,
        TransactionType: 'CustomerPayBillOnline',
        Amount: paymentRequest.amount,
        PartyA: paymentRequest.phoneNumber,
        PartyB: this.shortCode,
        PhoneNumber: paymentRequest.phoneNumber,
        CallBackURL: paymentRequest.callBackURL || `${window.location.origin}/api/payments/mpesa/callback`,
        AccountReference: paymentRequest.accountReference,
        TransactionDesc: paymentRequest.transactionDesc
      };

      const response = await fetch(`${this.baseURL}mpesa/stkpush/v1/processrequest`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(stkPushRequest)
      });

      const result = await response.json();
      
      if (result.ResponseCode === '0') {
        return {
          success: true,
          transactionId: result.CheckoutRequestID,
          message: 'Payment initiated successfully'
        };
      } else {
        return {
          success: false,
          message: result.ResponseDescription || 'Payment initiation failed',
          errorCode: result.ResponseCode
        };
      }
    } catch (error) {
      console.error('M-Pesa payment error:', error);
      return {
        success: false,
        message: 'Payment service unavailable',
        errorMessage: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  /**
   * Get OAuth token for M-Pesa API
   */
  private async getOAuthToken(): Promise<string> {
    const auth = Buffer.from(`${this.consumerKey}:${this.consumerSecret}`).toString('base64');
    
    const response = await fetch(`${this.baseURL}oauth/v1/generate?grant_type=client_credentials`, {
      method: 'GET',
      headers: {
        'Authorization': `Basic ${auth}`,
        'Content-Type': 'application/json',
      }
    });

    const result = await response.json();
    return result.access_token;
  }

  /**
   * Generate password for STK push
   */
  private generatePassword(timestamp: string): string {
    const data = `${this.shortCode}${this.passKey}${timestamp}`;
    return Buffer.from(data).toString('base64');
  }

  /**
   * Check payment status
   */
  async checkPaymentStatus(checkoutRequestID: string): Promise<PaymentConfirmation> {
    try {
      // In a real implementation, this would query your database
      // For now, return a mock response
      return {
        transactionId: checkoutRequestID,
        phoneNumber: '',
        amount: 0,
        timestamp: new Date().toISOString(),
        status: 'pending'
      };
    } catch (error) {
      throw new Error('Failed to check payment status');
    }
  }

  /**
   * Validate phone number for M-Pesa
   */
  validatePhoneNumber(phoneNumber: string): boolean {
    // Remove spaces, +, and leading zeros
    const cleaned = phoneNumber.replace(/[\s+]/g, '').replace(/^0+/, '');
    
    // Check if it's a valid Kenyan number (7-9 digits, starts with 1, 7, or 0)
    const kenyanPhoneRegex = /^(1|7)[0-9]{8}$/;
    return kenyanPhoneRegex.test(cleaned);
  }

  /**
   * Format amount for M-Pesa (minimum KES 10)
   */
  formatAmount(amount: number): number {
    const minimumAmount = 10;
    return Math.max(amount, minimumAmount);
  }
}

export default MPesaService;
