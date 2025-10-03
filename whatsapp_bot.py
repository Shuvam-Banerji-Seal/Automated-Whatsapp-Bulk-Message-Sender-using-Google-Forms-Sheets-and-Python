import time
from datetime import datetime
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
            
            # Wait longer for the chat to fully load before looking for message box
            print("🔄 Waiting for chat to load completely...")
            time.sleep(8)  # Longer initial wait
            
            # Check if we're actually in a chat (not on error page)
            try:
                current_url = self.driver.current_url
                if "web.whatsapp.com" not in current_url:
                    print(f"❌ Invalid URL redirect: {current_url}")
                    return False
            except:
                pass
            
            # Wait for the message input box to appear with multiple possible selectors
            # Avoid search box by being more specific about compose area
            message_box = None
            selectors = [
                '//div[@contenteditable="true"][@data-tab="10"]',  # Most specific for compose
                '//div[contains(@class, "selectable-text")][@contenteditable="true"][@data-tab="10"]',
                '//div[@data-testid="conversation-compose-box-input"]',
                '//div[contains(@aria-label, "Type a message")][@contenteditable="true"]',
                '//div[@title="Type a message"][@contenteditable="true"]',
                '//div[contains(@class, "lexical-rich-text-input")][@contenteditable="true"]',
                # Last resort, but exclude search (data-tab="3")
                '//div[@contenteditable="true"][@role="textbox"][not(@data-tab="3")]'
            ]
            
            # Wait longer and try multiple times
            print("🔍 Looking for message input box...")
            for attempt in range(5):  # Increased attempts
                for selector in selectors:
                    try:
                        # First check if element exists
                        elements = self.driver.find_elements(By.XPATH, selector)
                        if elements:
                            element = elements[0]
                            data_tab = element.get_attribute('data-tab')
                            
                            # Skip search box (data-tab="3")
                            if data_tab == '3':
                                continue
                                
                            # Wait for element to become visible and clickable
                            if element.is_displayed() and element.is_enabled():
                                message_box = element
                                print(f"✅ Found interactive message box: {selector} (data-tab: {data_tab})")
                                break
                            else:
                                print(f"⚠️ Found element but not ready: displayed={element.is_displayed()}, enabled={element.is_enabled()}")
                    except Exception as e:
                        print(f"⚠️ Selector failed: {e}")
                        continue
                
                if message_box is not None:
                    break
                    
                if attempt < 4:
                    print(f"🔄 Attempt {attempt + 1}/5: Waiting for chat interface...")
                    time.sleep(4)  # Wait longer between attempts
            
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
    
    def format_message_with_variables(self, message, name=None, phone=None):
        """Format message template with dynamic variables"""
        try:
            # Get current time in various formats
            now = datetime.now()
            
            # Replace variables in the message
            formatted_message = message
            
            # Name variable
            if name:
                formatted_message = formatted_message.replace('{name}', str(name))
                formatted_message = formatted_message.replace('{Name}', str(name))
                formatted_message = formatted_message.replace('{NAME}', str(name).upper())
            
            # Time variables
            formatted_message = formatted_message.replace('{time}', now.strftime('%H:%M'))
            formatted_message = formatted_message.replace('{date}', now.strftime('%B %d, %Y'))
            formatted_message = formatted_message.replace('{datetime}', now.strftime('%B %d, %Y at %H:%M'))
            formatted_message = formatted_message.replace('{day}', now.strftime('%A'))
            formatted_message = formatted_message.replace('{month}', now.strftime('%B'))
            formatted_message = formatted_message.replace('{year}', now.strftime('%Y'))
            
            # Phone variable (if needed)
            if phone:
                formatted_message = formatted_message.replace('{phone}', str(phone))
            
            return formatted_message
            
        except Exception as e:
            print(f"Error formatting message: {e}")
            return message
    
    def format_message_with_variables(self, message, name=None, phone=None):
        """Format message template with dynamic variables"""
        try:
            # Get current time in various formats
            now = datetime.now()
            
            # Replace variables in the message
            formatted_message = message
            
            # Name variable
            if name:
                formatted_message = formatted_message.replace('{name}', str(name))
                formatted_message = formatted_message.replace('{Name}', str(name))
                formatted_message = formatted_message.replace('{NAME}', str(name).upper())
            
            # Time variables
            formatted_message = formatted_message.replace('{time}', now.strftime('%H:%M'))
            formatted_message = formatted_message.replace('{date}', now.strftime('%B %d, %Y'))
            formatted_message = formatted_message.replace('{datetime}', now.strftime('%B %d, %Y at %H:%M'))
            formatted_message = formatted_message.replace('{day}', now.strftime('%A'))
            formatted_message = formatted_message.replace('{month}', now.strftime('%B'))
            formatted_message = formatted_message.replace('{year}', now.strftime('%Y'))
            
            # Phone variable (if needed)
            if phone:
                formatted_message = formatted_message.replace('{phone}', str(phone))
            
            return formatted_message
            
        except Exception as e:
            print(f"Error formatting message: {e}")
            return message

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
        
        # Step 3: Read contacts - Prioritize Google Sheets
        data = None
        
        # First choice: Try Google Sheets (recommended)
        sheet_id = "1-gSlQd7TgXHcBRUmO6Bg19zVzUCoPmMYiJo6LtmliLI"
        credentials_file = "credentials.json"
        
        if os.path.exists(credentials_file):
            print("� Reading contacts from Google Sheet (primary source)...")
            data = bot.read_google_sheet(sheet_id, credentials_file)
            if data:
                print("✅ Successfully loaded contacts from Google Sheets")
        else:
            print("⚠️ No credentials.json found for Google Sheets.")
        
        # Fallback: Try CSV file if Google Sheets failed or unavailable
        if data is None:
            csv_file = "contacts.csv"
            if not os.path.exists(csv_file):
                csv_file = "examples/contacts_example.csv"  # Fallback to example
                
            if os.path.exists(csv_file):
                print(f"� Reading contacts from {csv_file} (fallback source)...")
                data = bot.read_csv_file(csv_file)
                if csv_file == "examples/contacts_example.csv":
                    print("⚠️ Using example contacts. Create your own 'contacts.csv' file with real data.")
            else:
                print("❌ No contact sources available.")
                print("💡 Options:")
                print("   1. Set up Google Sheets API (recommended - see GOOGLE_SHEETS_SETUP.md)")
                print("   2. Create a 'contacts.csv' file with Name,Phone columns")
        
        # Send messages if we have data
        if data and len(data) > 0:
            print(f"📨 Found {len(data)} contacts, starting to send messages...")
            successful_sends = 0
            
            for i, row in enumerate(data, 1):
                phone = str(row.get('Phone', '')).strip()  # Convert to string and strip whitespace
                name = str(row.get('Name', '')).strip()    # Convert to string and strip whitespace
                
                if phone and name and phone != 'nan':  # Check for valid data
                    print(f"\n📱 Sending message {i}/{len(data)} to {name} ({phone})")
                    
                    # Format message with dynamic variables
                    personalized_msg = bot.format_message_with_variables(message, name=name, phone=phone)
                    
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