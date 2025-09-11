const API_BASE_URL = 'http://localhost:8000'


class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    })

    if (!response.ok) {
      const error = await response.text()
      throw new Error(error || 'API request failed')
    }

    return response.json()
  }

  private getAuthHeaders(token: string) {
    return {
      Authorization: `Bearer ${token}`,
    }
  }

  async register(data: {
    email: string
    password: string
    full_name: string
    phone_number?: string
    family_name: string
  }) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async login(data: { email: string; password: string }) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async getOverview(token: string) {
    return this.request('/family/overview', {
      headers: this.getAuthHeaders(token),
    })
  }

  async createChild(token: string, data: {
    full_name: string
    age: number
    date_of_birth: string
    safety_password: string
  }) {
    return this.request('/children', {
      method: 'POST',
      headers: this.getAuthHeaders(token),
      body: JSON.stringify(data),
    })
  }

  async manageConsent(token: string, data: {
    child_id: number
    consent_type: string
    consent_given: boolean
    parent_consent: boolean
  }) {
    return this.request('/consent', {
      method: 'POST',
      headers: this.getAuthHeaders(token),
      body: JSON.stringify(data),
    })
  }

  async getChildConsentStatus(token: string, childId: number) {
    return this.request(`/children/${childId}/consent-status`, {
      headers: this.getAuthHeaders(token),
    })
  }

  async getChildActivity(token: string, childId: number) {
    return this.request(`/children/${childId}/activity`, {
      headers: this.getAuthHeaders(token),
    })
  }

  async getEducationalProgress(token: string, childId: number) {
    return this.request(`/educational/progress/${childId}`, {
      headers: this.getAuthHeaders(token),
    })
  }

  async checkContentFilter(url: string, childAge: number) {
    return this.request(`/content-filter/check?url=${encodeURIComponent(url)}&child_age=${childAge}`)
  }
}

const familyApi = new ApiClient(API_BASE_URL)

export { familyApi }
