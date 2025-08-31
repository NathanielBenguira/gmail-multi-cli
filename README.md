# Gmail Multi-Account CLI Tool

This CLI tool allows you to manage multiple Gmail accounts and send a test email from each account to a specified address. Credentials are stored locally and securely using OAuth2 tokens.

## Features
- Add/remove multiple Gmail accounts
- Send a test email from all accounts
- Manual trigger (run when you want)

## Setup
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Google Cloud Setup:**
   - Go to https://console.cloud.google.com/
   - Create a new project (or use an existing one)
   - Enable the Gmail API
   - Create OAuth 2.0 Client IDs (Desktop app)
   - Download the `credentials.json` file and place it in this folder (`gmail-multi-cli/`)

3. **Run the tool:**
   ```bash
   python main.py
   ```

The first time you add an account, a browser window will open for authentication. Tokens are stored locally for future use.
