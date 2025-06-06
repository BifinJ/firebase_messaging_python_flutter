import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  print("🔔 Background Message: ${message.notification?.title}");
}

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();
  FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(title: 'FCM Test App', home: MyHomePage());
  }
}

class MyHomePage extends StatefulWidget {
  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  String? _token = "Fetching...";

  @override
  void initState() {
    super.initState();
    initFCM();
  }

  void initFCM() async {
    FirebaseMessaging messaging = FirebaseMessaging.instance;

    // 🔒 Request permission (not mandatory on Android, but good practice)
    await messaging.requestPermission();

    // 📱 Get the FCM device token
    String? token = await messaging.getToken();
    setState(() {
      _token = token;
    });

    // Send token to your backend
    final userId = "user123"; // change as needed
    await http.post(
      Uri.parse("http://192.168.213.192:5000/register-device"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"user_id": userId, "token": token}),
    );

    // Handle foreground messages
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      print("🔔 Foreground: ${message.notification?.title}");
      showDialog(
        context: context,
        builder:
            (_) => AlertDialog(
              title: Text(message.notification?.title ?? 'No Title'),
              content: Text(message.notification?.body ?? 'No Body'),
            ),
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("FCM Test")),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: SelectableText("Your device FCM token:\n\n$_token"),
      ),
    );
  }
}
