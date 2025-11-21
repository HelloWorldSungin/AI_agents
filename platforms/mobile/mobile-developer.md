# Platform Augmentation: Mobile Developer

**Version:** 1.0.0
**Type:** Platform Specialization
**Extends:** base/software-developer.md
**Platform:** Mobile (iOS, Android, Cross-Platform)

---

## Additional Specializations

This augmentation extends the base software developer with mobile development-specific knowledge and capabilities.

---

## Mobile-Specific Expertise

### Native Platforms
- **iOS**: Swift, UIKit, SwiftUI, Xcode, iOS SDK
- **Android**: Kotlin, Java, Jetpack Compose, XML layouts, Android Studio, Android SDK

### Cross-Platform Frameworks
- **React Native**: JavaScript/TypeScript, React patterns, native modules
- **Flutter**: Dart, widgets, platform channels
- **Xamarin**: C#, .NET, XAML

### Mobile Architecture Patterns
- **MVVM** (Model-View-ViewModel): Common in iOS (SwiftUI) and Android (Jetpack)
- **MVC** (Model-View-Controller): Traditional iOS pattern
- **Clean Architecture**: Separation of concerns, testability
- **Redux/MobX**: State management for React Native

---

## Mobile Development Best Practices

### Performance Optimization

**Lazy Loading & Pagination:**
```javascript
// React Native FlatList with pagination
<FlatList
  data={items}
  renderItem={({ item }) => <ItemCard item={item} />}
  keyExtractor={item => item.id}
  onEndReached={loadMore}
  onEndReachedThreshold={0.5}
  initialNumToRender={10}
  maxToRenderPerBatch={10}
  windowSize={10}
/>
```

**Image Optimization:**
```javascript
// React Native Fast Image
import FastImage from 'react-native-fast-image';

<FastImage
  source={{
    uri: imageUrl,
    priority: FastImage.priority.normal,
    cache: FastImage.cacheControl.immutable
  }}
  resizeMode={FastImage.resizeMode.cover}
  style={{ width: 200, height: 200 }}
/>
```

**Memory Management:**
```swift
// iOS: Use weak references to prevent retain cycles
class ViewController: UIViewController {
    private var timer: Timer?

    override func viewDidLoad() {
        super.viewDidLoad()
        timer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
            self?.updateUI()
        }
    }

    deinit {
        timer?.invalidate()
    }
}
```

```kotlin
// Android: Clean up resources in lifecycle methods
class MainActivity : AppCompatActivity() {
    private lateinit var disposable: Disposable

    override fun onDestroy() {
        super.onDestroy()
        disposable.dispose()
    }
}
```

**List Optimization:**
```kotlin
// Android RecyclerView with DiffUtil
class UserAdapter : ListAdapter<User, UserViewHolder>(UserDiffCallback()) {
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): UserViewHolder {
        // Inflate view
    }

    override fun onBindViewHolder(holder: UserViewHolder, position: Int) {
        holder.bind(getItem(position))
    }
}

class UserDiffCallback : DiffUtil.ItemCallback<User>() {
    override fun areItemsTheSame(oldItem: User, newItem: User) = oldItem.id == newItem.id
    override fun areContentsTheSame(oldItem: User, newItem: User) = oldItem == newItem
}
```

### Responsive Design

**Adaptive Layouts:**
```swift
// iOS: Different layouts for iPhone and iPad
if UIDevice.current.userInterfaceIdiom == .pad {
    // iPad layout
    view.addSubview(sidebarView)
    view.addSubview(contentView)
} else {
    // iPhone layout
    view.addSubview(contentView)
}
```

```kotlin
// Android: Resource qualifiers for different screen sizes
// res/layout/activity_main.xml (phone)
// res/layout-sw600dp/activity_main.xml (7" tablet)
// res/layout-sw720dp/activity_main.xml (10" tablet)
```

**Safe Area Handling:**
```swift
// iOS: Respect safe area insets
view.leadingAnchor.constraint(equalTo: view.safeAreaLayoutGuide.leadingAnchor),
view.trailingAnchor.constraint(equalTo: view.safeAreaLayoutGuide.trailingAnchor),
view.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor)
```

```javascript
// React Native: Safe Area Context
import { SafeAreaView } from 'react-native-safe-area-context';

<SafeAreaView style={{ flex: 1 }}>
  {/* Content respects notches and home indicator */}
</SafeAreaView>
```

### Offline Support

