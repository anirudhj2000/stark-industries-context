---
name: process-answer-media
description: Process media attachments (audio, video, image, document) in Q&A responses and extract text content
---

# Process Answer Media

You are about to process media attachments submitted as answers to Q&A questions.

## Arguments

This command receives two file path arguments:
- **First argument**: Path to manifest JSON file (contains organization info and Playbook API credentials)
- **Second argument**: Path to payload JSON file (contains response_id, question_id, media_urls, callback_url)

## Your Task

1. **Read the manifest and payload** from the file paths provided as arguments to this command

2. **Use the process-answer-media skill** to:
   - Identify media type (audio, video, image, document)
   - Extract text content using appropriate transcription engine
   - Clean up transcription with vocabulary normalization
   - **Return structured JSON output** (handler sends webhook)

3. **Follow the skill workflow exactly** - The skill contains all the intelligence and steps

## Command

```bash
# Invoke the skill
Use the skill: process-answer-media
```

## Important Notes

- **All intelligence is in the skill** - This command just tells you to use it
- **Return structured JSON** - The handler receives your output and sends the webhook
- **Do NOT send webhooks yourself** - Just return the JSON output matching the schema
- **No manual intervention** - The entire workflow is automated
- **response_id is REQUIRED** - Must be included in JSON output

## Success Criteria

- Media processed and text content extracted
- Valid JSON returned matching the output schema with response_id and text_content
- Handler sends webhook callback to Playbook
