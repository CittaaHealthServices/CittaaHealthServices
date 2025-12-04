package `in`.cittaa.vocalysis.data.repository

import `in`.cittaa.vocalysis.BuildConfig
import `in`.cittaa.vocalysis.data.api.*
import `in`.cittaa.vocalysis.data.models.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.util.UUID
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Repository for handling payments via Cashfree
 * Integrates with coupon system for discounts
 */
@Singleton
class PaymentRepository @Inject constructor(
    private val cashfreeService: CashfreeService,
    private val vocalysisApi: VocalysisApiService
) {
    // Cashfree credentials - In production, these should be fetched from secure storage or BuildConfig
    // Set these via gradle.properties or local.properties:
    // CASHFREE_CLIENT_ID=your_client_id
    // CASHFREE_CLIENT_SECRET=your_client_secret
    private val clientId = BuildConfig.CASHFREE_CLIENT_ID
    private val clientSecret = BuildConfig.CASHFREE_CLIENT_SECRET
    
    /**
     * Create a payment order for subscription
     */
    suspend fun createSubscriptionOrder(
        userId: String,
        userEmail: String,
        userPhone: String,
        userName: String,
        plan: SubscriptionPlan,
        isYearly: Boolean,
        couponCode: String? = null
    ): Result<PaymentOrder> = withContext(Dispatchers.IO) {
        try {
            // Calculate base price
            var amount = if (isYearly) {
                when (plan) {
                    SubscriptionPlan.PREMIUM_INDIVIDUAL -> 9999.0
                    SubscriptionPlan.PREMIUM_PLUS -> 19999.0
                    else -> 0.0
                }
            } else {
                when (plan) {
                    SubscriptionPlan.PREMIUM_INDIVIDUAL -> 999.0
                    SubscriptionPlan.PREMIUM_PLUS -> 1999.0
                    else -> 0.0
                }
            }
            
            // Apply coupon if provided
            var discountApplied = 0.0
            if (couponCode != null) {
                val couponResult = validateAndApplyCoupon(couponCode, userId, plan.name, amount)
                if (couponResult.isSuccess) {
                    val couponDiscount = couponResult.getOrNull() ?: 0.0
                    discountApplied = couponDiscount
                    amount -= couponDiscount
                }
            }
            
            // Generate unique order ID
            val orderId = "VOC_${System.currentTimeMillis()}_${UUID.randomUUID().toString().take(8)}"
            
            // Create Cashfree order
            val request = CreateOrderRequest(
                orderId = orderId,
                orderAmount = amount,
                orderCurrency = "INR",
                customerDetails = CustomerDetails(
                    customerId = userId,
                    customerEmail = userEmail,
                    customerPhone = userPhone,
                    customerName = userName
                ),
                orderMeta = OrderMeta(
                    returnUrl = "vocalysis://payment/callback",
                    notifyUrl = "https://vocalysis-backend-1081764900204.us-central1.run.app/api/v1/payments/webhook"
                ),
                orderNote = "Vocalysis ${plan.displayName} - ${if (isYearly) "Yearly" else "Monthly"}"
            )
            
            val response = cashfreeService.createOrder(
                clientId = clientId,
                clientSecret = clientSecret,
                request = request
            )
            
            Result.success(
                PaymentOrder(
                    orderId = response.orderId,
                    cfOrderId = response.cfOrderId ?: "",
                    amount = response.orderAmount,
                    originalAmount = amount + discountApplied,
                    discountApplied = discountApplied,
                    couponCode = couponCode,
                    currency = response.orderCurrency,
                    status = response.orderStatus,
                    paymentSessionId = response.paymentSessionId ?: "",
                    plan = plan,
                    isYearly = isYearly
                )
            )
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Validate and calculate coupon discount
     */
    private suspend fun validateAndApplyCoupon(
        code: String,
        userId: String,
        planId: String,
        originalAmount: Double
    ): Result<Double> {
        return try {
            val response = vocalysisApi.validateCoupon(
                CouponValidationRequest(
                    code = code,
                    userId = userId,
                    planId = planId
                )
            )
            
            if (response.valid) {
                val discount = when (response.discountType) {
                    DiscountType.PERCENT -> originalAmount * (response.discountValue ?: 0.0) / 100
                    DiscountType.AMOUNT -> response.discountValue ?: 0.0
                    DiscountType.FREE_TRIAL -> originalAmount // Full discount for free trial
                    else -> 0.0
                }
                Result.success(minOf(discount, originalAmount))
            } else {
                Result.failure(Exception(response.message))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Verify payment status
     */
    suspend fun verifyPayment(orderId: String): Result<PaymentStatus> = withContext(Dispatchers.IO) {
        try {
            val payments = cashfreeService.getPayments(
                clientId = clientId,
                clientSecret = clientSecret,
                orderId = orderId
            )
            
            val successfulPayment = payments.find { it.paymentStatus == "SUCCESS" }
            
            if (successfulPayment != null) {
                Result.success(
                    PaymentStatus(
                        orderId = orderId,
                        paymentId = successfulPayment.cfPaymentId,
                        status = PaymentStatusType.SUCCESS,
                        amount = successfulPayment.paymentAmount,
                        paymentTime = successfulPayment.paymentTime
                    )
                )
            } else {
                val latestPayment = payments.firstOrNull()
                Result.success(
                    PaymentStatus(
                        orderId = orderId,
                        paymentId = latestPayment?.cfPaymentId ?: "",
                        status = when (latestPayment?.paymentStatus) {
                            "PENDING" -> PaymentStatusType.PENDING
                            "FAILED" -> PaymentStatusType.FAILED
                            else -> PaymentStatusType.UNKNOWN
                        },
                        amount = latestPayment?.paymentAmount ?: 0.0,
                        paymentTime = latestPayment?.paymentTime
                    )
                )
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Create recurring subscription
     */
    suspend fun createRecurringSubscription(
        userId: String,
        userEmail: String,
        userPhone: String,
        userName: String,
        plan: SubscriptionPlan,
        isYearly: Boolean
    ): Result<SubscriptionResponse> = withContext(Dispatchers.IO) {
        try {
            val planId = when {
                plan == SubscriptionPlan.PREMIUM_INDIVIDUAL && !isYearly -> VocalysisPlans.PREMIUM_INDIVIDUAL_MONTHLY
                plan == SubscriptionPlan.PREMIUM_INDIVIDUAL && isYearly -> VocalysisPlans.PREMIUM_INDIVIDUAL_YEARLY
                plan == SubscriptionPlan.PREMIUM_PLUS && !isYearly -> VocalysisPlans.PREMIUM_PLUS_MONTHLY
                plan == SubscriptionPlan.PREMIUM_PLUS && isYearly -> VocalysisPlans.PREMIUM_PLUS_YEARLY
                else -> throw IllegalArgumentException("Invalid plan")
            }
            
            val subscriptionId = "SUB_${System.currentTimeMillis()}_${UUID.randomUUID().toString().take(8)}"
            
            val request = CreateSubscriptionRequest(
                subscriptionId = subscriptionId,
                planId = planId,
                customerDetails = CustomerDetails(
                    customerId = userId,
                    customerEmail = userEmail,
                    customerPhone = userPhone,
                    customerName = userName
                ),
                authorizationDetails = AuthorizationDetails(
                    authorizationAmount = 1.0,
                    authorizationAmountRefund = true
                ),
                subscriptionMeta = SubscriptionMeta(
                    returnUrl = "vocalysis://subscription/callback",
                    notifyUrl = "https://vocalysis-backend-1081764900204.us-central1.run.app/api/v1/subscriptions/webhook"
                )
            )
            
            val response = cashfreeService.createSubscription(
                clientId = clientId,
                clientSecret = clientSecret,
                request = request
            )
            
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Cancel subscription
     */
    suspend fun cancelSubscription(subscriptionId: String): Result<SubscriptionResponse> = withContext(Dispatchers.IO) {
        try {
            val response = cashfreeService.cancelSubscription(
                clientId = clientId,
                clientSecret = clientSecret,
                subscriptionId = subscriptionId
            )
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

// Local data classes

data class PaymentOrder(
    val orderId: String,
    val cfOrderId: String,
    val amount: Double,
    val originalAmount: Double,
    val discountApplied: Double,
    val couponCode: String?,
    val currency: String,
    val status: String,
    val paymentSessionId: String,
    val plan: SubscriptionPlan,
    val isYearly: Boolean
)

data class PaymentStatus(
    val orderId: String,
    val paymentId: String,
    val status: PaymentStatusType,
    val amount: Double,
    val paymentTime: String?
)

enum class PaymentStatusType {
    SUCCESS,
    PENDING,
    FAILED,
    UNKNOWN
}

// API Service interface for Vocalysis backend
interface VocalysisApiService {
    suspend fun validateCoupon(request: CouponValidationRequest): CouponValidationResponse
    suspend fun redeemCoupon(request: CouponRedemptionRequest): CouponRedemptionResponse
}