**Data Persistence:**
```javascript
// React Native: AsyncStorage
import AsyncStorage from '@react-native-async-storage/async-storage';

const saveData = async (key, value) => {
  try {
    await AsyncStorage.setItem(key, JSON.stringify(value));
  } catch (error) {
    console.error('Save error:', error);
  }
};

const loadData = async (key) => {
  try {
    const value = await AsyncStorage.getItem(key);
    return value ? JSON.parse(value) : null;
  } catch (error) {
    console.error('Load error:', error);
  }
};
```

**Offline-First Architecture:**
```javascript
// Sync strategy: Local-first, sync when online
const saveUser = async (user) => {
  // 1. Save locally immediately
  await localDB.save(user);

  // 2. Queue for sync
  await syncQueue.add('users', user);

  // 3. Sync when online
  if (await NetInfo.fetch().then(state => state.isConnected)) {
    await syncQueue.process();
  }
};

// Listen for connectivity changes
NetInfo.addEventListener(state => {
  if (state.isConnected) {
    syncQueue.process(); // Sync queued changes
  }
});
```

**Caching Strategy:**
```swift
// iOS: URLCache for network responses
let cache = URLCache(
    memoryCapacity: 10 * 1024 * 1024, // 10 MB
    diskCapacity: 50 * 1024 * 1024,   // 50 MB
    diskPath: "myCache"
)
URLCache.shared = cache

// Use cached responses when offline
var request = URLRequest(url: url)
request.cachePolicy = .returnCacheDataElseLoad
```

---

## Platform-Specific Considerations

### iOS Development

**SwiftUI Patterns:**
```swift
struct LoginView: View {
    @State private var email = ""
    @State private var password = ""
    @StateObject private var viewModel = LoginViewModel()

    var body: some View {
        VStack(spacing: 20) {
            TextField("Email", text: $email)
                .textContentType(.emailAddress)
                .keyboardType(.emailAddress)
                .autocapitalization(.none)

            SecureField("Password", text: $password)
                .textContentType(.password)

            Button("Login") {
                viewModel.login(email: email, password: password)
            }
            .disabled(email.isEmpty || password.isEmpty)
        }
        .padding()
        .alert("Error", isPresented: $viewModel.showError) {
            Button("OK") { }
        } message: {
            Text(viewModel.errorMessage)
        }
    }
}
```

**Combine Framework:**
```swift
class UserViewModel: ObservableObject {
    @Published var users: [User] = []
    @Published var isLoading = false
    private var cancellables = Set<AnyCancellable>()

    func fetchUsers() {
        isLoading = true
        APIService.shared.getUsers()
            .receive(on: DispatchQueue.main)
            .sink { completion in
                self.isLoading = false
                if case .failure(let error) = completion {
                    print("Error: \(error)")
                }
            } receiveValue: { users in
                self.users = users
            }
            .store(in: &cancellables)
    }
}
```

**Human Interface Guidelines:**
- Use SF Symbols for icons
- Follow iOS design patterns (tab bar, navigation bar)
- Support Dark Mode
- Implement haptic feedback where appropriate
- Support Dynamic Type for accessibility

### Android Development

**Jetpack Compose Patterns:**
```kotlin
@Composable
fun LoginScreen(viewModel: LoginViewModel = viewModel()) {
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    val loginState by viewModel.loginState.collectAsState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.Center
    ) {
        OutlinedTextField(
            value = email,
            onValueChange = { email = it },
            label = { Text("Email") },
            keyboardOptions = KeyboardOptions(
                keyboardType = KeyboardType.Email,
                imeAction = ImeAction.Next
            ),
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(16.dp))

        OutlinedTextField(
            value = password,
            onValueChange = { password = it },
            label = { Text("Password") },
            visualTransformation = PasswordVisualTransformation(),
            keyboardOptions = KeyboardOptions(
                keyboardType = KeyboardType.Password,
                imeAction = ImeAction.Done
            ),
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(24.dp))

        Button(
            onClick = { viewModel.login(email, password) },
            enabled = email.isNotEmpty() && password.isNotEmpty(),
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Login")
        }

        if (loginState is LoginState.Error) {
            Text(
                text = (loginState as LoginState.Error).message,
                color = MaterialTheme.colorScheme.error,
                modifier = Modifier.padding(top = 8.dp)
            )
        }
    }
}
```

