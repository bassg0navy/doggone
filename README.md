# doggone
Doggone is a cli tool to corral one-off resources into state with the remaining cattle. It leverages Pulumi's automation API and GitHub provider. ![](/images/doggone_logo.png)

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
Import with GitHub Integration
```
doggone import --resource-type bucket --id my-bucket --name my_bucket --create-pr --github-repo username/repo
```

![PR Created w/ Template](/images/pr_creation.png)

## Disclaimers
**WARNING: This repository does not follow all best practices and should not be used in a production environment.** It is more/less a demonstration of a strong use-case for Pulumi's automation API and fairly stout GitHub integration.
