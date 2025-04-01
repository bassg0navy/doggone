#!/usr/bin/env python3
# pylint: disable=broad-exception-caught

'''CLI tool to import infrastructure into Pulumi state'''
import os
import subprocess

import click
import pulumi
# import pulumi_github as github
from pulumi import automation as auto
import pulumi_oci
import oci

# Configuration
oci_config = oci.config.from_file(profile_name='TERRAFORM')
compartment_id = oci_config.get('tenancy')
namespace = oci_config.get('namespace')

# First determine if user authenticated to GitHub
def auth_check():
    '''Determine if authentication values are set up appropriately'''

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

def import_infra(resource_type, resource_name, resource_id):
    '''Pulumi program to import resource into state'''
    resource_types = {
        "bucket": pulumi_oci.objectstorage.Bucket,
        "identity_policy": pulumi_oci.identity.Policy,
        # Add other resource types as needed
    }
    # Get resource class using resource type parameter passed to function
    resource_class = resource_types.get(resource_type)
    if not resource_class:
        raise ValueError(f"Unsupported resource type: {resource_type}")

    # Build optional arguments to pass to resource when making call to auto API
    args = {}
    if resource_type == 'bucket':
        args = {
            "namespace": namespace,
            "metadata": {
                "Created-By": "Pulumi",
                "Purpose": "Infra Import Demo"
            },
            "storage_tier": "Standard",
            "versioning": "Enabled"
        }

    opts = pulumi.ResourceOptions(import_=resource_id)

    # Create resource object
    resource_class(resource_name,
        # Required parameters
        compartment_id=compartment_id,
        name=resource_name,
        # Optional parameters
        **args,
        opts=opts
    )

@click.group()
def cli():
    """Pulumi GitHub resource importer CLI tool."""

@cli.command('import')
@click.option('--resource-type', help='What is being imported? (bucket, compute instance, etc.)')
@click.option('--resource-id', help='ID of the resource to import (i.e. OCID, ARN, etc.)')
@click.option('--resource-name', help='Local name of resource to use within code')
def resource_import(resource_type, resource_name, resource_id):
    '''
    Shepherd wayward resources into state using Pulumi automation API
    '''
    user_authenticated = auth_check()

    if not user_authenticated:
        click.echo('User authentication failed! Please check your credentials.')
        return

    # Define wrapper to format parameters to send to import_infra function
    # Called by stack program
    def program_wrapper():
        return import_infra(resource_type, resource_name, resource_id)

    # Core import logic leveraging the automation and GitHub providers goes here
    try:
        stack = auto.create_or_select_stack(
            stack_name="dev",
            project_name="pulumi_infra",
            program=program_wrapper # program requires lambda style callable w/o parameters
        )

        # Capture the standard output during the operation
        stack.up(on_output=lambda msg: click.echo(msg)) # pylint: disable=unnecessary-lambda
        click.echo(f"Successfully imported {resource_type}")

    except Exception as e:
        click.echo(f"Error importing repositories: {e}")


if __name__ == '__main__':
    cli()
