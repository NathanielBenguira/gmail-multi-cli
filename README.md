# Gmail Multi-Account CLI Tool

A powerful command-line interface for managing multiple Gmail accounts and sending test emails from each account. Features secure OAuth2 authentication, local token storage, and a beautiful CLI interface.

## ✨ Features

- 🔐 **Secure OAuth2 Authentication** - No password storage, uses Google's secure OAuth flow
- 📧 **Multi-Account Management** - Add, remove, and manage multiple Gmail accounts
- 📤 **Bulk Email Testing** - Send test emails from all registered accounts simultaneously
- 🔑 **Password Change Helper** - Generate secure passwords and open Google's password change page
- 🎨 **Beautiful CLI Interface** - Rich terminal interface with colors and tables
- 💾 **Local Token Storage** - OAuth tokens stored securely on your machine
- 🔒 **Privacy Focused** - All credentials and tokens are kept local

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Cloud Platform account
- Gmail accounts you want to manage

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/nathanielbenguira/gmail-multi-cli.git
   cd gmail-multi-cli
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Google Cloud credentials** (see setup guide below)

4. **Run the tool:**
   ```bash
   python main.py
   ```

## 🔧 Google Cloud Setup

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"

### Step 2: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Desktop application" as the application type
4. Give it a name (e.g., "Gmail Multi-Account CLI")
5. Download the credentials file

### Step 3: Configure Credentials

1. Rename the downloaded file to `credentials.json`
2. Place it in the project root directory
3. **Important:** Add `credentials.json` to your `.gitignore` to keep it private

## 📖 Usage

### Interactive Mode

Run the tool without arguments for an interactive menu:

```bash
python main.py
```

**Available options:**
1. **List accounts** - View all registered accounts and their status
2. **Add account** - Authenticate a new Gmail account
3. **Remove account** - Remove an account and its stored credentials
4. **Send test email** - Send test emails from all accounts
5. **Change password helper** - Generate secure passwords and open Google's password change page
6. **Exit** - Close the application

### Command Line Mode

Use direct commands for automation:

```bash
# List all accounts
python main.py --list

# Add a new account
python main.py --add user@gmail.com

# Remove an account
python main.py --remove user@gmail.com

# Send test email from all accounts
python main.py --send-test recipient@example.com

# Change password helper (use number or email)
python main.py --change-password 1
python main.py --change-password user@gmail.com
```

## 🔐 Security Features

### OAuth2 Authentication
- Uses Google's secure OAuth2 flow
- No passwords are ever stored
- Tokens are automatically refreshed when needed
- All authentication happens through Google's official channels

### Local Storage
- OAuth tokens stored locally in `.tokens/` directory
- Account information stored in JSON format
- All sensitive data is excluded from version control

### Password Generation
- Cryptographically secure password generation
- Uses Python's `secrets` module
- Ensures mixed character types (uppercase, lowercase, numbers, symbols)
- Auto-copy to clipboard functionality

## 📁 File Structure

```
gmail-multi-cli/
├── main.py              # Main CLI application
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── .gitignore          # Git ignore rules
├── credentials.json    # Your OAuth credentials (not in repo)
└── .tokens/            # Local token storage (not in repo)
    ├── accounts.json   # Account mapping
    └── *.pickle        # OAuth token files
```

## 🛠️ Configuration

### Supported Credential Files

The tool automatically detects credential files with these names:
- `credentials.json`
- `client_secret.json`
- `oauth_credentials.json`
- `client_secret_*.json` (any file matching this pattern)

### Environment Variables

No environment variables are required. All configuration is done through the Google Cloud Console and local credential files.

## 🔧 Troubleshooting

### Common Issues

**"No credentials file found"**
- Ensure you've downloaded the OAuth credentials from Google Cloud Console
- Place the file in the project root directory
- Use one of the supported file names

**"Authentication failed"**
- Check that the Gmail API is enabled in your Google Cloud project
- Ensure you're using the correct OAuth credentials
- Try removing and re-adding the account

**"Permission denied"**
- Make sure the OAuth consent screen is configured
- Check that the Gmail API scope is included in your credentials

### Getting Help

1. Check that all dependencies are installed: `pip install -r requirements.txt`
2. Verify your Google Cloud setup (API enabled, credentials created)
3. Ensure your credential file is in the correct location
4. Check the `.tokens/` directory exists and is writable

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for personal use and testing purposes. Please ensure you comply with:
- Google's Terms of Service
- Gmail's usage policies
- Applicable privacy laws and regulations

## 🔗 Links

- [Google Cloud Console](https://console.cloud.google.com/)
- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)

---

**Made with ❤️ for Gmail power users**
