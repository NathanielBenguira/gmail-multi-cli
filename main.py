#!/usr/bin/env python3
"""
Gmail Multi-Account CLI Tool
Allows managing multiple Gmail accounts and sending test emails from each account.
"""

import os
import json
import pickle
import secrets
import string
import webbrowser
from pathlib import Path
from typing import Dict, List, Optional
import argparse
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text
from rich.syntax import Syntax

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# File paths
CREDENTIALS_FILE = 'client_secret_641266316519-ia1ng9fdbvf5hl5bdbv2i99iqscrgjuo.apps.googleusercontent.com.json'
TOKENS_DIR = Path('.tokens')
ACCOUNTS_FILE = TOKENS_DIR / 'accounts.json'

console = Console()


class GmailMultiAccountCLI:
    def __init__(self):
        self.accounts: Dict[str, str] = {}  # email -> token_file_path
        self.load_accounts()
        
    def load_accounts(self):
        """Load existing accounts from storage."""
        if ACCOUNTS_FILE.exists():
            try:
                with open(ACCOUNTS_FILE, 'r') as f:
                    self.accounts = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.accounts = {}
    
    def save_accounts(self):
        """Save accounts to storage."""
        TOKENS_DIR.mkdir(exist_ok=True)
        with open(ACCOUNTS_FILE, 'w') as f:
            json.dump(self.accounts, f, indent=2)
    
    def get_credentials(self, email: str) -> Optional[Credentials]:
        """Get credentials for a specific email account."""
        if email not in self.accounts:
            return None
            
        token_file = TOKENS_DIR / self.accounts[email]
        
        if not token_file.exists():
            return None
            
        try:
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)
                
            # If credentials are expired, refresh them
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open(token_file, 'wb') as token:
                    pickle.dump(creds, token)
                    
            return creds
        except Exception as e:
            console.print(f"[red]Error loading credentials for {email}: {e}[/red]")
            return None
    
    def authenticate_account(self, email: str) -> bool:
        """Authenticate a new Gmail account."""
        if not os.path.exists(CREDENTIALS_FILE):
            console.print(f"[red]Error: {CREDENTIALS_FILE} not found![/red]")
            console.print("Please download your OAuth 2.0 credentials from Google Cloud Console.")
            return False
        
        try:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            
            # Save credentials
            token_file = f"{email.replace('@', '_at_').replace('.', '_')}.pickle"
            token_path = TOKENS_DIR / token_file
            
            TOKENS_DIR.mkdir(exist_ok=True)
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
            
            # Add to accounts
            self.accounts[email] = token_file
            self.save_accounts()
            
            console.print(f"[green]Successfully authenticated {email}[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]Authentication failed for {email}: {e}[/red]")
            return False
    
    def send_test_email(self, email: str, to_email: str) -> bool:
        """Send a test email from a specific account."""
        creds = self.get_credentials(email)
        if not creds:
            console.print(f"[red]No valid credentials found for {email}[/red]")
            return False
        
        try:
            service = build('gmail', 'v1', credentials=creds)
            
            # Create email message
            message = {
                'raw': self._create_message(email, to_email, 
                                          f"Test Email from {email}",
                                          f"This is a test email sent from {email} using the Gmail Multi-Account CLI tool.\n\nSent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            }
            
            # Send the email
            sent_message = service.users().messages().send(userId='me', body=message).execute()
            
            console.print(f"[green]✓ Test email sent from {email} to {to_email}[/green]")
            return True
            
        except HttpError as error:
            console.print(f"[red]Error sending email from {email}: {error}[/red]")
            return False
        except Exception as e:
            console.print(f"[red]Unexpected error sending email from {email}: {e}[/red]")
            return False
    
    def _create_message(self, sender: str, to: str, subject: str, body: str) -> str:
        """Create a base64 encoded email message."""
        import base64
        from email.mime.text import MIMEText
        
        message = MIMEText(body)
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        
        return base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    
    def list_accounts(self, show_numbers: bool = False):
        """Display all registered accounts."""
        if not self.accounts:
            console.print("[yellow]No accounts registered yet.[/yellow]")
            return
        
        table = Table(title="Registered Gmail Accounts")
        if show_numbers:
            table.add_column("#", style="bold magenta")
        table.add_column("Email", style="cyan")
        table.add_column("Status", style="green")
        
        for i, email in enumerate(self.accounts, 1):
            creds = self.get_credentials(email)
            status = "✓ Valid" if creds else "✗ Invalid/Expired"
            if show_numbers:
                table.add_row(str(i), email, status)
            else:
                table.add_row(email, status)
        
        console.print(table)
    
    def remove_account(self, email: str) -> bool:
        """Remove an account and its stored credentials."""
        if email not in self.accounts:
            console.print(f"[red]Account {email} not found.[/red]")
            return False
        
        # Remove token file
        token_file = TOKENS_DIR / self.accounts[email]
        if token_file.exists():
            token_file.unlink()
        
        # Remove from accounts
        del self.accounts[email]
        self.save_accounts()
        
        console.print(f"[green]Successfully removed account {email}[/green]")
        return True
    
    def send_test_from_all_accounts(self, to_email: str):
        """Send test emails from all registered accounts."""
        if not self.accounts:
            console.print("[yellow]No accounts registered. Please add accounts first.[/yellow]")
            return
        
        console.print(f"\n[bold]Sending test emails to {to_email} from all accounts...[/bold]")
        
        success_count = 0
        total_count = len(self.accounts)
        
        for email in self.accounts:
            if self.send_test_email(email, to_email):
                success_count += 1
        
        console.print(f"\n[bold]Results: {success_count}/{total_count} emails sent successfully[/bold]")
    
    def generate_secure_password(self, length: int = 16) -> str:
        """Generate a secure password with mixed characters."""
        # Define character sets
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # Ensure at least one character from each set
        password = [
            secrets.choice(lowercase),
            secrets.choice(uppercase),
            secrets.choice(digits),
            secrets.choice(symbols)
        ]
        
        # Fill the rest with random characters from all sets
        all_chars = lowercase + uppercase + digits + symbols
        password.extend(secrets.choice(all_chars) for _ in range(length - 4))
        
        # Shuffle the password
        password_list = list(password)
        secrets.SystemRandom().shuffle(password_list)
        
        return ''.join(password_list)
    
    def change_password_helper(self, email: str):
        """Helper to change password for a Google account."""
        if email not in self.accounts:
            console.print(f"[red]Account {email} not found in registered accounts.[/red]")
            return
        
        # Generate a secure password
        password = self.generate_secure_password()
        
        # Display the generated password
        console.print("\n[bold green]Generated Secure Password:[/bold green]")
        password_syntax = Syntax(password, "text", theme="monokai")
        console.print(password_syntax)
        
        # Copy to clipboard if possible
        try:
            import pyperclip
            pyperclip.copy(password)
            console.print("[green]✓ Password copied to clipboard[/green]")
        except ImportError:
            console.print("[yellow]Install 'pyperclip' to auto-copy passwords: pip install pyperclip[/yellow]")
        except Exception:
            console.print("[yellow]Could not copy to clipboard. Please copy manually.[/yellow]")
        
        # Instructions
        console.print("\n[bold]Next Steps:[/bold]")
        console.print("1. Copy the password above")
        console.print("2. Click the link below to open Google's password change page")
        console.print("3. Sign in with your current password")
        console.print("4. Paste the new password and confirm")
        
        # Ask if user wants to open the password change page
        if Confirm.ask("\nOpen Google's password change page in your browser?"):
            password_change_url = "https://myaccount.google.com/security"
            try:
                webbrowser.open(password_change_url)
                console.print(f"[green]✓ Opened {password_change_url}[/green]")
            except Exception as e:
                console.print(f"[red]Could not open browser: {e}[/red]")
                console.print(f"Please manually visit: {password_change_url}")
        
        console.print("\n[bold yellow]Important:[/bold yellow]")
        console.print("• Keep this password secure and don't share it")
        console.print("• Consider using a password manager for better security")
        console.print("• You may need to update other devices/apps that use this account")
    
    def get_account_by_number(self, number: int) -> Optional[str]:
        """Get email address by account number."""
        accounts_list = list(self.accounts.keys())
        if 1 <= number <= len(accounts_list):
            return accounts_list[number - 1]
        return None


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description='Gmail Multi-Account CLI Tool')
    parser.add_argument('--list', action='store_true', help='List all registered accounts')
    parser.add_argument('--add', help='Add a new Gmail account')
    parser.add_argument('--remove', help='Remove a Gmail account')
    parser.add_argument('--send-test', help='Send test email to specified address from all accounts')
    parser.add_argument('--change-password', help='Generate secure password and open Google password change page for specified account (use number or email)')
    
    args = parser.parse_args()
    
    cli = GmailMultiAccountCLI()
    
    # Handle command line arguments
    if args.list:
        cli.list_accounts()
        return
    
    if args.add:
        cli.authenticate_account(args.add)
        return
    
    if args.remove:
        cli.remove_account(args.remove)
        return
    
    if args.send_test:
        cli.send_test_from_all_accounts(args.send_test)
        return
    
    if args.change_password:
        # Check if it's a number or email
        try:
            account_number = int(args.change_password)
            email = cli.get_account_by_number(account_number)
            if email:
                cli.change_password_helper(email)
            else:
                console.print(f"[red]Invalid account number. Please choose between 1 and {len(cli.accounts)}.[/red]")
                if cli.accounts:
                    cli.list_accounts(show_numbers=True)
        except ValueError:
            # Treat as email address
            cli.change_password_helper(args.change_password)
        return
    
    # Interactive mode
    console.print(Panel.fit(
        "[bold blue]Gmail Multi-Account CLI Tool[/bold blue]\n"
        "Manage multiple Gmail accounts and send test emails",
        title="Welcome"
    ))
    
    while True:
        console.print("\n[bold]Options:[/bold]")
        console.print("1. List accounts")
        console.print("2. Add account")
        console.print("3. Remove account")
        console.print("4. Send test email from all accounts")
        console.print("5. Change password helper")
        console.print("6. Exit")
        
        choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4", "5", "6"])
        
        if choice == "1":
            cli.list_accounts()
        
        elif choice == "2":
            email = Prompt.ask("Enter Gmail address")
            cli.authenticate_account(email)
        
        elif choice == "3":
            if not cli.accounts:
                console.print("[yellow]No accounts to remove.[/yellow]")
                continue
            
            cli.list_accounts()
            email = Prompt.ask("Enter email to remove")
            if email in cli.accounts:
                if Confirm.ask(f"Are you sure you want to remove {email}?"):
                    cli.remove_account(email)
            else:
                console.print(f"[red]Account {email} not found.[/red]")
        
        elif choice == "4":
            if not cli.accounts:
                console.print("[yellow]No accounts registered. Please add accounts first.[/yellow]")
                continue
            
            to_email = Prompt.ask("Enter recipient email address")
            cli.send_test_from_all_accounts(to_email)
        
        elif choice == "5":
            if not cli.accounts:
                console.print("[yellow]No accounts registered. Please add accounts first.[/yellow]")
                continue
            
            cli.list_accounts(show_numbers=True)
            try:
                account_number = int(Prompt.ask("Enter account number for password change"))
                email = cli.get_account_by_number(account_number)
                if email:
                    cli.change_password_helper(email)
                else:
                    console.print(f"[red]Invalid account number. Please choose between 1 and {len(cli.accounts)}.[/red]")
            except ValueError:
                console.print("[red]Please enter a valid number.[/red]")
        
        elif choice == "6":
            console.print("[green]Goodbye![/green]")
            break


if __name__ == "__main__":
    main()
