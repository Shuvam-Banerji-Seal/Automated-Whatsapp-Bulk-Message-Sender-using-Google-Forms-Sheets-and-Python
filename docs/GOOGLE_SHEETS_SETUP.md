# Google Sheets API Setup Guide

To use Google Sheets integration with the WhatsApp bot, you need to set up API credentials. Here's how:

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Name your project (e.g., "WhatsApp Bot")

## Step 2: Enable Google Sheets API

1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google Sheets API"
3. Click on it and press "Enable"
4. Also enable "Google Drive API" (required for accessing sheets)

## Step 3: Create Service Account Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Enter a name for your service account (e.g., "whatsapp-bot-service")
4. Click "Create and Continue"
5. Skip the optional steps and click "Done"

## Step 4: Generate JSON Key

1. In the Credentials page, find your service account
2. Click on the service account email
3. Go to the "Keys" tab
4. Click "Add Key" > "Create New Key"
5. Select "JSON" format
6. Click "Create" - this will download the `credentials.json` file

## Step 5: Move Credentials File

1. Rename the downloaded file to `credentials.json`
2. Move it to your bot directory: `/home/shuvam/codes/whatsapp_iitk_news_bot/`

## Step 6: Share Your Google Sheet

1. Open your Google Sheet
2. Click "Share" button
3. Add the service account email (found in the credentials.json file)
4. Give it "Editor" permissions
5. Make sure "Notify people" is unchecked

## Your Sheet Format

Make sure your Google Sheet has these columns:
- **Name**: Contact's name
- **Phone**: Phone number with country code (e.g., 919876543210)

Example:
| Name | Phone |
|------|-------|
| John Doe | 919876543210 |
| Jane Smith | 917890123456 |

## Alternative: CSV File Method

If you prefer not to use Google Sheets API, you can use a CSV file instead (see contacts.csv option in the bot).