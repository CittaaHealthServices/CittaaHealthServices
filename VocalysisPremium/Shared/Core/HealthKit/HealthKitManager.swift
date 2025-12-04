import Foundation
import HealthKit
import Combine

// MARK: - HealthKit Manager

/// Manages HealthKit integration for mental health tracking
@MainActor
final class HealthKitManager: ObservableObject {
    
    // MARK: - Published Properties
    
    @Published private(set) var isAuthorized = false
    @Published private(set) var authorizationStatus: HKAuthorizationStatus = .notDetermined
    @Published var error: HealthKitError?
    
    // Latest health data
    @Published private(set) var latestHeartRate: Double?
    @Published private(set) var latestHRV: Double?
    @Published private(set) var latestSleepDuration: TimeInterval?
    @Published private(set) var latestStepCount: Int?
    @Published private(set) var latestMindfulMinutes: TimeInterval?
    
    // MARK: - Properties
    
    static let shared = HealthKitManager()
    
    private let healthStore = HKHealthStore()
    
    /// Check if HealthKit is available on this device
    var isHealthKitAvailable: Bool {
        HKHealthStore.isHealthDataAvailable()
    }
    
    // MARK: - Health Data Types
    
    /// Types we want to read from HealthKit
    private var readTypes: Set<HKObjectType> {
        var types = Set<HKObjectType>()
        
        // Quantity types
        if let heartRate = HKQuantityType.quantityType(forIdentifier: .heartRate) {
            types.insert(heartRate)
        }
        if let hrv = HKQuantityType.quantityType(forIdentifier: .heartRateVariabilitySDNN) {
            types.insert(hrv)
        }
        if let restingHR = HKQuantityType.quantityType(forIdentifier: .restingHeartRate) {
            types.insert(restingHR)
        }
        if let steps = HKQuantityType.quantityType(forIdentifier: .stepCount) {
            types.insert(steps)
        }
        if let activeEnergy = HKQuantityType.quantityType(forIdentifier: .activeEnergyBurned) {
            types.insert(activeEnergy)
        }
        
        // Category types
        if let sleep = HKCategoryType.categoryType(forIdentifier: .sleepAnalysis) {
            types.insert(sleep)
        }
        if let mindful = HKCategoryType.categoryType(forIdentifier: .mindfulSession) {
            types.insert(mindful)
        }
        
        // Workout type
        types.insert(HKWorkoutType.workoutType())
        
        return types
    }
    
    /// Types we want to write to HealthKit
    private var writeTypes: Set<HKSampleType> {
        var types = Set<HKSampleType>()
        
        // Mindful session for mental health tracking
        if let mindful = HKCategoryType.categoryType(forIdentifier: .mindfulSession) {
            types.insert(mindful)
        }
        
        // Heart rate during analysis
        if let heartRate = HKQuantityType.quantityType(forIdentifier: .heartRate) {
            types.insert(heartRate)
        }
        
        return types
    }
    
    // MARK: - Authorization
    
    /// Request HealthKit authorization
    func requestAuthorization() async throws {
        guard isHealthKitAvailable else {
            throw HealthKitError.notAvailable
        }
        
        do {
            try await healthStore.requestAuthorization(toShare: writeTypes, read: readTypes)
            await updateAuthorizationStatus()
        } catch {
            throw HealthKitError.authorizationFailed(error.localizedDescription)
        }
    }
    
    /// Update authorization status
    private func updateAuthorizationStatus() async {
        guard let heartRateType = HKQuantityType.quantityType(forIdentifier: .heartRate) else {
            return
        }
        
        authorizationStatus = healthStore.authorizationStatus(for: heartRateType)
        isAuthorized = authorizationStatus == .sharingAuthorized
    }
    
    // MARK: - Reading Health Data
    
    /// Fetch latest heart rate
    func fetchLatestHeartRate() async throws -> Double? {
        guard let heartRateType = HKQuantityType.quantityType(forIdentifier: .heartRate) else {
            throw HealthKitError.typeNotAvailable
        }
        
        let sample = try await fetchLatestSample(for: heartRateType)
        
        guard let quantitySample = sample as? HKQuantitySample else {
            return nil
        }
        
        let heartRate = quantitySample.quantity.doubleValue(for: HKUnit.count().unitDivided(by: .minute()))
        latestHeartRate = heartRate
        return heartRate
    }
    
    /// Fetch latest HRV
    func fetchLatestHRV() async throws -> Double? {
        guard let hrvType = HKQuantityType.quantityType(forIdentifier: .heartRateVariabilitySDNN) else {
            throw HealthKitError.typeNotAvailable
        }
        
        let sample = try await fetchLatestSample(for: hrvType)
        
        guard let quantitySample = sample as? HKQuantitySample else {
            return nil
        }
        
        let hrv = quantitySample.quantity.doubleValue(for: HKUnit.secondUnit(with: .milli))
        latestHRV = hrv
        return hrv
    }
    
