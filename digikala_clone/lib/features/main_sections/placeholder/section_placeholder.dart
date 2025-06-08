import 'package:flutter/material.dart';

class SectionPlaceholder extends StatelessWidget {
  final String title;
  final Color? color; // Optional color for visual distinction

  const SectionPlaceholder({Key? key, required this.title, this.color}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      color: color ?? Colors.transparent,
      child: Center(
        child: Text(
          title,
          style: Theme.of(context).textTheme.headlineMedium?.copyWith(fontFamily: 'IranYekan'),
        ),
      ),
    );
  }
}
