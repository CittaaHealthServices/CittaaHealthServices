import SwiftUI

// MARK: - Login View

struct LoginView: View {
    
    // MARK: - State
    
    @EnvironmentObject var authManager: AuthManager
    
    @State private var email = ""
    @State private var password = ""
    @State private var showPassword = false
    @State private var showRegistration = false
    @State private var showForgotPassword = false
    @State private var isLoading = false
    
    // MARK: - Body
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 32) {
                    // Logo and Header
                    headerSection
                    
                    // Login Form
                    loginForm
                    
                    // Biometric Login
                    if KeychainManager.shared.isBiometricAvailable {
                        biometricButton
                    }
                    
                    // Divider
                    dividerSection
                    
                    // Register Link
                    registerSection
                }
                .padding(.horizontal, 24)
                .padding(.vertical, 40)
            }
            .background(CittaaColors.background.ignoresSafeArea())
            .navigationBarHidden(true)
            .sheet(isPresented: $showRegistration) {
                RegistrationView()
            }
            .sheet(isPresented: $showForgotPassword) {
                ForgotPasswordView()
            }
            .alert(item: $authManager.error) { error in
                Alert(
                    title: Text("Login Failed"),
                    message: Text(error.localizedDescription),
                    dismissButton: .default(Text("OK"))
                )
            }
        }
    }
    
    // MARK: - Header Section
    
    private var headerSection: some View {
        VStack(spacing: 16) {
            // Logo
            Image(systemName: "waveform.circle.fill")
                .resizable()
                .aspectRatio(contentMode: .fit)
                .frame(width: 80, height: 80)
                .foregroundColor(CittaaColors.primary)
            
            // App Name
            Text("Vocalysis")
                .font(.system(size: 32, weight: .bold))
                .foregroundColor(CittaaColors.textPrimary)
            
            // Tagline
            Text("Voice-Based Mental Health Screening")
                .font(.subheadline)
                .foregroundColor(CittaaColors.textSecondary)
                .multilineTextAlignment(.center)
            
            // Company
            Text("by CITTAA Health Services")
                .font(.caption)
                .foregroundColor(CittaaColors.textSecondary)
        }
    }
    
    // MARK: - Login Form
    
    private var loginForm: some View {
        VStack(spacing: 20) {
            // Email Field
            VStack(alignment: .leading, spacing: 8) {
                Text("Email")
                    .font(.subheadline)
                    .fontWeight(.medium)
                    .foregroundColor(CittaaColors.textPrimary)
                
                TextField("Enter your email", text: $email)
                    .textFieldStyle(CittaaTextFieldStyle())
                    .textContentType(.emailAddress)
                    .keyboardType(.emailAddress)
                    .autocapitalization(.none)
                    .disableAutocorrection(true)
            }
            
            // Password Field
            VStack(alignment: .leading, spacing: 8) {
                Text("Password")
                    .font(.subheadline)
                    .fontWeight(.medium)
                    .foregroundColor(CittaaColors.textPrimary)
                
                HStack {
                    if showPassword {
                        TextField("Enter your password", text: $password)
                    } else {
                        SecureField("Enter your password", text: $password)
                    }
                    
                    Button(action: { showPassword.toggle() }) {
                        Image(systemName: showPassword ? "eye.slash.fill" : "eye.fill")
                            .foregroundColor(CittaaColors.textSecondary)
                    }
                }
                .textFieldStyle(CittaaTextFieldStyle())
                .textContentType(.password)
            }
            
            // Forgot Password
            HStack {
                Spacer()
                Button("Forgot Password?") {
                    showForgotPassword = true
                }
                .font(.subheadline)
                .foregroundColor(CittaaColors.primary)
            }
            
            // Login Button
            Button(action: login) {
                HStack {
                    if authManager.isLoading {
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle(tint: .white))
                    } else {
                        Text("Sign In")
                            .fontWeight(.semibold)
                    }
                }
                .frame(maxWidth: .infinity)
                .frame(height: 50)
                .background(CittaaColors.primary)
                .foregroundColor(.white)
                .cornerRadius(12)
            }
            .disabled(authManager.isLoading || !isValidInput)
            .opacity(isValidInput ? 1 : 0.6)
        }
    }
    
    // MARK: - Biometric Button
    
    private var biometricButton: some View {
        Button(action: loginWithBiometrics) {
            HStack {
                Image(systemName: KeychainManager.shared.biometricType.iconName)
                Text("Sign in with \(KeychainManager.shared.biometricType.displayName)")
            }
            .frame(maxWidth: .infinity)
            .frame(height: 50)
            .background(Color.clear)
            .foregroundColor(CittaaColors.primary)
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(CittaaColors.primary, lineWidth: 2)
            )
        }
    }
    
    // MARK: - Divider Section
    
    private var dividerSection: some View {
        HStack {
            Rectangle()
                .fill(CittaaColors.textSecondary.opacity(0.3))
                .frame(height: 1)
            
            Text("OR")
                .font(.caption)
                .foregroundColor(CittaaColors.textSecondary)
                .padding(.horizontal, 16)
            
            Rectangle()
                .fill(CittaaColors.textSecondary.opacity(0.3))
                .frame(height: 1)
        }
    }
    
    // MARK: - Register Section
    
    private var registerSection: some View {
        VStack(spacing: 16) {
            Text("Don't have an account?")
                .font(.subheadline)
                .foregroundColor(CittaaColors.textSecondary)
            
            Button(action: { showRegistration = true }) {
                Text("Create Account")
                    .fontWeight(.semibold)
                    .frame(maxWidth: .infinity)
                    .frame(height: 50)
                    .background(CittaaColors.secondary)
                    .foregroundColor(.white)
                    .cornerRadius(12)
            }
        }
    }
    
    // MARK: - Validation
    
    private var isValidInput: Bool {
        !email.isEmpty && email.contains("@") && password.count >= 8
    }
    
    // MARK: - Actions
    
    private func login() {
        Task {
            do {
                try await authManager.login(email: email, password: password)
            } catch {
                // Error is handled by authManager
            }
        }
    }
    
    private func loginWithBiometrics() {
        Task {
            do {
                try await authManager.loginWithBiometrics()
            } catch {
                // Error is handled by authManager
            }
        }
    }
}

