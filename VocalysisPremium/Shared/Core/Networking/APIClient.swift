import Foundation

// MARK: - API Client

/// Main API client for Vocalysis backend communication
final class APIClient {
    
    // MARK: - Properties
    
    static let shared = APIClient()
    
    let baseURL: URL
    private let urlSession: URLSession
    private let jsonDecoder: JSONDecoder
    private let jsonEncoder: JSONEncoder
    
    /// Token provider closure - returns current auth token
    var tokenProvider: (() -> String?)?
    
    // MARK: - Initialization
    
    init(
        baseURL: URL = URL(string: "https://vocalysis-backend-1081764900204.us-central1.run.app/api/v1")!,
        urlSession: URLSession = .shared
    ) {
        self.baseURL = baseURL
        self.urlSession = urlSession
        
        // Configure JSON decoder with date handling
        self.jsonDecoder = JSONDecoder()
        jsonDecoder.dateDecodingStrategy = .custom { decoder in
            let container = try decoder.singleValueContainer()
            let dateString = try container.decode(String.self)
            
            // Try ISO8601 with fractional seconds
            let formatter = ISO8601DateFormatter()
            formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
            if let date = formatter.date(from: dateString) {
                return date
            }
            
            // Try ISO8601 without fractional seconds
            formatter.formatOptions = [.withInternetDateTime]
            if let date = formatter.date(from: dateString) {
                return date
            }
            
            throw DecodingError.dataCorruptedError(
                in: container,
                debugDescription: "Cannot decode date: \(dateString)"
            )
        }
        
        // Configure JSON encoder
        self.jsonEncoder = JSONEncoder()
        jsonEncoder.dateEncodingStrategy = .iso8601
    }
    
    // MARK: - Request Building
    
