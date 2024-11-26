import 'package:flutter/material.dart';
import 'package:fyc/emotions.dart';
import 'package:fyc/home_page.dart';

class MyNavBar extends StatefulWidget {
  const MyNavBar({super.key});

  @override
  State<MyNavBar> createState() => _MyNavBarState();
}

class _MyNavBarState extends State<MyNavBar> {
  int currentIndex = 0;
  final List<Widget> _screens = [
    const HomePage(),
    const EmotionsPage(),
    const Center(child: Text("other"),),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.blueAccent,
      // appBar: AppBar(
      //   title: const Text(
      //     "VORTEX",
      //     style: TextStyle(
      //         fontWeight: FontWeight.bold,
      //         fontSize: 24, // Tamaño de fuente más grande para el título
      //         color: colorMainPurple // Morado fuerte para el título
      //         ),
      //   ),
      //   centerTitle: true, // Centrar el título
      //   shadowColor: colorBG,
      //   scrolledUnderElevation: 10,
      //   backgroundColor: colorBG, // Hacer transparente el fondo del AppBar
      //   elevation: 0, // Sin sombra
      // ),
      body: _screens[currentIndex],
      bottomNavigationBar: BottomNavigationBar(
        backgroundColor: Colors.transparent,
        selectedItemColor: Colors.blue,
        unselectedItemColor: Colors.grey,
        currentIndex: currentIndex,
        onTap: (index) {
          setState(() {
            currentIndex = index;
          });
        },
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.home),
            label: 'Home',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.search),
            label: 'Search',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.military_tech_rounded),
            label: 'HWO',
          ),
        ],
      ),
    );
  }
}