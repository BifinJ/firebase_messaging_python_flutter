
# 🔔 Firebase Push Notification System (Python + Flutter)

This guide walks you through setting up push notifications using Firebase Cloud Messaging (FCM). It includes:

- Firebase Console Setup
- Firebase CLI Setup
- Flutter App Configuration
- Python Flask Backend Setup

---

## 📦 Prerequisites

- [Flutter SDK](https://docs.flutter.dev/get-started/install)
- Python 3.8+
- Firebase CLI
- A Firebase project with FCM enabled
- Android Studio / Emulator / Real device (for testing)

---

## ✅ 1. Firebase Console Setup

1. Go to [Firebase Console](https://console.firebase.google.com).
2. **Create a new project**.
3. Enable **Firebase Cloud Messaging**:
   - Go to **Project Settings > Cloud Messaging** tab.
   - No extra config is needed for testing push notifications.

4. **Register your Android app**:
   - In the Firebase Console, go to **Project Overview > Add App > Android**.
   - **Package name**: e.g., `com.example.fcmapp`
   - Download the `google-services.json` file and place it in your Flutter project under:

     ```
     android/app/google-services.json
     ```

5. Enable **APNs or FCM SDK** (if needed for production — optional for dev use).

---

## ⚙️ 2. Firebase CLI Setup

1. **Install Firebase CLI**:

   ```bash
   npm install -g firebase-tools
   ```

2. **Login to Firebase**:

   ```bash
   firebase login
   ```

3. **Initialize Firebase in your Flutter project (optional)**:

   ```bash
   firebase init
   ```

4. **Enable FlutterFire CLI**:

   ```bash
   dart pub global activate flutterfire_cli
   ```

5. **Configure FlutterFire**:

   ```bash
   flutterfire configure
   ```

   Choose your Firebase project and platform (Android). This will generate `firebase_options.dart`.

---

## 📲 3. Flutter App Configuration

### 🔧 Add dependencies to `pubspec.yaml`:

```yaml
dependencies:
  flutter:
    sdk: flutter
  firebase_core: ^2.0.0
  firebase_messaging: ^14.0.0
```

Then run:

```bash
flutter pub get
```

### 🔑 Modify Android Config

- **android/build.gradle**:
  ```gradle
  buildscript {
      dependencies {
          classpath 'com.google.gms:google-services:4.3.15' // or latest
      }
  }
  ```

- **android/app/build.gradle**:
  ```gradle
  apply plugin: 'com.google.gms.google-services'

  dependencies {
      implementation 'com.google.firebase:firebase-messaging:23.0.0' // or latest
  }
  ```

---

## 💻 4. Python Backend Setup

### 🔐 Firebase Admin SDK Setup

1. Go to Firebase Console → Project Settings → **Service Accounts**
2. Click **Generate new private key**
3. Download the `serviceAccountKey.json` and save it in the backend project directory (rename appropriately).

### 📦 Install Python Packages

```bash
pip install flask apscheduler firebase-admin
```

### 🧠 Start the Flask Server

Save your backend code as `app.py` and run:

```bash
python app.py
```

Make sure the console shows:

```
Server is running on port 5000
```

---

## 🔄 5. Connect Flutter with Backend

Uncomment and use the HTTP call in Flutter to register the FCM token to the backend:

```dart
// import 'package:http/http.dart' as http;
// import 'dart:convert';

// final userId = "user123";
// await http.post(
//   Uri.parse("http://<YOUR_IP>:5000/register-device"),
//   headers: {"Content-Type": "application/json"},
//   body: jsonEncode({"user_id": userId, "token": token}),
// );
```

Replace `<YOUR_IP>` with the IP of your machine running the Flask backend.

---

## 🔍 6. Testing the Setup

### 🧪 1. Launch the Flutter app
You should see your **FCM Token** printed and displayed.

### 🧪 2. Call `/create-task` from Postman or script:

```json
POST /create-task
Content-Type: application/json

{
  "type": "create_task",
  "user_id": "user123",
  "details": {
    "name": "Test Reminder",
    "date": "2025-06-10",
    "time": "15:30"
  }
}
```

If everything is successful, you’ll get a push notification on the device at the scheduled time.

---

## 📋 API Endpoints (Backend)

| Method | Endpoint              | Description                           |
|--------|-----------------------|---------------------------------------|
| POST   | `/register-device`    | Register device with user ID & token |
| POST   | `/create-task`        | Schedule a task reminder              |
| GET    | `/get-todos`          | Get all scheduled todos               |
| POST   | `/toggle-task-status` | Mark task as completed/incomplete     |

---

## ✅ Final Tips

- Make sure **both the Flutter app and Flask server** are on the **same network** if testing locally.
- Check for **firewall or network issues** if tokens are not received.
- Always use a proper database in production (instead of in-memory `user_tokens`).
