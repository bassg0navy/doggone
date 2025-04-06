#!/usr/bin/env python3
# pylint: disable=broad-exception-caught

'''CLI tool to import infrastructure into Pulumi state'''
import os
import json
import click
from pulumi import automation as auto
import oci
from .importer.base import import_infra
from .code_gen.file_ops import add_resource_to_main_file
from .github.pr import create_pull_request
from .github.branch import create_feature_branch, commit_changes
from .utils.auth import github_auth_check, pulumi_auth_check, get_pulumi_config

# OCI Configuration
oci_config = oci.config.from_file(profile_name='TERRAFORM')
compartment_id = oci_config.get('tenancy')
namespace = oci_config.get('namespace')

@click.group()
def cli():
    """Pulumi GitHub resource importer CLI tool."""

@cli.command('context')
@click.option('--project', help='Pulumi project name')
@click.option('--stack', default='dev', help='Pulumi stack name; dev used by default')
@click.option('--git-repo', help='Remote git repo to use. Ex: username/repo-name')
def configure_pulumi(project, stack, git_repo):
    """
    Configure Pulumi project and stack context for doggone to use.
    
    This saves configuration to a local file that will be used by other commands.
    """
    config_dir = os.path.expanduser("~/.doggone")
    config_file = os.path.join(config_dir, "config.json")

    # Create config directory if it doesn't exist
    os.makedirs(config_dir, exist_ok=True)

    # Read existing config if any
    config = {}
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            click.echo(f"Error reading config: {e}")

    # Update config with new values
    if project:
        config['pulumi_project'] = project
    elif 'pulumi_project' not in config:
        config['pulumi_project'] = click.prompt("Enter Pulumi project name")

    if stack:
        config['pulumi_stack'] = stack
    elif 'pulumi_stack' not in config:
        config['pulumi_stack'] = click.prompt("Enter Pulumi stack name")

    if git_repo:
        config['git_repo'] = git_repo
    elif 'pulumi_stack' not in config:
        config['git_repo'] = click.prompt("Enter Pulumi stack name")

    # Save config
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        click.echo(
            f"\nConfiguration saved: project={project}, stack={stack}, repo={git_repo}"
        )
    except Exception as e:
        click.echo(f"Error saving configuration: {e}")

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
@click.option('--file',
    default="__main__.py",
    help='Target Python file to add the resource code to'
)
@click.option('--local-repo-path',
     default='.', help='Path to the Pulumi project repository.'
)
def resource_import(
    resource_type, resource_name, resource_id, file, local_repo_path):
    '''
    Corral resources into state using Pulumi automation and GitHub API
    '''
    authenticated_to_github = github_auth_check()
    authenticated_to_pulumi = pulumi_auth_check()


    if not (authenticated_to_github and authenticated_to_pulumi):
        click.echo('User authentication failed! Please check your credentials.')
        return

    # Define wrapper to format parameters to send to import_infra function
    # Called by stack program
    def program_wrapper():
        return import_infra(resource_type, resource_name, resource_id, namespace, compartment_id)

    # Core import logic leveraging the automation and GitHub providers goes here
    try:
        project_name, stack_name, git_repo = get_pulumi_config()

        stack = auto.create_or_select_stack(
            stack_name=stack_name,
            project_name=project_name,
            program=program_wrapper # program requires lambda style callable w/o parameters
        )

        # Capture the standard output during the operation
        stack.up(on_output=lambda msg: click.echo(msg)) # pylint: disable=unnecessary-lambda
        click.echo(f"\nSuccessfully imported {resource_type}: {resource_name}!")

        # Get resource properties from the import result
        properties = {
            "name": resource_name,
            "compartment_id": compartment_id,
            "namespace": namespace,
            # Add other properties as needed
        }
        # Log success of updating main file
        # pylint: disable-next=unused-variable
        _, message = add_resource_to_main_file(
            resource_type,
            resource_name,
            properties,
            local_repo_path,
            file
        )
        click.echo(message)

        # Create branch
        click.echo("Creating feature branch...")
        branch_name = create_feature_branch(local_repo_path, resource_name)
        if not branch_name:
            click.echo("Failed to create feature branch. PR creation aborted.")
            return

        # Commit changes
        click.echo("Committing changes...")
        if not commit_changes(local_repo_path, resource_type, resource_name):
            click.echo("Failed to commit changes. PR creation aborted.")
            return

        # Create pull request
        click.echo("Creating pull request...")
        pr_url, _ = create_pull_request(
            git_repo, branch_name, resource_type, resource_name, id
        )
        if pr_url:
            click.echo(f"Import complete! Review and merge the PR: {pr_url}")


    except Exception as e:
        click.echo(f"Error importing repositories: {e}")

## Add support of additional functionality

if __name__ == '__main__':
    cli()
