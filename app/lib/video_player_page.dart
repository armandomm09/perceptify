// video_player_page.dart
import 'package:flutter/material.dart';
import 'package:video_player/video_player.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:fl_chart/fl_chart.dart';

class VideoPlayerPage extends StatefulWidget {
  final int videoId; 
  final String videoUuid; 

  const VideoPlayerPage({Key? key, required this.videoId, required this.videoUuid}) : super(key: key);

  @override
  _VideoPlayerPageState createState() => _VideoPlayerPageState();
}

class _VideoPlayerPageState extends State<VideoPlayerPage> {
  late VideoPlayerController _controller;
  late Future<void> _initializeVideoPlayerFuture;

  Map<String, dynamic>? analysisData; 
  bool isLoadingAnalysis = true;

  @override
  void initState() {
    super.initState();
    String videoUrl = 'http://10.50.87.175:8000/emotion_video/${widget.videoUuid}';

   
    _controller = VideoPlayerController.network(videoUrl);
    _initializeVideoPlayerFuture = _controller.initialize();

   
    _controller.setLooping(true);

   
    fetchAnalysisData();
  }

  Future<void> fetchAnalysisData() async {
    final response = await http.get(Uri.parse('http://10.50.87.175:8000/emotions_by_video/${widget.videoId}'));

    if (response.statusCode == 200) {
      setState(() {
        analysisData = json.decode(response.body);
        isLoadingAnalysis = false;
      });
    } else {
      setState(() {
        isLoadingAnalysis = false;
      });
      print('Error al obtener los datos del análisis');
    }
  }

  @override
  void dispose() {
   
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.blueAccent,
        title: const Text('Análisis de Emociones'),
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
          
            SizedBox(height: 50,),
            Center(
              child: Container(
                height: 200,
                child: FutureBuilder(
                  future: _initializeVideoPlayerFuture,
                  builder: (context, snapshot) {
                    if (snapshot.connectionState == ConnectionState.done) {
                   
                      return AspectRatio(
                        aspectRatio: _controller.value.aspectRatio,
                        child: VideoPlayer(_controller),
                      );
                    } else {
                    
                      return const Center(child: CircularProgressIndicator());
                    }
                  },
                ),
              ),
            ),
            const SizedBox(height: 20),
            // Datos del análisis
            isLoadingAnalysis
                ? const CircularProgressIndicator()
                : analysisData != null
                    ? buildAnalysisSection()
                    : const Text('No hay datos de análisis disponibles'),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          
          setState(() {
            _controller.value.isPlaying ? _controller.pause() : _controller.play();
          });
        },
        child: Icon(_controller.value.isPlaying ? Icons.pause : Icons.play_arrow),
      ),
    );
  }

  Widget buildAnalysisSection() {
    
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          
          buildMostFrequentEmotion(),
          const SizedBox(height: 20),
         
          buildPieChart(),
        ],
      ),
    );
  }

  Widget buildMostFrequentEmotion() {
    
    String emotion = analysisData!['most_frequent_emotion'];

    
    Map<String, IconData> emotionIcons = {
      'angry': Icons.sentiment_very_dissatisfied,
      'disgust': Icons.sentiment_dissatisfied,
      'fear': Icons.sentiment_neutral,
      'happy': Icons.sentiment_very_satisfied,
      'neutral': Icons.sentiment_neutral,
      'sad': Icons.sentiment_dissatisfied,
      'surprise': Icons.sentiment_satisfied,
    };

    IconData iconData = emotionIcons[emotion] ?? Icons.sentiment_neutral;

    return Column(
      children: [
        Text(
          'Emoción Más Frecuente',
          style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 10),
        Icon(
          iconData,
          color: Colors.blue,
          size: 80,
        ),
        const SizedBox(height: 10),
        Text(
          emotion[0].toUpperCase() + emotion.substring(1),
          style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
        ),
      ],
    );
  }

  Widget buildPieChart() {
    
    Map<String, dynamic> avgProbs = analysisData!['average_probabilities'];

    List<PieChartSectionData> sections = [];
    List<Color> colors = [
      Colors.redAccent,
      Colors.green,
      Colors.purple,
      Colors.yellow,
      Colors.blueGrey,
      Colors.blue,
      Colors.orange,
    ];

    List<String> emotions = [
      'angry',
      'disgust',
      'fear',
      'happy',
      'neutral',
      'sad',
      'surprise'
    ];

    int index = 0;
    for (var emotion in emotions) {
      double value = avgProbs['avg_$emotion'] * 100; 
      if (value > 0) {
        sections.add(PieChartSectionData(
          color: colors[index % colors.length],
          value: value,
          title: '${value.toStringAsFixed(1)}%',
          radius: 60,
          titleStyle: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ));
      }
      index++;
    }

    return Column(
      children: [
        Text(
          'Distribución de Emociones',
          style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 10),
        SizedBox(
          height: 250,
          child: PieChart(
            PieChartData(
              sections: sections,
              centerSpaceRadius: 40,
              sectionsSpace: 2,
              borderData: FlBorderData(show: false),
            ),
          ),
        ),
        const SizedBox(height: 20),
        // Leyenda
        Wrap(
          alignment: WrapAlignment.center,
          spacing: 10,
          runSpacing: 10,
          children: List.generate(emotions.length, (index) {
            String emotion = emotions[index];
            double value = avgProbs['avg_$emotion'] * 100;
            if (value > 0) {
              return Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 12,
                    height: 12,
                    color: colors[index % colors.length],
                  ),
                  const SizedBox(width: 5),
                  Text(
                    '${emotion[0].toUpperCase()}${emotion.substring(1)}',
                    style: const TextStyle(fontSize: 14),
                  ),
                ],
              );
            } else {
              return const SizedBox.shrink();
            }
          }),
        ),
      ],
    );
  }
}
