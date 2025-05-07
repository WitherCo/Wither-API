#!/usr/bin/env python3
import os
import subprocess
import sys

def push_to_github():
    """Push code to GitHub repository."""
    try:
        # Set up git configuration
        subprocess.run(['git', 'init'], check=True)
        subprocess.run(['git', 'config', 'user.email', 'wither@witherco.xyz'], check=True)
        subprocess.run(['git', 'config', 'user.name', 'WitherCo'], check=True)
        
        # Add and commit files
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit for Wither API Gateway'], check=True)
        
        # Set up remote and push
        subprocess.run(['git', 'remote', 'add', 'origin', 'https://github.com/WitherCo/Wither-API.git'], check=True)
        subprocess.run(['git', 'branch', '-M', 'main'], check=True)
        subprocess.run(['git', 'push', '-u', 'origin', 'main'], check=True)
        
        print("\n==================================================")
        print("GitHub Repository Push Complete!")
        print("==================================================")
        print("Repository URL: https://github.com/WitherCo/Wither-API")
        print("Next steps:")
        print("1. Set up your witherco.xyz domain by following instructions in CUSTOM_DOMAIN_SETUP.md")
        print("2. Deploy your API Gateway using instructions in DEPLOYMENT_GUIDE.md")
        print("3. Update your API documentation with your specific endpoints and authentication")
        print("==================================================")
        
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Pushing Wither-API to GitHub repository...")
    push_to_github()