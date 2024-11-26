// emotions_page.dart
import 'package:flutter/material.dart';
import 'package:fyc/model/video_data.dart';
import 'package:fyc/video_player_page.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

import 'package:mesh_gradient/mesh_gradient.dart';

class EmotionsPage extends StatefulWidget {
  const EmotionsPage({super.key});

  @override
  State<EmotionsPage> createState() => _EmotionsPageState();
}

class _EmotionsPageState extends State<EmotionsPage> {
  Future<List<VideoData>> fetchVideos() async {
    final response =
        await http.get(Uri.parse('http://localhost:8000/all_emotion_videos'));

    if (response.statusCode == 200) {
      List<dynamic> jsonData = json.decode(response.body);
      List<VideoData> videos =
          jsonData.map((item) => VideoData.fromJson(item)).toList();
      return videos;
    } else {
      throw Exception('Error al cargar los videos');
    }
  }



  meshGrid(BuildContext context) {
    late final AnimatedMeshGradientController _controller =
        AnimatedMeshGradientController();
  _controller.start();
    return Center(
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(20)
        ),
          height: MediaQuery.of(context).size.height,
          width: MediaQuery.of(context).size.width,
          child: AnimatedMeshGradient(
            colors: [
              const Color.fromARGB(255, 17, 17, 17),
              const Color.fromARGB(255, 24, 25, 26),
               Colors.blueAccent,
              const Color.fromARGB(255, 17, 17, 17),
            ],
            options: AnimatedMeshGradientOptions(),
            controller: _controller,
          )),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // appBar: AppBar(
      //   title: const Text('Emotion Videos'),
      // ),
      body: Stack(
        children: [
          meshGrid(context),
          FutureBuilder<List<VideoData>>(
            future: fetchVideos(),
            builder: (context, snapshot) {
              if (snapshot.hasData) {
                List<VideoData> videos = snapshot.data!;
                return ListView.builder(
                  itemCount: videos.length,
                  itemBuilder: (context, index) {
                    VideoData video = videos[index];
                    return GestureDetector(
                      // En emotions_page.dart
          onTap: () {
            // Navegar a la página del reproductor de video
            Navigator.push(
              context,
              MaterialPageRoute(
          builder: (context) => VideoPlayerPage(
            videoId: video.id,
            videoUuid: video.uuid,
          ),
              ),
            );
          },
          
                      child: Padding(
                        padding: const EdgeInsets.all(8.0),
                        child: Center(
                          child: Container(
                            margin: const EdgeInsets.symmetric(vertical: 8.0),
                            height: 60,
                            width: MediaQuery.of(context).size.width * 0.8,
                            decoration: BoxDecoration(
                              color: Colors.blueAccent,
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Padding(
                              padding: const EdgeInsets.all(8.0),
                              child: Column(
                                children: [
                                  Text(
                                    "Emotion Detection at: ${video.timestamp}",
                                    style: const TextStyle(
                                        color: Colors.white,
                                        fontWeight: FontWeight.bold),
                                  )
                                ],
                              ),
                            ),
                          ),
                        ),
                      ),
                    );
                  },
                );
              } else if (snapshot.hasError) {
                return const Center(child: Text('Error al cargar los videos'));
              } else {
                return const Center(child: CircularProgressIndicator());
              }
            },
          ),
        ],
      ),
    );
  }
}
