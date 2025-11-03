import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() => runApp(SentinelApp());

class SentinelApp extends StatefulWidget {
  @override _SentinelAppState createState() => _SentinelAppState();
}

class _SentinelAppState extends State<SentinelApp> {
  String status = "Connecting...";
  List<String> alerts = [];

  @override
  void initState() {
    super.initState();
    checkStatus();
  }

  void checkStatus() async {
    try {
      final res = await http.get(Uri.parse("http://YOUR_ADAM_IP:8000/status"));
      setState(() {
        status = json.decode(res.body)["status"];
      });
    } catch (e) {
      status = "Backend offline";
    }
  }

  void travelMode() async {
    final ctrl = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text("Travel Mode"),
        content: TextField(controller: ctrl, decoration: InputDecoration(hintText: "Paris, 7 days")),
        actions: [
          TextButton(
            onPressed: () async {
              await http.post(Uri.parse("http://YOUR_ADAM_IP:8000/travel"), body: json.encode({"location": ctrl.text}));
              setState(() => alerts.add("Travel: ${ctrl.text}"));
              Navigator.pop(ctx);
            },
            child: Text("Save"),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(title: Text("Sentinel Guard"), backgroundColor: Colors.black),
        body: Column(children: [
          Text("Status: $status", style: TextStyle(color: Colors.cyan)),
          ElevatedButton(onPressed: travelMode, child: Text("I'm Traveling")),
          Expanded(child: ListView.builder(
            itemCount: alerts.length,
            itemBuilder: (c, i) => ListTile(title: Text(alerts[i])),
          )),
        ]),
      ),
    );
  }
}
