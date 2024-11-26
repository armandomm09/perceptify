class VideoData {
  final int id;
  final String path;
  final DateTime timestamp;
  final String uuid;

  VideoData({
    required this.id,
    required this.path,
    required this.timestamp,
    required this.uuid,
  });

  factory VideoData.fromJson(Map<String, dynamic> json) {
    return VideoData(
      id: json['id'],
      path: json['path'],
      timestamp: DateTime.parse(json['timestamp']),
      uuid: json['uuid'],
    );
  }
}
