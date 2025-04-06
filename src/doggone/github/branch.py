# pylint: disable=broad-exception-caught
'''Work with branch resources'''
import time
import click
from git import Repo

main_branch = 'main'

def create_feature_branch(local_repo_path, resource_name):
    """
    Create a new feature branch for the imported resource.
    
    Args:
        local_repo_path: Path to the Git repository
        resource_name: Name of the imported resource
    
    Returns:
        Branch name
    """
    # Open the repository
    repo = Repo(local_repo_path)

    # Make sure we're on the main branch and up to date
    try:
        repo.git.checkout(main_branch)
        repo.git.pull()
    except Exception as e:
        click.echo(f"Warning: Could not update main branch: {e}")

    # Create a new branch with a timestamp
    timestamp = time.strftime("%Y%m%d%H%M%S")
    branch_name = f"import/{resource_name}-{timestamp}"

    try:
        repo.git.checkout('-b', branch_name)
        click.echo(f"Created new branch: {branch_name}")
        return branch_name
    except Exception as e:
        click.echo(f"Error creating branch: {e}")
        return None

def commit_changes(local_repo_path, resource_type, resource_name):
    """
    Commit the changes to the feature branch.
    
    Args:
        local_repo_path: Path to the Git repository
        resource_type: Type of imported resource
        resource_name: Name of the imported resource
    
    Returns:
        Success status
    """
    repo = Repo(local_repo_path)

    # Check if __main__.py has changes
    try:
        repo.git.add('__main__.py')

        commit_message = f"Import {resource_type} resource: {resource_name}\n\n" \
                         f"Imported existing {resource_type} '{resource_name}' into Pulumi state"

        repo.git.commit('-m', commit_message)
        repo.git.push('--set-upstream', 'origin', repo.active_branch.name)

        # Once complete, return to main branch
        repo.git.checkout(main_branch)
        repo.git.pull()

        return True
    except Exception as e:
        click.echo(f"Error committing changes: {e}")
        return False