    /// Fetch sleep data for the past night
    func fetchSleepData(for date: Date = Date()) async throws -> SleepData? {
        guard let sleepType = HKCategoryType.categoryType(forIdentifier: .sleepAnalysis) else {
            throw HealthKitError.typeNotAvailable
        }
        
        // Get sleep data from the previous night
        let calendar = Calendar.current
        let endOfDay = calendar.startOfDay(for: date)
        let startOfPreviousDay = calendar.date(byAdding: .day, value: -1, to: endOfDay)!
        
        let predicate = HKQuery.predicateForSamples(
            withStart: startOfPreviousDay,
            end: date,
            options: .strictStartDate
        )
        
        let samples = try await fetchSamples(for: sleepType, predicate: predicate)
        
        guard !samples.isEmpty else {
            return nil
        }
        
        // Calculate total sleep duration
        var totalSleep: TimeInterval = 0
        var sleepStart: Date?
        var sleepEnd: Date?
        
        for sample in samples {
            guard let categorySample = sample as? HKCategorySample else { continue }
            
            // Only count asleep states (not in bed)
            let sleepValue = HKCategoryValueSleepAnalysis(rawValue: categorySample.value)
            if sleepValue == .asleepCore || sleepValue == .asleepDeep || sleepValue == .asleepREM || sleepValue == .asleepUnspecified {
                totalSleep += categorySample.endDate.timeIntervalSince(categorySample.startDate)
                
                if sleepStart == nil || categorySample.startDate < sleepStart! {
                    sleepStart = categorySample.startDate
                }
                if sleepEnd == nil || categorySample.endDate > sleepEnd! {
                    sleepEnd = categorySample.endDate
                }
            }
        }
        
        latestSleepDuration = totalSleep
        
        return SleepData(
            duration: totalSleep,
            startTime: sleepStart,
            endTime: sleepEnd,
            quality: calculateSleepQuality(duration: totalSleep)
        )
    }
    
    /// Fetch step count for today
    func fetchStepCount(for date: Date = Date()) async throws -> Int? {
        guard let stepType = HKQuantityType.quantityType(forIdentifier: .stepCount) else {
            throw HealthKitError.typeNotAvailable
        }
        
        let calendar = Calendar.current
        let startOfDay = calendar.startOfDay(for: date)
        let endOfDay = calendar.date(byAdding: .day, value: 1, to: startOfDay)!
        
        let predicate = HKQuery.predicateForSamples(
            withStart: startOfDay,
            end: endOfDay,
            options: .strictStartDate
        )
        
        let statistics = try await fetchStatistics(for: stepType, predicate: predicate, options: .cumulativeSum)
        
        guard let sum = statistics.sumQuantity() else {
            return nil
        }
        
        let steps = Int(sum.doubleValue(for: .count()))
        latestStepCount = steps
        return steps
    }
    
    /// Fetch mindful minutes for today
    func fetchMindfulMinutes(for date: Date = Date()) async throws -> TimeInterval? {
        guard let mindfulType = HKCategoryType.categoryType(forIdentifier: .mindfulSession) else {
            throw HealthKitError.typeNotAvailable
        }
        
        let calendar = Calendar.current
        let startOfDay = calendar.startOfDay(for: date)
        let endOfDay = calendar.date(byAdding: .day, value: 1, to: startOfDay)!
        
        let predicate = HKQuery.predicateForSamples(
            withStart: startOfDay,
            end: endOfDay,
            options: .strictStartDate
        )
        
        let samples = try await fetchSamples(for: mindfulType, predicate: predicate)
        
        var totalMinutes: TimeInterval = 0
        for sample in samples {
            totalMinutes += sample.endDate.timeIntervalSince(sample.startDate)
        }
        
        latestMindfulMinutes = totalMinutes
        return totalMinutes
    }
    
    /// Fetch all health data for correlation
    func fetchHealthCorrelationData(for date: Date = Date()) async throws -> HealthCorrelationData {
        async let heartRate = fetchLatestHeartRate()
        async let hrv = fetchLatestHRV()
        async let sleep = fetchSleepData(for: date)
        async let steps = fetchStepCount(for: date)
        async let mindful = fetchMindfulMinutes(for: date)
        
        return try await HealthCorrelationData(
            date: date,
            heartRate: heartRate,
            hrv: hrv,
            sleepData: sleep,
            stepCount: steps,
            mindfulMinutes: mindful
        )
    }
    
    // MARK: - Writing Health Data
    
    /// Save a mindful session
    func saveMindfulSession(start: Date, end: Date) async throws {
        guard let mindfulType = HKCategoryType.categoryType(forIdentifier: .mindfulSession) else {
            throw HealthKitError.typeNotAvailable
        }
        
        let sample = HKCategorySample(
            type: mindfulType,
            value: HKCategoryValue.notApplicable.rawValue,
            start: start,
            end: end
        )
        
        try await healthStore.save(sample)
    }
    