// MARK: - Custom Text Field Style

struct CittaaTextFieldStyle: TextFieldStyle {
    func _body(configuration: TextField<Self._Label>) -> some View {
        configuration
            .padding(.horizontal, 16)
            .padding(.vertical, 14)
            .background(Color.white)
            .cornerRadius(12)
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(CittaaColors.textSecondary.opacity(0.2), lineWidth: 1)
            )
    }
}

// MARK: - Registration View

struct RegistrationView: View {
    @Environment(\.dismiss) var dismiss
    @EnvironmentObject var authManager: AuthManager
    
    @State private var email = ""
    @State private var password = ""
    @State private var confirmPassword = ""
    @State private var fullName = ""
    @State private var phone = ""
    @State private var selectedLanguage: SupportedLanguage = .english
    @State private var showPassword = false
    @State private var agreedToTerms = false
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 24) {
                    // Header
                    VStack(spacing: 8) {
                        Text("Create Account")
                            .font(.title)
                            .fontWeight(.bold)
                        
                        Text("Join Vocalysis for personalized mental health insights")
                            .font(.subheadline)
                            .foregroundColor(CittaaColors.textSecondary)
                            .multilineTextAlignment(.center)
                    }
                    .padding(.top, 20)
                    
                    // Form Fields
                    VStack(spacing: 16) {
                        // Full Name
                        FormField(title: "Full Name", text: $fullName, placeholder: "Enter your full name")
                        
                        // Email
                        FormField(title: "Email", text: $email, placeholder: "Enter your email", keyboardType: .emailAddress)
                        
                        // Phone (Optional)
                        FormField(title: "Phone (Optional)", text: $phone, placeholder: "Enter your phone number", keyboardType: .phonePad)
                        
                        // Language
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Preferred Language")
                                .font(.subheadline)
                                .fontWeight(.medium)
                            
                            Picker("Language", selection: $selectedLanguage) {
                                ForEach(SupportedLanguage.allCases) { language in
                                    Text(language.displayName).tag(language)
                                }
                            }
                            .pickerStyle(MenuPickerStyle())
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding()
                            .background(Color.white)
                            .cornerRadius(12)
                            .overlay(
                                RoundedRectangle(cornerRadius: 12)
                                    .stroke(CittaaColors.textSecondary.opacity(0.2), lineWidth: 1)
                            )
                        }
                        
                        // Password
                        FormField(title: "Password", text: $password, placeholder: "Create a password (min 8 characters)", isSecure: true)
                        
                        // Confirm Password
                        FormField(title: "Confirm Password", text: $confirmPassword, placeholder: "Confirm your password", isSecure: true)
                        
                        // Password requirements
                        if !password.isEmpty {
                            PasswordRequirementsView(password: password)
                        }
                    }
                    
                    // Terms Agreement
                    Toggle(isOn: $agreedToTerms) {
                        Text("I agree to the Terms of Service and Privacy Policy")
                            .font(.caption)
                            .foregroundColor(CittaaColors.textSecondary)
                    }
                    .toggleStyle(CheckboxToggleStyle())
                    
                    // Register Button
                    Button(action: register) {
                        HStack {
                            if authManager.isLoading {
                                ProgressView()
                                    .progressViewStyle(CircularProgressViewStyle(tint: .white))
                            } else {
                                Text("Create Account")
                                    .fontWeight(.semibold)
                            }
                        }
                        .frame(maxWidth: .infinity)
                        .frame(height: 50)
                        .background(CittaaColors.primary)
                        .foregroundColor(.white)
                        .cornerRadius(12)
                    }
                    .disabled(!isValidInput || authManager.isLoading)
                    .opacity(isValidInput ? 1 : 0.6)
                }
                .padding(.horizontal, 24)
                .padding(.bottom, 40)
            }
            .background(CittaaColors.background.ignoresSafeArea())
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") {
                        dismiss()
                    }
                }
            }
            .alert(item: $authManager.error) { error in
                Alert(
                    title: Text("Registration Failed"),
                    message: Text(error.localizedDescription),
                    dismissButton: .default(Text("OK"))
                )
            }
        }
    }
    
    private var isValidInput: Bool {
        !email.isEmpty &&
        email.contains("@") &&
        password.count >= 8 &&
        password == confirmPassword &&
        agreedToTerms
    }
    
    private func register() {
        Task {
            do {
                try await authManager.register(
                    email: email,
                    password: password,
                    fullName: fullName.isEmpty ? nil : fullName,
                    phone: phone.isEmpty ? nil : phone,
                    language: selectedLanguage
                )
                dismiss()
            } catch {
                // Error handled by authManager
            }
        }
    }
}

