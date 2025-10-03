# Quick Start Guide

## 🚀 5-Minute Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create Your Contact List
Create `contacts.csv` in the root directory:
```csv
Name,Phone
John Doe,919876543210
Jane Smith,917890123456
```

### 3. Customize Your Message
Edit `templates/message.txt`:
```
Hello! This is your daily news update...
```

### 4. Run the Bot
```bash
python whatsapp_bot.py
```

### 5. Scan QR Code
- Bot opens WhatsApp Web
- Scan QR code with your phone
- Messages will be sent automatically!

## 📋 File Structure After Setup
```
├── whatsapp_bot.py          # Main script
├── contacts.csv             # Your contact list
├── templates/
│   └── message.txt          # Your message template
└── User_Data/               # Chrome session (auto-created)
```

## 🔧 Advanced Options

### Use Google Sheets Instead
1. Follow `docs/GOOGLE_SHEETS_SETUP.md`
2. Remove `contacts.csv` file
3. Bot will automatically use Google Sheets

### Multiple Message Templates
- Create different `.txt` files in `templates/`
- Modify `message_file` in `whatsapp_bot.py`

That's it! Happy messaging! 🎉