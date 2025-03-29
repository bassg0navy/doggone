import click
import pulumi
import pulumi_github as github
import pulumi_oci as oci

@click.command()
@click.option('--username', help='Username to log in to your repository with.')

def login(username):
    '''Logs user into repository/cloud provider'''
    click.echo(username)
    
if __name__ == '__main__':
    login()