// MARK: - Form Field Component

struct FormField: View {
    let title: String
    @Binding var text: String
    let placeholder: String
    var keyboardType: UIKeyboardType = .default
    var isSecure: Bool = false
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.subheadline)
                .fontWeight(.medium)
                .foregroundColor(CittaaColors.textPrimary)
            
            if isSecure {
                SecureField(placeholder, text: $text)
                    .textFieldStyle(CittaaTextFieldStyle())
            } else {
                TextField(placeholder, text: $text)
                    .textFieldStyle(CittaaTextFieldStyle())
                    .keyboardType(keyboardType)
                    .autocapitalization(keyboardType == .emailAddress ? .none : .words)
            }
        }
    }
}

// MARK: - Password Requirements View

struct PasswordRequirementsView: View {
    let password: String
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            RequirementRow(met: password.count >= 8, text: "At least 8 characters")
            RequirementRow(met: password.rangeOfCharacter(from: .uppercaseLetters) != nil, text: "One uppercase letter")
            RequirementRow(met: password.rangeOfCharacter(from: .lowercaseLetters) != nil, text: "One lowercase letter")
            RequirementRow(met: password.rangeOfCharacter(from: .decimalDigits) != nil, text: "One number")
        }
        .padding()
        .background(CittaaColors.surfaceLight)
        .cornerRadius(8)
    }
}

