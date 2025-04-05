#!/usr/bin/env python3
# pylint: disable=broad-exception-caught

'''CLI tool to import infrastructure into Pulumi state'''
import os
import subprocess

import click
from pulumi import automation as auto
import oci
from .importer.base import import_infra
from .code_gen.file_ops import add_resource_to_main_file

# Configuration
oci_config = oci.config.from_file(profile_name='TERRAFORM')
compartment_id = oci_config.get('tenancy')
namespace = oci_config.get('namespace')

def auth_check():
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

@click.group()
def cli():
    """Pulumi GitHub resource importer CLI tool."""

## Import Support
@cli.command('import')
@click.option('--resource-type',
    help='What is being imported? (bucket, compute instance, etc.)'
)
@click.option('--resource-id',
    help='ID of the resource to import (i.e. OCID, ARN, etc.)'
)
@click.option('--resource-name',
    help='Local name of resource to use within code'
)
@click.option('--add-to-code',
    is_flag=True, default=True,
    help='Add the imported resource to __main__.py'
)
@click.option('--file',
    default="__main__.py",
    help='Target Python file to add the resource code to'
)
@click.option('--create-pr',
    is_flag=True, help='Create a pull request for the imported resource.'
)
@click.option('--repo-path',
     default='.', help='Path to the Pulumi project repository.'
)
@click.option(
    '--github-repo', help='GitHub repository name (e.g., "username/repo").'
)
def resource_import(
    resource_type, resource_name, resource_id, file, repo_path, github_repo,
    add_to_code=True
):
    '''
    Corral resources into state using Pulumi automation API
    '''
    user_authenticated = auth_check()

    if not user_authenticated:
        click.echo('User authentication failed! Please check your credentials.')
        return

    # Define wrapper to format parameters to send to import_infra function
    # Called by stack program
    def program_wrapper():
        return import_infra(resource_type, resource_name, resource_id, namespace, compartment_id)

    # Core import logic leveraging the automation and GitHub providers goes here
    try:
        stack = auto.create_or_select_stack(
            stack_name="dev",
            project_name="pulumi_infra",
            program=program_wrapper # program requires lambda style callable w/o parameters
        )

        # Capture the standard output during the operation
        stack.up(on_output=lambda msg: click.echo(msg)) # pylint: disable=unnecessary-lambda
        click.echo(f"\nSuccessfully imported {resource_type}: {resource_name}!")

        if add_to_code:
            # Get resource properties from the import result
            properties = {
                "name": resource_name,
                "compartment_id": compartment_id,
                "namespace": namespace,
                # Add other properties as needed
            }
            # Log success of updating main file
            # pylint: disable-next=unused-variable
            success, message = add_resource_to_main_file(
                resource_type,
                resource_name,
                properties,
                file
            )
            click.echo(message)

            # Create branch


    except Exception as e:
        click.echo(f"Error importing repositories: {e}")

## Add support of additional functionality

if __name__ == '__main__':
    cli()
