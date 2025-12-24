import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class LegalDisclaimer extends StatelessWidget {
  const LegalDisclaimer({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: AppTheme.warningColor.withOpacity(0.08),
        border: Border(
          top: BorderSide(
            color: AppTheme.warningColor.withOpacity(0.2),
            width: 1,
          ),
        ),
      ),
      child: Row(
        children: [
          Icon(
            Icons.info_outline,
            size: 14,
            color: AppTheme.warningColor.withOpacity(0.8),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              'Information juridique générale • Ne constitue pas un avis juridique',
              style: TextStyle(
                fontSize: 11,
                color: AppTheme.warningColor.withOpacity(0.8),
                fontWeight: FontWeight.w500,
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }
}
