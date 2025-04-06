# pylint: disable=broad-exception-caught
'''Holds functions related to user authentication'''
import os
import json
import subprocess

def github_auth_check():
    '''Verify user is authenticated to GitHub'''

    # First check if token is exported as environment variable
    if os.environ.get('GITHUB_TOKEN'):
        return True

    # If not, check Pulumi config for token information
    result = subprocess.run(
        ['pulumi', 'config', 'get', 'github:token'],
        capture_output=True,
        check=False, # Don't raise error if process fails; return code handled below
        text=True
    )
    # Return true if config contains value
    if result.returncode == 0 and result.stdout.strip():
        return True

    # Default return if previous methods unsuccessful
    return False

def pulumi_auth_check():
    '''Check if user is authenticated to Pulumi'''
    result = subprocess.run(
        ['pulumi', 'whoami'],
        capture_output=True,
        text=True,
        check=False
    )

    if result.returncode != 0:
        return False
    else:
        return True

def get_pulumi_config():
    """Get Pulumi configuration from doggone config file."""
    config_file = os.path.expanduser("~/.doggone/config.json")

    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return (
                    config.get('pulumi_project'),
                    config.get('pulumi_stack'),
                    config.get('git_repo')
                )
        except Exception:
            pass

    return None, None