struct RequirementRow: View {
    let met: Bool
    let text: String
    
    var body: some View {
        HStack(spacing: 8) {
            Image(systemName: met ? "checkmark.circle.fill" : "circle")
                .foregroundColor(met ? CittaaColors.success : CittaaColors.textSecondary)
                .font(.caption)
            
            Text(text)
                .font(.caption)
                .foregroundColor(met ? CittaaColors.textPrimary : CittaaColors.textSecondary)
        }
    }
}

// MARK: - Checkbox Toggle Style

struct CheckboxToggleStyle: ToggleStyle {
    func makeBody(configuration: Configuration) -> some View {
        HStack(alignment: .top, spacing: 12) {
            Image(systemName: configuration.isOn ? "checkmark.square.fill" : "square")
                .foregroundColor(configuration.isOn ? CittaaColors.primary : CittaaColors.textSecondary)
                .onTapGesture {
                    configuration.isOn.toggle()
                }
            
            configuration.label
        }
    }
}

// MARK: - Forgot Password View

struct ForgotPasswordView: View {
    @Environment(\.dismiss) var dismiss
    @EnvironmentObject var authManager: AuthManager
    
    @State private var email = ""
    @State private var showSuccess = false
    
    var body: some View {
        NavigationView {
            VStack(spacing: 24) {
                // Header
                VStack(spacing: 8) {
                    Image(systemName: "lock.rotation")
                        .font(.system(size: 60))
                        .foregroundColor(CittaaColors.primary)
                    
                    Text("Reset Password")
                        .font(.title2)
                        .fontWeight(.bold)
                    
                    Text("Enter your email and we'll send you instructions to reset your password")
                        .font(.subheadline)
                        .foregroundColor(CittaaColors.textSecondary)
                        .multilineTextAlignment(.center)
                }
                .padding(.top, 40)
                
                // Email Field
                FormField(title: "Email", text: $email, placeholder: "Enter your email", keyboardType: .emailAddress)
                
                // Submit Button
                Button(action: resetPassword) {
                    HStack {
                        if authManager.isLoading {
                            ProgressView()
                                .progressViewStyle(CircularProgressViewStyle(tint: .white))
                        } else {
                            Text("Send Reset Link")
                                .fontWeight(.semibold)
                        }
                    }
                    .frame(maxWidth: .infinity)
                    .frame(height: 50)
                    .background(CittaaColors.primary)
                    .foregroundColor(.white)
                    .cornerRadius(12)
                }
                .disabled(email.isEmpty || !email.contains("@") || authManager.isLoading)
                
                Spacer()
            }
            .padding(.horizontal, 24)
            .background(CittaaColors.background.ignoresSafeArea())
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") {
                        dismiss()
                    }
                }
            }
            .alert("Check Your Email", isPresented: $showSuccess) {
                Button("OK") {
                    dismiss()
                }
            } message: {
                Text("If an account exists with this email, you'll receive password reset instructions.")
            }
        }
    }
    
    private func resetPassword() {
        Task {
            do {
                try await authManager.forgotPassword(email: email)
                showSuccess = true
            } catch {
                // Error handled by authManager
            }
        }
    }
}

// MARK: - Preview

#Preview {
    LoginView()
        .environmentObject(AuthManager.shared)
}
