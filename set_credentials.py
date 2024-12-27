#!/usr/bin/env python3
import os
import sys
import getpass
import argparse

def set_credentials(username=None, password=None):
    """Set Instagram credentials either from arguments or interactive input"""
    print("Setting up Instagram credentials...")
    
    if username is None:
        username = input("Enter Instagram username: ")
    if password is None:
        password = getpass.getpass("Enter Instagram password: ")
    
    # Write to .env file
    with open('.env', 'w') as f:
        f.write(f'INSTAGRAM_USERNAME={username}\n')
        f.write(f'INSTAGRAM_PASSWORD={password}\n')
    
    print("\nCredentials saved to .env file.")
    print("Please restart the application for changes to take effect.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Set Instagram credentials')
    parser.add_argument('--username', '-u', help='Instagram username')
    parser.add_argument('--password', '-p', help='Instagram password')
    
    args = parser.parse_args()
    
    try:
        set_credentials(args.username, args.password)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)
