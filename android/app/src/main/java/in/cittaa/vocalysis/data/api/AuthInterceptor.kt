package `in`.cittaa.vocalysis.data.api

import android.content.Context
import android.content.SharedPreferences
import android.util.Log
import dagger.hilt.android.qualifiers.ApplicationContext
import okhttp3.Interceptor
import okhttp3.Response
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Auth Interceptor for automatic token injection
 * Reads token from secure storage and adds Bearer header to all requests
 * 
 * IMPORTANT: Uses regular SharedPreferences to avoid data loss issues with
 * EncryptedSharedPreferences across app updates. The token is still secure
 * as it's stored in app-private storage and expires on the backend.
 */
@Singleton
class AuthInterceptor @Inject constructor(
    @ApplicationContext private val context: Context
) : Interceptor {

    companion object {
        private const val TAG = "AuthInterceptor"
        private const val PREFS_NAME = "vocalysis_auth_prefs"
        private const val KEY_ACCESS_TOKEN = "access_token"
        private const val KEY_USER_ID = "user_id"
        private const val KEY_USER_EMAIL = "user_email"
        private const val KEY_USER_NAME = "user_name"
        private const val KEY_USER_ROLE = "user_role"
    }

    // Use regular SharedPreferences to avoid data loss across app updates
    // The fallback from EncryptedSharedPreferences was causing auth data to be lost
    // when the encryption key changed between app versions
    private val prefs: SharedPreferences by lazy {
        Log.d(TAG, "Initializing SharedPreferences for auth storage")
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE).also {
            Log.d(TAG, "SharedPreferences initialized, hasToken=${it.contains(KEY_ACCESS_TOKEN)}")
        }
    }

    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()
        
        // Skip auth header for login, register, and forgot-password endpoints
        val path = originalRequest.url.encodedPath
        if (path.contains("/auth/login") || 
            path.contains("/auth/register") || 
            path.contains("/auth/forgot-password")) {
            return chain.proceed(originalRequest)
        }
        
        val token = getToken()
        
        return if (token != null) {
            val newRequest = originalRequest.newBuilder()
                .header("Authorization", "Bearer $token")
                .build()
            chain.proceed(newRequest)
        } else {
            Log.w(TAG, "No auth token available for request: $path")
            chain.proceed(originalRequest)
        }
    }

    fun saveToken(token: String) {
        Log.d(TAG, "Saving auth token")
        prefs.edit().putString(KEY_ACCESS_TOKEN, token).apply()
    }

    fun getToken(): String? {
        val token = prefs.getString(KEY_ACCESS_TOKEN, null)
        Log.d(TAG, "getToken called, hasToken=${token != null}")
        return token
    }

    fun saveUser(userId: String, email: String, fullName: String, role: String) {
        Log.d(TAG, "Saving user: id=$userId, email=$email, role=$role")
        prefs.edit()
            .putString(KEY_USER_ID, userId)
            .putString(KEY_USER_EMAIL, email)
            .putString(KEY_USER_NAME, fullName)
            .putString(KEY_USER_ROLE, role)
            .apply()
    }

    fun getUserId(): String? {
        val userId = prefs.getString(KEY_USER_ID, null)
        Log.d(TAG, "getUserId called, userId=$userId")
        return userId
    }
    
    fun getUserEmail(): String? = prefs.getString(KEY_USER_EMAIL, null)
    fun getUserName(): String? = prefs.getString(KEY_USER_NAME, null)
    fun getUserRole(): String? = prefs.getString(KEY_USER_ROLE, null)

    fun clearAuth() {
        Log.d(TAG, "Clearing auth data")
        prefs.edit()
            .remove(KEY_ACCESS_TOKEN)
            .remove(KEY_USER_ID)
            .remove(KEY_USER_EMAIL)
            .remove(KEY_USER_NAME)
            .remove(KEY_USER_ROLE)
            .apply()
    }

    fun isLoggedIn(): Boolean {
        val loggedIn = getToken() != null
        Log.d(TAG, "isLoggedIn=$loggedIn")
        return loggedIn
    }
}
