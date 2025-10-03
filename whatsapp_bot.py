import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import csv
import unicodedata
import re

class WhatsAppBot:
    def __init__(self):
        """Initialize the WhatsApp bot with Chrome driver"""
        chrome_options = Options()
        chrome_options.add_argument("--user-data-dir=./User_Data")  # Save session
        chrome_options.add_argument("--profile-directory=Default")
        # chrome_options.add_argument("--headless")  # Uncomment for headless mode
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 30)
    
    def open_whatsapp(self):
        """Open WhatsApp Web and wait for QR scan"""
        print("Opening WhatsApp Web...")
        self.driver.get("https://web.whatsapp.com")
        print("Please scan the QR code if prompted...")
        
        # Wait for the main page to load (try multiple selectors)
        selectors = [
            '//div[@contenteditable="true"][@data-tab="3"]',  # Search box
            '//div[@data-testid="chat-list"]',  # Chat list
            '//div[contains(@class, "two")]',  # Main layout
            '//span[contains(text(), "WhatsApp")]'  # WhatsApp text
        ]
        
        loaded = False
        for selector in selectors:
            try:
                self.wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                print("WhatsApp Web loaded successfully!")
                loaded = True
                break
            except:
                continue
        
        if not loaded:
            print("⚠️ Waiting for WhatsApp to load... Make sure you scan the QR code.")
            time.sleep(15)
            # Try one more time with a longer wait
            try:
                self.wait.until(EC.presence_of_element_located(
                    (By.XPATH, '//div[@data-testid="chat-list"]')
                ))
                print("WhatsApp Web loaded successfully!")
            except:
                print("❌ WhatsApp Web failed to load properly. Please check your connection and try again.")
    
    def sanitize_message(self, message):
        """
        Sanitize message to remove characters that ChromeDriver can't handle
        Removes emojis and normalizes Unicode characters
        """
        try:
            # Remove emojis and other non-BMP characters
            # BMP = Basic Multilingual Plane (Unicode characters U+0000 to U+FFFF)
            sanitized = ''.join(char for char in message if ord(char) <= 0xFFFF)
            
            # Normalize Unicode characters
            sanitized = unicodedata.normalize('NFKC', sanitized)
            
            # Remove any remaining problematic characters
            sanitized = re.sub(r'[^\x00-\x7F\u0080-\uFFFF]', '', sanitized)
            
            return sanitized
        except Exception as e:
            print(f"⚠️ Warning: Error sanitizing message: {e}")
            # Fallback: keep only ASCII characters
            return ''.join(char for char in message if ord(char) < 128)
    
    def read_message_from_file(self, file_path):
        """Read message content from a file (supports .txt, .md, .html)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            print(f"Message loaded from {file_path}")
            
            # Sanitize the message to avoid ChromeDriver issues
            sanitized_content = self.sanitize_message(content)
            if sanitized_content != content:
                print("⚠️ Message contained special characters/emojis that were removed for compatibility")
            
            return sanitized_content
        except FileNotFoundError:
            print(f"Error: File {file_path} not found!")
            return None
    
    def send_message(self, phone_number, message):
        """
        Send a message to a phone number
        phone_number: Include country code without + (e.g., '919876543210')
        message: The text message to send
        """
        try:
            # Sanitize the message before sending
            sanitized_message = self.sanitize_message(message)
            
            # Open chat using phone number
            url = f"https://web.whatsapp.com/send?phone={phone_number}"
            self.driver.get(url)
            print(f"Opening chat with {phone_number}...")
            
            # Wait for the message input box to appear with multiple possible selectors
            message_box = None
            selectors = [
                '//div[@contenteditable="true"][@data-tab="10"]',
                '//div[@contenteditable="true"][@role="textbox"]',
                '//div[contains(@class, "lexical-rich-text-input")]',
                '//div[@title="Type a message"]',
                '//div[@data-testid="conversation-compose-box-input"]'
            ]
            
            for selector in selectors:
                try:
                    message_box = self.wait.until(EC.presence_of_element_located(
                        (By.XPATH, selector)
                    ))
                    print(f"Found message box with selector: {selector}")
                    break
                except:
                    continue
            
            if message_box is None:
                print(f"❌ Could not find message input box for {phone_number}")
                return False
            
            time.sleep(3)  # Increased delay to ensure page is ready
            
            # Clear any existing text and focus on the input
            message_box.clear()
            message_box.click()
            time.sleep(1)
            
            # Split message by lines and send (to preserve formatting)
            lines = sanitized_message.split('\n')
            for i, line in enumerate(lines):
                if line.strip():  # Only send non-empty lines
                    message_box.send_keys(line)
                if i < len(lines) - 1:  # Not the last line
                    message_box.send_keys(Keys.SHIFT + Keys.ENTER)
            
            # Send the message
            message_box.send_keys(Keys.ENTER)
            print(f"Message sent to {phone_number}!")
            time.sleep(3)  # Wait for message to be sent
            
            return True
            
        except Exception as e:
            print(f"❌ Error sending message to {phone_number}: {str(e)}")
            return False
    
    def read_csv_file(self, csv_file_path):
        """
        Read contacts from a CSV file
        csv_file_path: Path to CSV file with Name and Phone columns
        """
        try:
            data = []
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    data.append(row)
            print(f"Successfully read {len(data)} rows from CSV file")
            return data
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return None
    
    def read_google_sheet(self, sheet_id, credentials_file):
        """
        Read data from Google Sheet
        sheet_id: Your Google Sheet ID (from the URL)
        credentials_file: Path to your service account JSON file
        """
        try:
            scope = ['https://spreadsheets.google.com/feeds',
                     'https://www.googleapis.com/auth/drive']
            
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                credentials_file, scope
            )
            client = gspread.authorize(creds)
            
            # Open the spreadsheet
            sheet = client.open_by_key(sheet_id).sheet1
            
            # Get all records
            data = sheet.get_all_records()
            print(f"Successfully read {len(data)} rows from Google Sheet")
            return data
            
        except Exception as e:
            print(f"Error reading Google Sheet: {e}")
            return None
    
    def close(self):
        """Close the browser"""
        print("Closing browser...")
        self.driver.quit()


# ===== USAGE EXAMPLE =====
if __name__ == "__main__":
    # Initialize bot
    bot = WhatsAppBot()
    
    try:
        # Step 1: Open WhatsApp Web
        bot.open_whatsapp()
        
        # Step 2: Read message from file
        # You can use .txt, .md, or .html files
        message_file = "templates/message.txt"  # Updated path
        message = bot.read_message_from_file(message_file)
        
        # If file doesn't exist, try fallback
        if message is None:
            message_file = "templates/message_no_emoji.txt"
            message = bot.read_message_from_file(message_file)
        
        # If still no file, use a default message
        if message is None:
            message = """Hello! 