    /// Build a URL request with authentication
    func buildRequest(
        endpoint: String,
        method: HTTPMethod,
        body: Data? = nil,
        contentType: ContentType = .json,
        requiresAuth: Bool = true
    ) -> URLRequest {
        let url = baseURL.appendingPathComponent(endpoint)
        var request = URLRequest(url: url)
        request.httpMethod = method.rawValue
        request.httpBody = body
        
        // Set content type
        if let contentTypeHeader = contentType.headerValue {
            request.setValue(contentTypeHeader, forHTTPHeaderField: "Content-Type")
        }
        
        // Add auth token if required
        if requiresAuth, let token = tokenProvider?() {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        // Common headers
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        request.setValue("VocalysisPremium-iOS/1.0", forHTTPHeaderField: "User-Agent")
        
        return request
    }
    
    // MARK: - Request Execution
    
    /// Perform a request and decode the response
    func perform<T: Decodable>(
        _ request: URLRequest,
        as type: T.Type
    ) async throws -> T {
        let (data, response) = try await urlSession.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        // Handle HTTP status codes
        switch httpResponse.statusCode {
        case 200...299:
            do {
                return try jsonDecoder.decode(T.self, from: data)
            } catch {
                print("Decoding error: \(error)")
                throw APIError.decodingError(error)
            }
            
        case 401:
            throw APIError.unauthorized
            
        case 403:
            throw APIError.forbidden
            
        case 404:
            throw APIError.notFound
            
        case 422:
            // Validation error
            if let errorResponse = try? jsonDecoder.decode(ValidationErrorResponse.self, from: data) {
                throw APIError.validationError(errorResponse.detail)
            }
            throw APIError.validationError([])
            
        case 500...599:
            throw APIError.serverError(httpResponse.statusCode)
            
        default:
            throw APIError.httpError(httpResponse.statusCode, data)
        }
    }
    
    /// Perform a request without expecting a response body
    func performVoid(_ request: URLRequest) async throws {
        let (data, response) = try await urlSession.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        guard (200...299).contains(httpResponse.statusCode) else {
            if httpResponse.statusCode == 401 {
                throw APIError.unauthorized
            }
            throw APIError.httpError(httpResponse.statusCode, data)
        }
    }
    
    // MARK: - Multipart Upload
    
    /// Upload a file using multipart/form-data
    func uploadMultipart<T: Decodable>(
        endpoint: String,
        fileData: Data,
        fileName: String,
        mimeType: String,
        fieldName: String = "file",
        additionalFields: [String: String] = [:],
        as type: T.Type
    ) async throws -> T {
        let boundary = UUID().uuidString
        let url = baseURL.appendingPathComponent(endpoint)
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        
        // Add auth token
        if let token = tokenProvider?() {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        // Build multipart body
        var body = Data()
        
        // Add file field
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"\(fieldName)\"; filename=\"\(fileName)\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: \(mimeType)\r\n\r\n".data(using: .utf8)!)
        body.append(fileData)
        body.append("\r\n".data(using: .utf8)!)
        
        // Add additional fields
        for (key, value) in additionalFields {
            body.append("--\(boundary)\r\n".data(using: .utf8)!)
            body.append("Content-Disposition: form-data; name=\"\(key)\"\r\n\r\n".data(using: .utf8)!)
            body.append("\(value)\r\n".data(using: .utf8)!)
        }
        
        // Close boundary
        body.append("--\(boundary)--\r\n".data(using: .utf8)!)
        
        request.httpBody = body
        
        return try await perform(request, as: type)
    }
    
    // MARK: - Convenience Methods
    
    /// GET request
    func get<T: Decodable>(
        _ endpoint: String,
        queryItems: [URLQueryItem]? = nil,
        requiresAuth: Bool = true,
        as type: T.Type
    ) async throws -> T {
        var url = baseURL.appendingPathComponent(endpoint)
        
        if let queryItems = queryItems, !queryItems.isEmpty {
            var components = URLComponents(url: url, resolvingAgainstBaseURL: false)!
            components.queryItems = queryItems
            url = components.url!
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        
        if requiresAuth, let token = tokenProvider?() {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        return try await perform(request, as: type)
    }
    
    /// POST request with JSON body
    func post<T: Decodable, B: Encodable>(
        _ endpoint: String,
        body: B,
        requiresAuth: Bool = true,
        as type: T.Type
    ) async throws -> T {
        let bodyData = try jsonEncoder.encode(body)
        let request = buildRequest(
            endpoint: endpoint,
            method: .post,
            body: bodyData,
            requiresAuth: requiresAuth
        )
        return try await perform(request, as: type)
    }
    
    /// PUT request with JSON body
    func put<T: Decodable, B: Encodable>(
        _ endpoint: String,
        body: B,
        requiresAuth: Bool = true,
        as type: T.Type
    ) async throws -> T {
        let bodyData = try jsonEncoder.encode(body)
        let request = buildRequest(
            endpoint: endpoint,
            method: .put,
            body: bodyData,
            requiresAuth: requiresAuth
        )
        return try await perform(request, as: type)
    }
    
    /// DELETE request
    func delete(
        _ endpoint: String,
        requiresAuth: Bool = true
    ) async throws {
        let request = buildRequest(
            endpoint: endpoint,
            method: .delete,
            requiresAuth: requiresAuth
        )
        try await performVoid(request)
    }
}

// MARK: - Supporting Types

enum HTTPMethod: String {
    case get = "GET"
    case post = "POST"
    case put = "PUT"
    case patch = "PATCH"
    case delete = "DELETE"
}

enum ContentType {
    case json
    case formData
    case multipart(boundary: String)
    
    var headerValue: String? {
        switch self {
        case .json:
            return "application/json"
        case .formData:
            return "application/x-www-form-urlencoded"
        case .multipart(let boundary):
            return "multipart/form-data; boundary=\(boundary)"
        }
    }
}

// MARK: - API Errors

enum APIError: Error, LocalizedError {
    case invalidResponse
    case unauthorized
    case forbidden
    case notFound
    case validationError([ValidationErrorDetail])
    case serverError(Int)
    case httpError(Int, Data)
    case decodingError(Error)
    case networkError(Error)
    case unknown
    
    var errorDescription: String? {
        switch self {
        case .invalidResponse:
            return "Invalid response from server"
        case .unauthorized:
            return "Please log in to continue"
        case .forbidden:
            return "You don't have permission to access this resource"
        case .notFound:
            return "Resource not found"
        case .validationError(let details):
            if let first = details.first {
                return first.msg
            }
            return "Validation error"
        case .serverError(let code):
            return "Server error (\(code)). Please try again later."
        case .httpError(let code, _):
            return "Request failed with status \(code)"
        case .decodingError(let error):
            return "Failed to process response: \(error.localizedDescription)"
        case .networkError(let error):
            return "Network error: \(error.localizedDescription)"
        case .unknown:
            return "An unknown error occurred"
        }
    }
}

// MARK: - Validation Error Response

struct ValidationErrorResponse: Codable {
    let detail: [ValidationErrorDetail]
}

struct ValidationErrorDetail: Codable {
    let loc: [String]
    let msg: String
    let type: String
}
