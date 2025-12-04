package `in`.cittaa.vocalysis.data.api

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import dagger.hilt.android.qualifiers.ApplicationContext
import okhttp3.Interceptor
import okhttp3.Response
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Auth Interceptor for automatic token injection
 * Reads token from secure storage and adds Bearer header to all requests
 */
@Singleton
class AuthInterceptor @Inject constructor(
    @ApplicationContext private val context: Context
) : Interceptor {

    private val securePrefs: SharedPreferences by lazy {
        try {
            val masterKey = MasterKey.Builder(context)
                .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
                .build()
            
            EncryptedSharedPreferences.create(
                context,
                "vocalysis_secure_prefs",
                masterKey,
                EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
                EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
            )
        } catch (e: Exception) {
            // Fallback to regular SharedPreferences if encryption fails
            context.getSharedPreferences("vocalysis_prefs", Context.MODE_PRIVATE)
        }
    }

    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()
        
        // Skip auth header for login and register endpoints
        val path = originalRequest.url.encodedPath
        if (path.contains("/auth/login") || path.contains("/auth/register")) {
            return chain.proceed(originalRequest)
        }
        
        val token = getToken()
        
        return if (token != null) {
            val newRequest = originalRequest.newBuilder()
                .header("Authorization", "Bearer $token")
                .build()
            chain.proceed(newRequest)
        } else {
            chain.proceed(originalRequest)
        }
    }

    fun saveToken(token: String) {
        securePrefs.edit().putString(KEY_ACCESS_TOKEN, token).apply()
    }

    fun getToken(): String? {
        return securePrefs.getString(KEY_ACCESS_TOKEN, null)
    }

    fun saveUser(userId: String, email: String, fullName: String, role: String) {
        securePrefs.edit()
            .putString(KEY_USER_ID, userId)
            .putString(KEY_USER_EMAIL, email)
            .putString(KEY_USER_NAME, fullName)
            .putString(KEY_USER_ROLE, role)
            .apply()
    }

    fun getUserId(): String? = securePrefs.getString(KEY_USER_ID, null)
    fun getUserEmail(): String? = securePrefs.getString(KEY_USER_EMAIL, null)
    fun getUserName(): String? = securePrefs.getString(KEY_USER_NAME, null)
    fun getUserRole(): String? = securePrefs.getString(KEY_USER_ROLE, null)

    fun clearAuth() {
        securePrefs.edit()
            .remove(KEY_ACCESS_TOKEN)
            .remove(KEY_USER_ID)
            .remove(KEY_USER_EMAIL)
            .remove(KEY_USER_NAME)
            .remove(KEY_USER_ROLE)
            .apply()
    }

    fun isLoggedIn(): Boolean = getToken() != null

    companion object {
        private const val KEY_ACCESS_TOKEN = "access_token"
        private const val KEY_USER_ID = "user_id"
        private const val KEY_USER_EMAIL = "user_email"
        private const val KEY_USER_NAME = "user_name"
        private const val KEY_USER_ROLE = "user_role"
    }
}
