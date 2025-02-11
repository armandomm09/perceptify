import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';
import 'package:http/http.dart' as http;

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  String realtimeUrl = "http://10.50.87.175:8000/video_feed";
  String detectEmotionUrl = "http://10.50.87.175:8000/detect_emotion";

  WebViewController controller = WebViewController()
    ..setJavaScriptMode(JavaScriptMode.unrestricted)
    ..loadRequest(Uri.parse("http://10.50.87.175:8000/video_feed"));

  Future<void> fetchEmotionAnalysis() async {
    try {
      final response = await http.get(Uri.parse(detectEmotionUrl));
      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Emotion analysis result: ${response.body}')),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to fetch emotion analysis')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('FYC'),
        backgroundColor: Colors.blueAccent,
        actions: [
          IconButton(
            icon: Icon(Icons.settings),
            onPressed: () {
            },
          ),
        ],
      ),
      body: Column(
        children: [
          Container(height: 225, child: WebViewWidget(controller: controller)),
          SizedBox(height: 100),
          Container(
            child: Center(
              child: TextButton(
                onPressed: fetchEmotionAnalysis,
                child: Text("Make emotions analysis"),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