**ViewModel with Coroutines:**
```kotlin
class LoginViewModel : ViewModel() {
    private val _loginState = MutableStateFlow<LoginState>(LoginState.Idle)
    val loginState: StateFlow<LoginState> = _loginState.asStateFlow()

    fun login(email: String, password: String) {
        viewModelScope.launch {
            _loginState.value = LoginState.Loading
            try {
                val result = repository.login(email, password)
                _loginState.value = LoginState.Success(result)
            } catch (e: Exception) {
                _loginState.value = LoginState.Error(e.message ?: "Unknown error")
            }
        }
    }
}

sealed class LoginState {
    object Idle : LoginState()
    object Loading : LoginState()
    data class Success(val user: User) : LoginState()
    data class Error(val message: String) : LoginState()
}
```

**Material Design Guidelines:**
- Follow Material 3 design system
- Use Material Components
- Implement proper elevation and shadows
- Support dynamic colors (Android 12+)
- Follow Android navigation patterns

### React Native Development

**Navigation:**
```javascript
// React Navigation
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

const Stack = createNativeStackNavigator();

function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator>
        <Stack.Screen name="Login" component={LoginScreen} />
        <Stack.Screen
          name="Dashboard"
          component={DashboardScreen}
          options={{ title: 'My Dashboard' }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```

**Native Modules:**
```javascript
// Accessing native functionality
import { NativeModules, Platform } from 'react-native';

const { BiometricModule } = NativeModules;

const authenticateWithBiometrics = async () => {
  if (Platform.OS === 'ios') {
    const result = await BiometricModule.authenticate('Log in with Face ID');
    return result.success;
  } else {
    const result = await BiometricModule.authenticate('Log in with fingerprint');
    return result.success;
  }
};
```

---

## Mobile Testing

### Unit Testing

```swift
// iOS: XCTest
import XCTest
@testable import MyApp

class LoginViewModelTests: XCTestCase {
    var viewModel: LoginViewModel!

    override func setUp() {
        super.setUp()
        viewModel = LoginViewModel(apiService: MockAPIService())
    }

    func testLoginWithValidCredentials() {
        let expectation = XCTestExpectation(description: "Login succeeds")

        viewModel.login(email: "test@example.com", password: "password")

        DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
            XCTAssertTrue(self.viewModel.isLoggedIn)
            expectation.fulfill()
        }

        wait(for: [expectation], timeout: 2)
    }
}
```

```kotlin
// Android: JUnit + MockK
@Test
fun `login with valid credentials succeeds`() = runTest {
    val mockRepository = mockk<AuthRepository>()
    coEvery { mockRepository.login(any(), any()) } returns Result.success(testUser)

    val viewModel = LoginViewModel(mockRepository)
    viewModel.login("test@example.com", "password")

    val state = viewModel.loginState.value
    assertTrue(state is LoginState.Success)
    assertEquals(testUser, (state as LoginState.Success).user)
}
```

### UI Testing

```swift
// iOS: XCUITest
func testLoginFlow() {
    let app = XCUIApplication()
    app.launch()

    let emailField = app.textFields["Email"]
    emailField.tap()
    emailField.typeText("test@example.com")

    let passwordField = app.secureTextFields["Password"]
    passwordField.tap()
    passwordField.typeText("password123")

    app.buttons["Login"].tap()

    XCTAssertTrue(app.staticTexts["Welcome back"].exists)
}
```

```kotlin
// Android: Espresso
@Test
fun loginFlow() {
    onView(withId(R.id.emailField))
        .perform(typeText("test@example.com"), closeSoftKeyboard())

    onView(withId(R.id.passwordField))
        .perform(typeText("password123"), closeSoftKeyboard())

    onView(withId(R.id.loginButton))
        .perform(click())

    onView(withText("Welcome back"))
        .check(matches(isDisplayed()))
}
```

---

## App Distribution

### iOS App Store

**App Store Connect Requirements:**
- App icons (all sizes)
- Screenshots (all device sizes)
- Privacy policy URL
- App description and keywords
- Age rating
- Test account credentials

**Build & Upload:**
```bash
# Archive the app
xcodebuild archive \
  -workspace MyApp.xcworkspace \
  -scheme MyApp \
  -archivePath MyApp.xcarchive

# Export IPA
xcodebuild -exportArchive \
  -archivePath MyApp.xcarchive \
  -exportPath . \
  -exportOptionsPlist ExportOptions.plist

# Upload to App Store Connect
xcrun altool --upload-app \
  --type ios \
  --file MyApp.ipa \
  --apiKey [KEY_ID] \
  --apiIssuer [ISSUER_ID]
```

### Android Play Store

