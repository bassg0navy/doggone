<p align="center" width="100%">
    <img width="66%" src="https://raw.githubusercontent.com/bassg0navy/doggone/main/images/doggone_large_rectangle.png">
</p>

# doggone
Doggone is a cli tool to corral one-off infrastructure resources back into state with the rest of the heard. It leverages Pulumi's automation API and GitHub provider. 


## Why Doggone?
Sure, "Operation: Click-Ops" achieves the same goal. However, resource imports can be tedious, error-prone, and often lack proper _(if any)_ documentation. Doggone solves these challenges with:
+ Automated Code Generation: Add well-formatted code to your Pulumi files
+ GitHub Integration: Create feature branches and pull requests for each import
+ Audit Trail: Document _who_ imported _what_ and _when_ with detailed PRs


# Installation
### Prerequisites
+ Python 3.8 or higher
+ Pulumi CLI
+ Git
+ GitHub personal access token (for PR creation)

### Clone the repository
```
git clone https://github.com/yourusername/doggone.git
cd doggone
```

### Create a virtual environment
```
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Install the package in development mode
```
pip install -e .
```

### Set up GitHub authentication
```
export GITHUB_TOKEN=your_github_token
```


# Usage
Configure doggone
```
doggone context --project <pulumi project name> --stack <pulumi stack name: defaults to 'dev'> --git-repo <username/repo-name>
```

Import with GitHub integration
```
doggone import --resource-type <bucket> --resource-name <resource name> --resource-id <OCID, ARN, etc.> --file <__main__.py>
```

Successful PR creation
![PR Created w/ Template](/images/pr_creation.png)

Successful Pulumi stack update
![PR Created w/ Template](/images/pulumi_update.png)

## Disclaimers
**WARNING: This repository does not follow all best practices and should not be used in a production environment.** It is more/less a demonstration of a strong use-case for Pulumi's automation API and fairly stout GitHub integration. It does not account for a plethora of important concerns:
+ Multi-cloud: OCI (Oracle Cloud Infrastructure) is the only supported provider
+ Variety of languages: supports infra code written in Python only
+ Resource types: supports import of object storage buckets only