This is an automated message sent via Python + Selenium.

Best regards,
Your WhatsApp Bot"""
        
        # Step 3: Read contacts and send messages
        data = None
        
        # Try CSV file first (simpler option)
        csv_file = "contacts.csv"
        if not os.path.exists(csv_file):
            csv_file = "examples/contacts_example.csv"  # Fallback to example
            
        if os.path.exists(csv_file):
            print(f"📄 Reading contacts from {csv_file}...")
            data = bot.read_csv_file(csv_file)
            if csv_file == "examples/contacts_example.csv":
                print("⚠️ Using example contacts. Create your own 'contacts.csv' file with real data.")
        
        # If no CSV or CSV failed, try Google Sheets
        if data is None:
            sheet_id = "1-gSlQd7TgXHcBRUmO6Bg19zVzUCoPmMYiJo6LtmliLI"
            credentials_file = "credentials.json"
            
            if os.path.exists(credentials_file):
                print("📊 Reading contacts from Google Sheet...")
                data = bot.read_google_sheet(sheet_id, credentials_file)
            else:
                print("❌ No credentials.json found for Google Sheets.")
                print("💡 Options:")
                print("   1. Create a 'contacts.csv' file with Name,Phone columns")
                print("   2. Set up Google Sheets API (see GOOGLE_SHEETS_SETUP.md)")
        
        # Send messages if we have data
        if data and len(data) > 0:
            print(f"📨 Found {len(data)} contacts, starting to send messages...")
            successful_sends = 0
            
            for i, row in enumerate(data, 1):
                phone = row.get('Phone')  # Column name in your file
                name = row.get('Name')    # Column name in your file
                
                if phone and name:
                    print(f"\n📱 Sending message {i}/{len(data)} to {name} ({phone})")
                    
                    # Personalize message
                    personalized_msg = f"Hi {name}!\n\n" + message
                    
                    success = bot.send_message(phone, personalized_msg)
                    if success:
                        successful_sends += 1
                        print(f"✅ Message sent successfully to {name}")
                    else:
                        print(f"❌ Failed to send message to {name}")
                    
                    time.sleep(5)  # Wait between messages to avoid being blocked
                else:
                    print(f"⚠️ Skipping row {i}: Missing phone or name data")
            
            print(f"\n📊 Summary: {successful_sends}/{len(data)} messages sent successfully")
        else:
            print("❌ No contacts found. Please create either:")
            print("   • contacts.csv file with Name,Phone columns")
            print("   • Google Sheets API setup (see GOOGLE_SHEETS_SETUP.md)")
        
        print("\n✅ All messages sent successfully!")
        
        # Keep browser open for a few seconds
        time.sleep(5)
        
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        # Close browser
        bot.close()