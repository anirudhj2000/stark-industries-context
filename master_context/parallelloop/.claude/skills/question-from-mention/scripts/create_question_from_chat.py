#!/usr/bin/env python3
"""
Create Q&A question from chat @-mention.

DETERMINISTIC SCRIPT - No intelligence here.
All brainstorming/refinement happens in the skill conversation.
This just POSTs the final data to Playbook API.

Usage:
    python3 create_question_from_chat.py \
        --question-text "Your refined question here" \
        --assignee-ids "uuid1,uuid2" \
        --organization-id "org-uuid" \
        --project-id "proj-uuid" \
        --mentioned-by "user-uuid" \
        --conversation-id "conv-uuid"

Output (JSON to stdout):
    {"success": true, "question_id": "q-123", "assignees": [...]}
    {"success": false, "error": "..."}

Environment variables (set by Agent SDK):
    PLAYBOOK_API_URL: Base URL for Playbook API
    INTER_SERVICE_API_KEY: API key for service-to-service auth
"""

import argparse
import json
import os
import sys

import requests


def main():
    parser = argparse.ArgumentParser(
        description="Create Q&A question from chat @-mention"
    )
    parser.add_argument(
        "--question-text",
        required=True,
        help="The refined question text to create"
    )
    parser.add_argument(
        "--assignee-ids",
        required=True,
        help="Comma-separated UUIDs of assignees"
    )
    parser.add_argument(
        "--organization-id",
        required=True,
        help="Organization UUID"
    )
    parser.add_argument(
        "--project-id",
        default="",
        help="Project UUID (optional, uses default project if not provided)"
    )
    parser.add_argument(
        "--mentioned-by",
        required=True,
        help="UUID of user who mentioned the team members"
    )
    parser.add_argument(
        "--conversation-id",
        required=True,
        help="Conversation UUID for tracking"
    )
    parser.add_argument(
        "--question-type",
        default="clarification",
        help="Question type (default: clarification)"
    )
    parser.add_argument(
        "--context-items",
        default="",
        help="Comma-separated source/artifact IDs for context"
    )
    args = parser.parse_args()

    # Get config from environment (set by Agent SDK)
    # Try PLAYBOOK_API_URL first, fall back to PLAYBOOK_WEBHOOK_BASE_URL (Agent SDK standard)
    api_url = (
        os.environ.get("PLAYBOOK_API_URL")
        or os.environ.get("PLAYBOOK_WEBHOOK_BASE_URL")
        or ""
    ).rstrip("/")
    api_key = os.environ.get("INTER_SERVICE_API_KEY", "")

    if not api_url:
        print(json.dumps({
            "success": False,
            "error": "Missing PLAYBOOK_API_URL or PLAYBOOK_WEBHOOK_BASE_URL environment variable"
        }))
        sys.exit(1)

    if not api_key:
        print(json.dumps({
            "success": False,
            "error": "Missing INTER_SERVICE_API_KEY environment variable"
        }))
        sys.exit(1)

    # Parse comma-separated values
    assignee_ids = [x.strip() for x in args.assignee_ids.split(",") if x.strip()]
    context_items = (
        [x.strip() for x in args.context_items.split(",") if x.strip()]
        if args.context_items
        else []
    )

    if not assignee_ids:
        print(json.dumps({
            "success": False,
            "error": "At least one assignee required"
        }))
        sys.exit(1)

    # Build payload for Playbook API
    payload = {
        "text": args.question_text,
        "assignee_ids": assignee_ids,
        "question_type": args.question_type,
        "context": {
            "conversation_id": args.conversation_id,
            "mentioned_by": args.mentioned_by,
            "context_items": context_items,
        },
        "routing_metadata": {
            "source": "chat_mention",
            "skill": "question-from-mention",
        },
        "conversation_id": args.conversation_id,
    }

    # Add project_id if provided
    if args.project_id:
        payload["project_id"] = args.project_id

    # POST to Playbook
    endpoint = f"{api_url}/api/v1/context/questions/from-chat/"
    # SSL verification - disable for local dev with mkcert
    ssl_verify = os.environ.get("SSL_VERIFY", "true").lower() != "false"

    try:
        resp = requests.post(
            endpoint,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "X-API-Key": api_key,
                "X-Organization-ID": args.organization_id,
            },
            timeout=30,
            verify=ssl_verify,
        )

        if resp.status_code == 201:
            data = resp.json()
            # Handle both APIResponse wrapper and direct response
            result_data = data.get("data", data)
            print(json.dumps({
                "success": True,
                "question_id": result_data.get("question_id"),
                "assignees": result_data.get("assignees", []),
            }))
        else:
            # Try to extract error message from response
            try:
                error_data = resp.json()
                error_msg = (
                    error_data.get("message")
                    or error_data.get("error")
                    or error_data.get("detail")
                    or resp.text[:200]
                )
            except Exception:
                error_msg = f"HTTP {resp.status_code}: {resp.text[:200]}"

            print(json.dumps({
                "success": False,
                "error": error_msg
            }))
            sys.exit(1)

    except requests.exceptions.Timeout:
        print(json.dumps({
            "success": False,
            "error": "Request timed out after 30 seconds"
        }))
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(json.dumps({
            "success": False,
            "error": f"Request failed: {str(e)}"
        }))
        sys.exit(1)


if __name__ == "__main__":
    main()
