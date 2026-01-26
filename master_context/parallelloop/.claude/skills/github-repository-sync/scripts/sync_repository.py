#!/usr/bin/env python3
"""
GitHub Repository Sync Script

Syncs a GitHub repository (clone or pull) using an access token for authentication.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


def parse_repo_url(repo_url: str) -> tuple[str, str]:
    """
    Parse GitHub repository URL to extract owner and repo name.

    Args:
        repo_url: GitHub repository URL (e.g., https://github.com/owner/repo or https://github.com/owner/repo.git)

    Returns:
        Tuple of (owner, repo_name)
    """
    # Remove .git suffix if present
    repo_url = repo_url.rstrip('/')
    if repo_url.endswith('.git'):
        repo_url = repo_url[:-4]

    # Extract owner and repo from URL
    # Supports: https://github.com/owner/repo or github.com/owner/repo
    pattern = r'(?:https?://)?(?:www\.)?github\.com/([^/]+)/([^/]+)'
    match = re.match(pattern, repo_url)

    if not match:
        raise ValueError(f"Invalid GitHub repository URL: {repo_url}")

    owner = match.group(1)
    repo_name = match.group(2)

    return owner, repo_name


def construct_authenticated_url(owner: str, repo_name: str, access_token: str) -> str:
    """
    Construct authenticated GitHub clone URL.

    Args:
        owner: Repository owner
        repo_name: Repository name
        access_token: GitHub access token

    Returns:
        Authenticated clone URL
    """
    return f"https://x-access-token:{access_token}@github.com/{owner}/{repo_name}.git"


def clone_repository(
    repo_url: str,
    access_token: str,
    sync_path: str,
    branch: str = None
) -> dict:
    """
    Clone GitHub repository with authentication.

    Args:
        repo_url: Repository URL
        access_token: GitHub App installation access token
        sync_path: Local path to clone repository
        branch: Optional specific branch to clone

    Returns:
        {
            "sync_path": "...",
            "commit_sha": "...",
            "branch": "...",
            "owner": "...",
            "repo_name": "...",
            "operation": "clone",
            "commits_pulled": 0
        }
    """
    # Parse repository URL
    owner, repo_name = parse_repo_url(repo_url)

    # Construct authenticated URL
    authenticated_url = construct_authenticated_url(owner, repo_name, access_token)

    # Prepare sync path
    sync_path_obj = Path(sync_path)
    sync_path_obj.parent.mkdir(parents=True, exist_ok=True)

    # Check if directory already exists
    if sync_path_obj.exists():
        raise FileExistsError(f"Sync path already exists: {sync_path}")

    # Build git clone command
    cmd = ["git", "clone"]
    if branch:
        cmd.extend(["--branch", branch])
    cmd.extend([authenticated_url, str(sync_path_obj)])

    try:
        # Execute git clone
        print(f"Cloning {owner}/{repo_name}...", file=sys.stderr)
        subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout for large repos
        )

        print(f"Repository cloned successfully", file=sys.stderr)

        # Get latest commit SHA
        result = subprocess.run(
            ["git", "-C", str(sync_path_obj), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True
        )
        commit_sha = result.stdout.strip()

        # Get current branch
        result = subprocess.run(
            ["git", "-C", str(sync_path_obj), "rev-parse", "--abbrev-ref", "HEAD"],
            check=True,
            capture_output=True,
            text=True
        )
        current_branch = result.stdout.strip()

        return {
            "sync_path": str(sync_path_obj.absolute()),
            "commit_sha": commit_sha,
            "branch": current_branch,
            "owner": owner,
            "repo_name": repo_name,
            "operation": "clone",
            "commits_pulled": 0
        }

    except subprocess.TimeoutExpired:
        raise Exception(f"Git clone timed out after 5 minutes. Repository may be too large or network is slow.")
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else str(e)
        # Sanitize error message to avoid leaking token
        error_msg = error_msg.replace(access_token, "***")
        raise Exception(f"Git clone failed: {error_msg}")
    except Exception as e:
        raise Exception(f"Unexpected error during clone: {e}")


def pull_repository(
    repo_url: str,
    access_token: str,
    sync_path: str,
    branch: str = None
) -> dict:
    """
    Pull updates for an existing GitHub repository.

    Args:
        repo_url: Repository URL
        access_token: GitHub App installation access token
        sync_path: Local path to existing repository
        branch: Optional specific branch to pull

    Returns:
        {
            "sync_path": "...",
            "commit_sha": "...",
            "branch": "...",
            "owner": "...",
            "repo_name": "...",
            "operation": "pull",
            "commits_pulled": N
        }
    """
    # Parse repository URL
    owner, repo_name = parse_repo_url(repo_url)

    # Construct authenticated URL
    authenticated_url = construct_authenticated_url(owner, repo_name, access_token)

    sync_path_obj = Path(sync_path)

    # Verify repository exists
    if not sync_path_obj.exists():
        raise FileNotFoundError(f"Repository path does not exist: {sync_path}")

    git_dir = sync_path_obj / ".git"
    if not git_dir.exists():
        raise ValueError(f"Path is not a git repository: {sync_path}")

    try:
        # Get commit SHA before pull
        result = subprocess.run(
            ["git", "-C", str(sync_path_obj), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True
        )
        before_sha = result.stdout.strip()

        # Configure remote URL with authentication
        print(f"Updating remote URL with authentication...", file=sys.stderr)
        subprocess.run(
            ["git", "-C", str(sync_path_obj), "remote", "set-url", "origin", authenticated_url],
            check=True,
            capture_output=True,
            text=True
        )

        # Fetch all updates
        print(f"Fetching updates for {owner}/{repo_name}...", file=sys.stderr)
        subprocess.run(
            ["git", "-C", str(sync_path_obj), "fetch", "--all"],
            check=True,
            capture_output=True,
            text=True,
            timeout=300
        )

        # Pull updates
        print(f"Pulling updates...", file=sys.stderr)
        pull_cmd = ["git", "-C", str(sync_path_obj), "pull"]
        if branch:
            pull_cmd.extend(["origin", branch])

        subprocess.run(
            pull_cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=300
        )

        print(f"Repository updated successfully", file=sys.stderr)

        # Get commit SHA after pull
        result = subprocess.run(
            ["git", "-C", str(sync_path_obj), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True
        )
        after_sha = result.stdout.strip()

        # Count commits pulled
        commits_pulled = 0
        if before_sha != after_sha:
            result = subprocess.run(
                ["git", "-C", str(sync_path_obj), "rev-list", "--count", f"{before_sha}..{after_sha}"],
                check=True,
                capture_output=True,
                text=True
            )
            commits_pulled = int(result.stdout.strip())

        # Get current branch
        result = subprocess.run(
            ["git", "-C", str(sync_path_obj), "rev-parse", "--abbrev-ref", "HEAD"],
            check=True,
            capture_output=True,
            text=True
        )
        current_branch = result.stdout.strip()

        return {
            "sync_path": str(sync_path_obj.absolute()),
            "commit_sha": after_sha,
            "branch": current_branch,
            "owner": owner,
            "repo_name": repo_name,
            "operation": "pull",
            "commits_pulled": commits_pulled
        }

    except subprocess.TimeoutExpired:
        raise Exception(f"Git pull timed out after 5 minutes. Network may be slow.")
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else str(e)
        # Sanitize error message to avoid leaking token
        error_msg = error_msg.replace(access_token, "***")
        raise Exception(f"Git pull failed: {error_msg}")
    except Exception as e:
        raise Exception(f"Unexpected error during pull: {e}")


def sync_repository(
    repo_url: str,
    access_token: str,
    sync_path: str,
    operation: str,
    branch: str = None
) -> dict:
    """
    Sync GitHub repository (clone or pull based on operation).

    Args:
        repo_url: Repository URL
        access_token: GitHub App installation access token
        sync_path: Local path to sync repository
        operation: "clone" or "pull"
        branch: Optional specific branch

    Returns:
        Sync result dictionary
    """
    if operation == "clone":
        return clone_repository(repo_url, access_token, sync_path, branch)
    elif operation == "pull":
        return pull_repository(repo_url, access_token, sync_path, branch)
    else:
        raise ValueError(f"Invalid operation: {operation}. Must be 'clone' or 'pull'.")


def main():
    parser = argparse.ArgumentParser(
        description="Sync GitHub repository (clone or pull) with access token authentication"
    )
    parser.add_argument(
        "--repo-url",
        required=True,
        help="GitHub repository URL (e.g., https://github.com/owner/repo)"
    )
    parser.add_argument(
        "--access-token",
        required=True,
        help="GitHub access token for authentication"
    )
    parser.add_argument(
        "--sync-path",
        required=True,
        help="Local path to sync repository"
    )
    parser.add_argument(
        "--operation",
        required=True,
        choices=["clone", "pull"],
        help="Operation to perform: clone (new repo) or pull (update existing)"
    )
    parser.add_argument(
        "--branch",
        help="Specific branch to sync (optional)"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output file path for sync result JSON"
    )

    args = parser.parse_args()

    try:
        # Sync repository
        sync_result = sync_repository(
            repo_url=args.repo_url,
            access_token=args.access_token,
            sync_path=args.sync_path,
            operation=args.operation,
            branch=args.branch
        )

        # Write to output file
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(sync_result, f, indent=2)

        print(f"Sync metadata written to: {args.output}", file=sys.stderr)
        print(f"Repository at: {sync_result['sync_path']}", file=sys.stderr)
        print(f"Operation: {sync_result['operation']}", file=sys.stderr)
        print(f"Branch: {sync_result['branch']}", file=sys.stderr)
        print(f"Commit: {sync_result['commit_sha']}", file=sys.stderr)
        if sync_result['operation'] == 'pull':
            print(f"Commits pulled: {sync_result['commits_pulled']}", file=sys.stderr)

        # Also output to stdout for piping
        print(json.dumps(sync_result))

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