    /// Save heart rate during voice analysis
    func saveHeartRate(_ bpm: Double, at date: Date = Date()) async throws {
        guard let heartRateType = HKQuantityType.quantityType(forIdentifier: .heartRate) else {
            throw HealthKitError.typeNotAvailable
        }
        
        let quantity = HKQuantity(unit: HKUnit.count().unitDivided(by: .minute()), doubleValue: bpm)
        let sample = HKQuantitySample(type: heartRateType, quantity: quantity, start: date, end: date)
        
        try await healthStore.save(sample)
    }
    
    // MARK: - Private Helpers
    
    private func fetchLatestSample(for type: HKSampleType) async throws -> HKSample? {
        let sortDescriptor = NSSortDescriptor(key: HKSampleSortIdentifierStartDate, ascending: false)
        
        return try await withCheckedThrowingContinuation { continuation in
            let query = HKSampleQuery(
                sampleType: type,
                predicate: nil,
                limit: 1,
                sortDescriptors: [sortDescriptor]
            ) { _, samples, error in
                if let error = error {
                    continuation.resume(throwing: HealthKitError.queryFailed(error.localizedDescription))
                } else {
                    continuation.resume(returning: samples?.first)
                }
            }
            
            healthStore.execute(query)
        }
    }
    
    private func fetchSamples(for type: HKSampleType, predicate: NSPredicate?) async throws -> [HKSample] {
        let sortDescriptor = NSSortDescriptor(key: HKSampleSortIdentifierStartDate, ascending: true)
        
        return try await withCheckedThrowingContinuation { continuation in
            let query = HKSampleQuery(
                sampleType: type,
                predicate: predicate,
                limit: HKObjectQueryNoLimit,
                sortDescriptors: [sortDescriptor]
            ) { _, samples, error in
                if let error = error {
                    continuation.resume(throwing: HealthKitError.queryFailed(error.localizedDescription))
                } else {
                    continuation.resume(returning: samples ?? [])
                }
            }
            
            healthStore.execute(query)
        }
    }
    
    private func fetchStatistics(
        for type: HKQuantityType,
        predicate: NSPredicate?,
        options: HKStatisticsOptions
    ) async throws -> HKStatistics {
        return try await withCheckedThrowingContinuation { continuation in
            let query = HKStatisticsQuery(
                quantityType: type,
                quantitySamplePredicate: predicate,
                options: options
            ) { _, statistics, error in
                if let error = error {
                    continuation.resume(throwing: HealthKitError.queryFailed(error.localizedDescription))
                } else if let statistics = statistics {
                    continuation.resume(returning: statistics)
                } else {
                    continuation.resume(throwing: HealthKitError.noData)
                }
            }
            
            healthStore.execute(query)
        }
    }
    
    private func calculateSleepQuality(duration: TimeInterval) -> SleepQuality {
        let hours = duration / 3600
        switch hours {
        case 7...: return .excellent
        case 6..<7: return .good
        case 5..<6: return .fair
        default: return .poor
        }
    }
}

// MARK: - Supporting Types

struct SleepData {
    let duration: TimeInterval
    let startTime: Date?
    let endTime: Date?
    let quality: SleepQuality
    
    var durationHours: Double {
        duration / 3600
    }
    
    var formattedDuration: String {
        let hours = Int(duration / 3600)
        let minutes = Int((duration.truncatingRemainder(dividingBy: 3600)) / 60)
        return "\(hours)h \(minutes)m"
    }
}

struct HealthCorrelationData {
    let date: Date
    let heartRate: Double?
    let hrv: Double?
    let sleepData: SleepData?
    let stepCount: Int?
    let mindfulMinutes: TimeInterval?
    
    var formattedMindfulMinutes: String {
        guard let minutes = mindfulMinutes else { return "0m" }
        let mins = Int(minutes / 60)
        return "\(mins)m"
    }
}

// MARK: - HealthKit Errors

enum HealthKitError: Error, LocalizedError, Identifiable {
    case notAvailable
    case authorizationFailed(String)
    case typeNotAvailable
    case queryFailed(String)
    case saveFailed(String)
    case noData
    
    var id: String { localizedDescription }
    
    var errorDescription: String? {
        switch self {
        case .notAvailable:
            return "HealthKit is not available on this device"
        case .authorizationFailed(let reason):
            return "Failed to authorize HealthKit: \(reason)"
        case .typeNotAvailable:
            return "Health data type not available"
        case .queryFailed(let reason):
            return "Failed to fetch health data: \(reason)"
        case .saveFailed(let reason):
            return "Failed to save health data: \(reason)"
        case .noData:
            return "No health data available"
        }
    }
}
