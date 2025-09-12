class ApiClient {
  constructor() {
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const baseUrl = 'https://invisible-parental-control-app-tunnel-wg23lz5v.devinapps.com'
    const url = `${baseUrl}${endpoint}`
    
    const defaultHeaders: HeadersInit = {
      'Content-Type': 'application/json',
      'Authorization': 'Basic ' + btoa('user:1af8d504a70e676be22fe020844d99c8'),
    }
    
    const requestHeaders = { ...defaultHeaders }
    
    if (options.headers) {
      Object.assign(requestHeaders, options.headers)
    }
    
    const response = await fetch(url, {
      mode: 'cors',
      credentials: 'omit',
      headers: requestHeaders,
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

  async generateMobileProfile(token: string, data: {
    child_id: number
    device_type: string
    device_id: string
  }) {
    return this.request('/mobile-profile/generate', {
      method: 'POST',
      headers: this.getAuthHeaders(token),
      body: JSON.stringify(data),
    })
  }

  async listMobileProfiles(token: string) {
    return this.request('/mobile-profile/list', {
      headers: this.getAuthHeaders(token),
    })
  }

  async downloadMobileProfile(downloadToken: string) {
    return this.request(`/mobile-profile/download/${downloadToken}`)
  }

  async activateMobileProfile(downloadToken: string) {
    return this.request(`/mobile-profile/activate/${downloadToken}`, {
      method: 'POST',
    })
  }
}

const familyApi = new ApiClient()

export { familyApi }
