# WhatsApp News Bot 🤖

An automated WhatsApp messaging bot built with Python and Selenium that can send bulk messages to contacts from CSV files or Google Sheets. Perfect for sending news updates, announcements, or notifications to multiple contacts.

## 🚀 Features

- **Multiple Data Sources**: Read contacts from CSV files or Google Sheets
- **Bulk Messaging**: Send personalized messages to multiple contacts
- **Message Templates**: Support for text files with message templates
- **Unicode Safe**: Automatic handling of emojis and special characters
- **Session Persistence**: Chrome user data saved for easy re-login
- **Error Handling**: Robust error handling with detailed feedback
- **Progress Tracking**: Real-time progress updates during message sending

## 📋 Requirements

- Python 3.7+
- Chrome/Chromium browser
- ChromeDriver (automatically managed by selenium)
- Virtual environment (recommended)

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd whatsapp_iitk_news_bot
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 📊 Setup Options

### Option 1: CSV File (Recommended for beginners)

1. **Create/Edit `contacts.csv`:**
   ```csv
   Name,Phone
   John Doe,919876543210
   Jane Smith,917890123456
   ```

2. **Create your message in `message.txt`:**
   ```
   Hello! This is your news update for today...
   ```

3. **Run the bot:**
   ```bash
   python whatsapp_bot.py
   ```

### Option 2: Google Sheets Integration

1. **Set up Google Sheets API** (see [GOOGLE_SHEETS_SETUP.md](GOOGLE_SHEETS_SETUP.md))
2. **Download `credentials.json`** and place it in the project directory
3. **Share your Google Sheet** with the service account email
4. **Run the bot** - it will automatically use Google Sheets if no CSV is found

## 📁 Project Structure

```
whatsapp_iitk_news_bot/
├── whatsapp_bot.py          # Main bot script
├── requirements.txt         # Python dependencies
├── message.txt              # Message template
├── message_no_emoji.txt     # Emoji-free message template
├── contacts.csv             # Contact list (create this)
├── credentials.json         # Google Sheets API credentials (create this)
├── GOOGLE_SHEETS_SETUP.md   # Google Sheets setup guide
├── User_Data/               # Chrome session data (auto-created)
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## 🔧 Configuration

### Message Templates

- **`message.txt`**: Main message template
- **`message_no_emoji.txt`**: Fallback template without emojis
- Supports multi-line messages with proper formatting

### Contact Format

**CSV File:**
```csv
Name,Phone
Contact Name,Country_Code_Phone_Number
```

**Google Sheets:**
- Column A: Name
- Column B: Phone
- Phone numbers should include country code (e.g., 919876543210 for India)

## 🚀 Usage

1. **First Run:**
   - The bot will open WhatsApp Web
   - Scan the QR code with your phone
   - Session will be saved for future runs

2. **Subsequent Runs:**
   - Bot will use saved session (no QR scan needed)
   - Automatically reads contacts and sends messages

3. **Message Personalization:**
   ```python
   # Messages are automatically personalized:
   # "Hi {Name}! Your message content here..."
   ```

## ⚙️ Advanced Configuration

### Chrome Options

```python
# In whatsapp_bot.py, you can modify Chrome options:
chrome_options.add_argument("--headless")  # Run in background
chrome_options.add_argument("--no-sandbox")  # For server environments
```

### Error Handling

The bot includes comprehensive error handling for:
- Network connectivity issues
- WhatsApp Web loading problems
- Invalid phone numbers
- Unicode/emoji compatibility
- API rate limiting

## 🔒 Security & Privacy

- **Credentials**: Never commit `credentials.json` or personal data
- **Session Data**: `User_Data/` contains your WhatsApp session
- **Contact Lists**: Keep `contacts.csv` private
- **Logs**: Check logs for any sensitive information before sharing

## 🐛 Troubleshooting

### Common Issues

1. **"ChromeDriver only supports characters in the BMP"**
   - Solution: Bot automatically removes problematic characters

2. **"No such file or directory: credentials.json"**
   - Solution: Use CSV file method or set up Google Sheets API

3. **WhatsApp Web not loading**
   - Solution: Check internet connection, clear User_Data folder

4. **Messages not sending**
   - Solution: Verify phone numbers include country code
   - Check WhatsApp Web is properly loaded

### Debug Mode

```bash
# Run with verbose output
python whatsapp_bot.py --debug
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Additional Terms:**
- If you use this project for events, organizations, or public purposes, please star ⭐ this repository and provide attribution as described in the Attribution section above.
- Commercial use is permitted under MIT License terms, but attribution is appreciated.

## ⚠️ Disclaimer

- This bot is for educational and legitimate business purposes only
- Respect WhatsApp's Terms of Service and local regulations
- Avoid spamming and respect recipient privacy
- Use responsibly and ethically

## 🙏 Attribution & Credits

**If you use this project for your events, organizations, or any public purpose, please:**

1. **⭐ Star this repository** - It helps others discover this project
2. **📝 Give credit** - Mention this project in your documentation/announcements
3. **🔗 Link back** - Include a link to this repository

**Example credit format:**
```
WhatsApp messaging powered by: https://github.com/Shuvam-Banerji-Seal/Automated-Whatsapp-Bulk-Message-Sender-using-Google-Forms-Sheets-and-Python
```

**For academic/research use:** Please cite this repository in your work.

**For commercial use:** Consider reaching out to discuss collaboration opportunities.

Your support helps maintain and improve this project for everyone! 🚀

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a Pull Request

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the setup guides in the docs folder
3. Create an issue with detailed error logs

## 🔄 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.

---

**Happy Messaging! 🚀**