package `in`.cittaa.vocalysis.data.api

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import retrofit2.http.*

/**
 * Cashfree Payment Gateway Integration
 * Documentation: https://docs.cashfree.com/docs/
 */
interface CashfreeService {
    
    /**
     * Create a new payment order
     */
    @POST("orders")
    suspend fun createOrder(
        @Header("x-client-id") clientId: String,
        @Header("x-client-secret") clientSecret: String,
        @Header("x-api-version") apiVersion: String = "2023-08-01",
        @Body request: CreateOrderRequest
    ): OrderResponse
    
    /**
     * Get order details
     */
    @GET("orders/{order_id}")
    suspend fun getOrder(
        @Header("x-client-id") clientId: String,
        @Header("x-client-secret") clientSecret: String,
        @Header("x-api-version") apiVersion: String = "2023-08-01",
        @Path("order_id") orderId: String
    ): OrderResponse
    
    /**
     * Get payments for an order
     */
    @GET("orders/{order_id}/payments")
    suspend fun getPayments(
        @Header("x-client-id") clientId: String,
        @Header("x-client-secret") clientSecret: String,
        @Header("x-api-version") apiVersion: String = "2023-08-01",
        @Path("order_id") orderId: String
    ): List<PaymentResponse>
    
    /**
     * Create a subscription
     */
    @POST("subscriptions")
    suspend fun createSubscription(
        @Header("x-client-id") clientId: String,
        @Header("x-client-secret") clientSecret: String,
        @Header("x-api-version") apiVersion: String = "2023-08-01",
        @Body request: CreateSubscriptionRequest
    ): SubscriptionResponse
    
    /**
     * Get subscription details
     */
    @GET("subscriptions/{subscription_id}")
    suspend fun getSubscription(
        @Header("x-client-id") clientId: String,
        @Header("x-client-secret") clientSecret: String,
        @Header("x-api-version") apiVersion: String = "2023-08-01",
        @Path("subscription_id") subscriptionId: String
    ): SubscriptionResponse
    
    /**
     * Cancel a subscription
     */
    @POST("subscriptions/{subscription_id}/cancel")
    suspend fun cancelSubscription(
        @Header("x-client-id") clientId: String,
        @Header("x-client-secret") clientSecret: String,
        @Header("x-api-version") apiVersion: String = "2023-08-01",
        @Path("subscription_id") subscriptionId: String
    ): SubscriptionResponse
}

// Request Models

@Serializable
data class CreateOrderRequest(
    @SerialName("order_id") val orderId: String,
    @SerialName("order_amount") val orderAmount: Double,
    @SerialName("order_currency") val orderCurrency: String = "INR",
    @SerialName("customer_details") val customerDetails: CustomerDetails,
    @SerialName("order_meta") val orderMeta: OrderMeta? = null,
    @SerialName("order_note") val orderNote: String? = null
)

@Serializable
data class CustomerDetails(
    @SerialName("customer_id") val customerId: String,
    @SerialName("customer_email") val customerEmail: String,
    @SerialName("customer_phone") val customerPhone: String,
    @SerialName("customer_name") val customerName: String? = null
)

@Serializable
data class OrderMeta(
    @SerialName("return_url") val returnUrl: String? = null,
    @SerialName("notify_url") val notifyUrl: String? = null,
    @SerialName("payment_methods") val paymentMethods: String? = null
)

@Serializable
data class CreateSubscriptionRequest(
    @SerialName("subscription_id") val subscriptionId: String,
    @SerialName("plan_id") val planId: String,
    @SerialName("customer_details") val customerDetails: CustomerDetails,
    @SerialName("authorization_details") val authorizationDetails: AuthorizationDetails? = null,
    @SerialName("subscription_meta") val subscriptionMeta: SubscriptionMeta? = null
)

@Serializable
data class AuthorizationDetails(
    @SerialName("authorization_amount") val authorizationAmount: Double,
    @SerialName("authorization_amount_refund") val authorizationAmountRefund: Boolean = true
)

@Serializable
data class SubscriptionMeta(
    @SerialName("return_url") val returnUrl: String? = null,
    @SerialName("notify_url") val notifyUrl: String? = null
)

// Response Models

@Serializable
data class OrderResponse(
    @SerialName("cf_order_id") val cfOrderId: String? = null,
    @SerialName("order_id") val orderId: String,
    @SerialName("order_amount") val orderAmount: Double,
    @SerialName("order_currency") val orderCurrency: String,
    @SerialName("order_status") val orderStatus: String,
    @SerialName("payment_session_id") val paymentSessionId: String? = null,
    @SerialName("order_expiry_time") val orderExpiryTime: String? = null,
    @SerialName("order_note") val orderNote: String? = null,
    @SerialName("customer_details") val customerDetails: CustomerDetails? = null,
    @SerialName("payments") val payments: PaymentsInfo? = null
)

@Serializable
data class PaymentsInfo(
    val url: String? = null
)

@Serializable
data class PaymentResponse(
    @SerialName("cf_payment_id") val cfPaymentId: String,
    @SerialName("order_id") val orderId: String,
    @SerialName("payment_amount") val paymentAmount: Double,
    @SerialName("payment_currency") val paymentCurrency: String,
    @SerialName("payment_status") val paymentStatus: String,
    @SerialName("payment_time") val paymentTime: String? = null,
    @SerialName("payment_method") val paymentMethod: PaymentMethod? = null,
    @SerialName("bank_reference") val bankReference: String? = null
)

@Serializable
data class PaymentMethod(
    val upi: UpiPayment? = null,
    val card: CardPayment? = null,
    val netbanking: NetbankingPayment? = null
)

@Serializable
data class UpiPayment(
    val channel: String? = null,
    @SerialName("upi_id") val upiId: String? = null
)

@Serializable
data class CardPayment(
    val channel: String? = null,
    @SerialName("card_number") val cardNumber: String? = null,
    @SerialName("card_network") val cardNetwork: String? = null,
    @SerialName("card_type") val cardType: String? = null
)

@Serializable
data class NetbankingPayment(
    val channel: String? = null,
    @SerialName("netbanking_bank_code") val netbankingBankCode: String? = null,
    @SerialName("netbanking_bank_name") val netbankingBankName: String? = null
)

@Serializable
data class SubscriptionResponse(
    @SerialName("cf_subscription_id") val cfSubscriptionId: String? = null,
    @SerialName("subscription_id") val subscriptionId: String,
    @SerialName("plan_id") val planId: String,
    @SerialName("subscription_status") val subscriptionStatus: String,
    @SerialName("subscription_expiry_time") val subscriptionExpiryTime: String? = null,
    @SerialName("customer_details") val customerDetails: CustomerDetails? = null,
    @SerialName("authorization_details") val authorizationDetails: AuthorizationDetails? = null
)

// Subscription Plans for Vocalysis
object VocalysisPlans {
    const val PREMIUM_INDIVIDUAL_MONTHLY = "vocalysis_premium_monthly"
    const val PREMIUM_INDIVIDUAL_YEARLY = "vocalysis_premium_yearly"
    const val PREMIUM_PLUS_MONTHLY = "vocalysis_premium_plus_monthly"
    const val PREMIUM_PLUS_YEARLY = "vocalysis_premium_plus_yearly"
    
    val planPrices = mapOf(
        PREMIUM_INDIVIDUAL_MONTHLY to 999.0,
        PREMIUM_INDIVIDUAL_YEARLY to 9999.0,
        PREMIUM_PLUS_MONTHLY to 1999.0,
        PREMIUM_PLUS_YEARLY to 19999.0
    )
}
