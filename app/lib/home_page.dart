import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  String realtimeUrl = "http://172.17.7.236:8000/video_feed";
  String githubUrl = "https://github.com";

  WebViewController controller = WebViewController()
    ..setJavaScriptMode(JavaScriptMode.unrestricted)
    ..loadRequest(Uri.parse("http://localhost:8000/video_feed"));

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
              // Navegar a la página de configuración
            },
          ),
        ],
      ),
      body: Column(
        children: [
          Container(height: 225, child: WebViewWidget(controller: controller)),
          SizedBox(
            height: 100,
          ),
          Container(
            child: Center(
                child: TextButton(
                  onPressed: () {
                    
                  },
              child: Text("Make emotions analisis"),
            )),
          )
        ],
      ),
    );
  }
}
