# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-03

### Added
- Initial release of WhatsApp News Bot
- Support for CSV file contact management
- Google Sheets integration for contact management
- Automated message personalization
- Unicode and emoji handling for ChromeDriver compatibility
- Session persistence with Chrome user data
- Comprehensive error handling and logging
- Multiple message template support
- Robust WhatsApp Web element detection with fallback selectors
- Progress tracking and detailed feedback
- Example files and documentation

### Features
- **Multi-source contacts**: CSV files and Google Sheets support
- **Template system**: Flexible message templates with personalization
- **Error recovery**: Automatic fallback for element detection
- **Session management**: Persistent Chrome sessions for easy re-login
- **Unicode safety**: Automatic handling of problematic characters
- **Progress tracking**: Real-time feedback during bulk messaging

### Security
- Comprehensive .gitignore for sensitive data protection
- Credential management best practices
- Session data protection

### Documentation
- Detailed README with setup instructions
- Google Sheets API setup guide
- Troubleshooting section
- Example files and templates
- MIT License

### Dependencies
- selenium >= 4.0.0
- gspread >= 5.0.0
- oauth2client >= 4.1.3