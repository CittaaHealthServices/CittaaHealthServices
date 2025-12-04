package `in`.cittaa.vocalysis.data.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

/**
 * Coupon/Promo Code System
 * Supports: Percentage discount, Fixed amount, Free trial
 * Single-use per person
 */

@Serializable
data class Coupon(
    val id: String,
    val code: String,
    val description: String,
    @SerialName("discount_type") val discountType: DiscountType,
    @SerialName("discount_value") val discountValue: Double,
    @SerialName("applies_to_plan") val appliesToPlan: SubscriptionPlan? = null,
    @SerialName("max_redemptions") val maxRedemptions: Int? = null,
    @SerialName("per_user_limit") val perUserLimit: Int = 1,
    @SerialName("start_at") val startAt: String? = null,
    @SerialName("expires_at") val expiresAt: String? = null,
    val status: CouponStatus = CouponStatus.ACTIVE,
    @SerialName("usage_count") val usageCount: Int = 0,
    @SerialName("created_by") val createdBy: String? = null,
    @SerialName("created_at") val createdAt: String? = null
)

@Serializable
enum class DiscountType(val displayName: String) {
    @SerialName("percent") PERCENT("Percentage Off"),
    @SerialName("amount") AMOUNT("Fixed Amount Off"),
    @SerialName("free_trial") FREE_TRIAL("Free Trial Period")
}

@Serializable
enum class CouponStatus {
    @SerialName("active") ACTIVE,
    @SerialName("inactive") INACTIVE,
    @SerialName("expired") EXPIRED
}

@Serializable
enum class SubscriptionPlan(val displayName: String, val priceMonthly: Int, val priceYearly: Int) {
    @SerialName("free") FREE("Free", 0, 0),
    @SerialName("premium_individual") PREMIUM_INDIVIDUAL("Premium Individual", 999, 9999),
    @SerialName("premium_plus") PREMIUM_PLUS("Premium Plus", 1999, 19999),
    @SerialName("corporate") CORPORATE("Corporate Wellness", 0, 0) // Custom pricing
}

@Serializable
data class CouponValidationRequest(
    val code: String,
    @SerialName("user_id") val userId: String,
    @SerialName("plan_id") val planId: String
)

@Serializable
data class CouponValidationResponse(
    val valid: Boolean,
    @SerialName("discount_type") val discountType: DiscountType? = null,
    @SerialName("discount_value") val discountValue: Double? = null,
    val message: String,
    @SerialName("applies_to_plan") val appliesToPlan: String? = null,
    @SerialName("final_price") val finalPrice: Double? = null
)

@Serializable
data class CouponRedemptionRequest(
    val code: String,
    @SerialName("user_id") val userId: String,
    @SerialName("subscription_id") val subscriptionId: String
)

@Serializable
data class CouponRedemptionResponse(
    val success: Boolean,
    val message: String,
    @SerialName("redemption_id") val redemptionId: String? = null,
    @SerialName("discount_applied") val discountApplied: Double? = null
)

@Serializable
data class CreateCouponRequest(
    val code: String,
    val description: String,
    @SerialName("discount_type") val discountType: DiscountType,
    @SerialName("discount_value") val discountValue: Double,
    @SerialName("applies_to_plan") val appliesToPlan: SubscriptionPlan? = null,
    @SerialName("max_redemptions") val maxRedemptions: Int? = null,
    @SerialName("per_user_limit") val perUserLimit: Int = 1,
    @SerialName("start_at") val startAt: String? = null,
    @SerialName("expires_at") val expiresAt: String? = null
)

// Subscription & Payment Models

@Serializable
data class Subscription(
    val id: String,
    @SerialName("user_id") val userId: String,
    val plan: SubscriptionPlan,
    val status: SubscriptionStatus,
    @SerialName("payment_provider") val paymentProvider: PaymentProvider,
    @SerialName("provider_subscription_id") val providerSubscriptionId: String? = null,
    @SerialName("current_period_start") val currentPeriodStart: String,
    @SerialName("current_period_end") val currentPeriodEnd: String,
    @SerialName("cancel_at_period_end") val cancelAtPeriodEnd: Boolean = false,
    @SerialName("coupon_applied") val couponApplied: String? = null,
    @SerialName("created_at") val createdAt: String
)

@Serializable
enum class SubscriptionStatus {
    @SerialName("active") ACTIVE,
    @SerialName("trialing") TRIALING,
    @SerialName("past_due") PAST_DUE,
    @SerialName("canceled") CANCELED,
    @SerialName("expired") EXPIRED
}

@Serializable
enum class PaymentProvider(val displayName: String) {
    @SerialName("razorpay") RAZORPAY("Razorpay"),
    @SerialName("apple") APPLE("Apple In-App Purchase"),
    @SerialName("google") GOOGLE("Google Play Billing")
}

@Serializable
data class RazorpayOrder(
    val id: String,
    val amount: Int, // in paise
    val currency: String = "INR",
    @SerialName("receipt") val receipt: String,
    val status: String
)

@Serializable
data class PaymentVerificationRequest(
    @SerialName("razorpay_order_id") val razorpayOrderId: String,
    @SerialName("razorpay_payment_id") val razorpayPaymentId: String,
    @SerialName("razorpay_signature") val razorpaySignature: String
)
