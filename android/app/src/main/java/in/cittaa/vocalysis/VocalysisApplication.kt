package `in`.cittaa.vocalysis

import android.app.Application
import dagger.hilt.android.HiltAndroidApp

@HiltAndroidApp
class VocalysisApplication : Application() {
    
    override fun onCreate() {
        super.onCreate()
        // Initialize any app-wide components here
    }
}