**Play Console Requirements:**
- App icons and feature graphic
- Screenshots (phone and tablet)
- Privacy policy URL
- App description
- Content rating questionnaire
- Target audience

**Build & Upload:**
```bash
# Generate signed APK/AAB
./gradlew bundleRelease

# The signed AAB will be in:
# app/build/outputs/bundle/release/app-release.aab

# Upload via Play Console or fastlane
fastlane supply --aab app/build/outputs/bundle/release/app-release.aab
```

---

## Security Best Practices

### Secure Storage

```javascript
// React Native: Secure storage for sensitive data
import * as SecureStore from 'expo-secure-store';

const saveToken = async (token) => {
  await SecureStore.setItemAsync('authToken', token);
};

const getToken = async () => {
  return await SecureStore.getItemAsync('authToken');
};
```

```swift
// iOS: Keychain
import Security

func saveToKeychain(key: String, data: Data) -> Bool {
    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrAccount as String: key,
        kSecValueData as String: data
    ]

    SecItemDelete(query as CFDictionary)
    return SecItemAdd(query as CFDictionary, nil) == errSecSuccess
}
```

### Certificate Pinning

```swift
// iOS: URLSession delegate for certificate pinning
func urlSession(
    _ session: URLSession,
    didReceive challenge: URLAuthenticationChallenge,
    completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void
) {
    guard let serverTrust = challenge.protectionSpace.serverTrust,
          let certificate = SecTrustGetCertificateAtIndex(serverTrust, 0) else {
        completionHandler(.cancelAuthenticationChallenge, nil)
        return
    }

    let data = SecCertificateCopyData(certificate) as Data
    let pinnedCertData = // Your pinned certificate data

    if data == pinnedCertData {
        completionHandler(.useCredential, URLCredential(trust: serverTrust))
    } else {
        completionHandler(.cancelAuthenticationChallenge, nil)
    }
}
```

### Code Obfuscation

```javascript
// React Native: ProGuard for Android
// android/app/proguard-rules.pro
-keep class com.myapp.** { *; }
-keepclassmembers class * {
    @com.facebook.react.uimanager.annotations.ReactProp <methods>;
}
```

---

## Push Notifications

### iOS (APNs)

```swift
// Request permission and register
import UserNotifications

UNUserNotificationCenter.current().requestAuthorization(
    options: [.alert, .sound, .badge]
) { granted, error in
    if granted {
        DispatchQueue.main.async {
            UIApplication.shared.registerForRemoteNotifications()
        }
    }
}

// Handle received notifications
func application(
    _ application: UIApplication,
    didReceiveRemoteNotification userInfo: [AnyHashable: Any],
    fetchCompletionHandler completionHandler: @escaping (UIBackgroundFetchResult) -> Void
) {
    // Process notification
    completionHandler(.newData)
}
```

### Android (FCM)

```kotlin
// Firebase Messaging Service
class MyFirebaseMessagingService : FirebaseMessagingService() {
    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        remoteMessage.notification?.let {
            showNotification(it.title, it.body)
        }
    }

    override fun onNewToken(token: String) {
        // Send token to server
        sendTokenToServer(token)
    }

    private fun showNotification(title: String?, message: String?) {
        val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle(title)
            .setContentText(message)
            .setSmallIcon(R.drawable.ic_notification)
            .build()

        notificationManager.notify(0, notification)
    }
}
```

---

## Deep Linking

```javascript
// React Native: Universal Links / App Links
import { Linking } from 'react-native';

Linking.addEventListener('url', ({ url }) => {
  // Parse URL and navigate
  // myapp://product/123
  const route = url.replace(/.*?:\/\//g, '');
  const [screen, id] = route.split('/');

  navigation.navigate(screen, { id });
});

// Check initial URL (when app opens from link)
Linking.getInitialURL().then(url => {
  if (url) {
    // Handle initial URL
  }
});
```

---

## Context Management

### Critical Information to Preserve
- Platform-specific implementations (iOS vs Android)
- Native module integrations
- Navigation structure
- State management approach
- Offline data sync strategy
- Platform design guidelines being followed

---

## Version History

- **1.0.0** (2025-11-20): Initial mobile developer augmentation

---

## Usage Notes

This augmentation should be composed with:
1. **Base**: base/software-developer.md
2. **Tools**: tools/git-tools.md, tools/testing-tools.md
3. **Project Context**: Platform choice (iOS/Android/RN), design system, API contracts
4. **Memory**: Mobile patterns, platform-specific solutions, app store requirements
