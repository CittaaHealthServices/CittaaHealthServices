"""
Load Testing Script for Vocalysis API
Target: 1000 requests/second
Uses locust for distributed load testing
"""

import json
import random
from locust import HttpUser, task, between, events
from locust.runners import MasterRunner
import time

# Test data
TEST_USERS = [
    {"email": "admin@cittaa.in", "password": "Admin@123"},
    {"email": "patient@cittaa.in", "password": "Patient@123"},
    {"email": "doctor@cittaa.in", "password": "Doctor@123"},
    {"email": "researcher@cittaa.in", "password": "Researcher@123"},
]

# Sample voice analysis request data
SAMPLE_VOICE_DATA = {
    "mfcc_features": [random.uniform(-2, 2) for _ in range(13)],
    "pitch_mean": random.uniform(100, 250),
    "pitch_std": random.uniform(10, 50),
    "jitter": random.uniform(0.01, 0.05),
    "shimmer": random.uniform(0.02, 0.10),
    "hnr": random.uniform(10, 25),
    "speech_rate": random.uniform(2, 5),
}


class VocalysisUser(HttpUser):
    """Simulates a user interacting with the Vocalysis API"""
    
    wait_time = between(0.1, 0.5)  # Fast requests for load testing
    token = None
    user_data = None
    
    def on_start(self):
        """Login when user starts"""
        self.user_data = random.choice(TEST_USERS)
        self.login()
    
    def login(self):
        """Authenticate and get token"""
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": self.user_data["email"],
                "password": self.user_data["password"]
            }
        )
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
        else:
            self.token = None
    
    def get_headers(self):
        """Get authorization headers"""
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}
    
    @task(10)
    def health_check(self):
        """Health check endpoint - most frequent"""
        self.client.get("/health")
    
    @task(5)
    def get_user_profile(self):
        """Get current user profile"""
        if self.token:
            self.client.get(
                "/api/v1/auth/me",
                headers=self.get_headers()
            )
    
    @task(3)
    def get_voice_history(self):
        """Get voice analysis history"""
        if self.token:
            self.client.get(
                "/api/v1/voice/history",
                headers=self.get_headers()
            )
    
    @task(2)
    def analyze_voice_demo(self):
        """Submit voice analysis (demo mode)"""
        if self.token:
            self.client.post(
                "/api/v1/voice/analyze/demo",
                headers=self.get_headers()
            )
    
    @task(1)
    def get_admin_stats(self):
        """Get admin statistics (admin users only)"""
        if self.token and self.user_data["email"] == "admin@cittaa.in":
            self.client.get(
                "/api/v1/admin/stats",
                headers=self.get_headers()
            )
    
    @task(1)
    def get_pending_approvals(self):
        """Get pending approvals (admin users only)"""
        if self.token and self.user_data["email"] == "admin@cittaa.in":
            self.client.get(
                "/api/v1/admin/pending-approvals",
                headers=self.get_headers()
            )


class VocalysisHighLoadUser(HttpUser):
    """High-frequency user for stress testing"""
    
    wait_time = between(0.01, 0.1)  # Very fast requests
    
    @task
    def health_check(self):
        """Rapid health checks"""
        self.client.get("/health")


# Custom event handlers for reporting
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, response, context, exception, **kwargs):
    """Log request metrics"""
    if exception:
        print(f"Request failed: {name} - {exception}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Test start handler"""
    print("=" * 60)
    print("Vocalysis Load Test Started")
    print(f"Target: 1000 requests/second")
    print("=" * 60)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Test stop handler - print summary"""
    print("=" * 60)
    print("Vocalysis Load Test Completed")
    print("=" * 60)
    
    if environment.stats.total.num_requests > 0:
        print(f"Total Requests: {environment.stats.total.num_requests}")
        print(f"Total Failures: {environment.stats.total.num_failures}")
        print(f"Average Response Time: {environment.stats.total.avg_response_time:.2f}ms")
        print(f"Requests/sec: {environment.stats.total.current_rps:.2f}")
        print(f"Failure Rate: {environment.stats.total.fail_ratio * 100:.2f}%")


# CLI runner for quick tests
if __name__ == "__main__":
    import subprocess
    import sys
    
    # Default test configuration
    host = "https://vocalysis-backend-1081764900204.us-central1.run.app"
    users = 100
    spawn_rate = 10
    run_time = "60s"
    
    print(f"Running load test against: {host}")
    print(f"Users: {users}, Spawn Rate: {spawn_rate}/s, Duration: {run_time}")
    
    # Run locust in headless mode
    cmd = [
        "locust",
        "-f", __file__,
        "--host", host,
        "--users", str(users),
        "--spawn-rate", str(spawn_rate),
        "--run-time", run_time,
        "--headless",
        "--only-summary"
    ]
    
    subprocess.run(cmd)
