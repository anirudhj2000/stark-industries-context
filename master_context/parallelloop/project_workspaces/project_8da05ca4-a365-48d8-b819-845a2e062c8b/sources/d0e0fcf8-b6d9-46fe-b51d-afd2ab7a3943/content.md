# TDD: Recall AI Meeting Bot Integration

**Version**: 1.0
**Date**: 2026-04-19
**Status**: Draft
**Based on**: Recall AI Meeting Bot — Implementation Plan (Phase 1 & 2)

---

## System Architecture

Recall AI is integrated as a **custom DIRECT integration** (not Composio) within Parallelloop's existing integration framework. The integration follows the same structural pattern as the Slack and GitHub custom integrations, plugging natively into:

- `integrations/custom/recall_ai/` — integration package
- `core/webhooks/` — InboundWebhook inbox for Svix events
- `context/` — Source creation, IngestionJob dispatch, and Agent SDK command routing
- `integrations/models.py` — `Integration` + `IntegrationConnection` for API key storage

### End-to-End Flow (Phase 1)

```
[User submits meeting URL in UI]
        │
        ▼
POST /api/v1/integrations/recall-ai/bots/
        │
        ▼
RecallAIService.create_bot(meeting_url, org_id, user_id, project_id)
  → POST https://{region}.recall.ai/api/v1/bot
  → Store RecallBot record (bot_id, metadata, status=joining)
        │
        ▼
Recall AI bot joins meeting (Zoom / Meet / Teams)
        │
[Meeting ends]
        │
        ▼
Recall → Svix webhook → POST /api/v1/integrations/recall-ai/webhooks/
  → InboundWebhook.objects.create(source="recall_ai", event_type="bot.done")
  → Return HTTP 200 immediately
  → process_inbound_webhook.delay(webhook_id)
        │
        ▼
Celery: handle_recall_bot_done(webhook)
  → GET /api/v1/bot/{bot_id}  [confirm done]
  → Download transcript via media_shortcuts.transcript.data.download_url
  → Upload transcript file to S3
  → SourceService.create_from_recall(bot_record, transcript_s3_key, ...)
      → Source(upload_type="meeting", source_type=SourceType.AUDIO, origin=INTEGRATION)
  → queue_source_processing_task.delay(source_id)
        │
        ▼
Celery: SourceService.queue_processing(source)
  → AgentCommandClient.send(command_key="source.process.audio", payload={...})
        │
        ▼
Agent SDK: meeting-notes skill
  → Transcript processed → Meeting notes artifact
  → action-extractor → Action records
  → extract-decisions → Decisions context
        │
        ▼
Agent SDK webhook: POST /api/v1/context/webhooks/completion/
  → transcription_complete handler → Source.status = PROCESSED
  → meeting_notes_generated handler → Artifact created
  → actions_extracted handler → Question records created
```

### End-to-End Flow (Phase 2 — Chat & Email additions)

```
[In-meeting: participant types "@BotName query" in chat]
        │
        ▼
Recall real-time chat event → POST /api/v1/integrations/recall-ai/webhooks/
  → InboundWebhook(source="recall_ai", event_type="chat.message")
  → Celery: detect @{bot_name} prefix → bot-mention-responder skill
  → POST /api/v1/bot/{bot_id}/send_chat_message  ← response back into meeting

[Meeting ends + notes generated]
        │
        ▼
Celery: post_meeting_email_task(source_id)
  → AttendeeEmailResolver.resolve(participant_list, org_id)
  → For each attendee: personalize email (filter their action items)
  → GMAIL_SEND_EMAIL via Composio MCP
```

---

## Component Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                        Playbook (Django)                         │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │            integrations/custom/recall_ai/                  │  │
│  │                                                            │  │
│  │  BotCreateView          → RecallAIService.create_bot()     │  │
│  │  RecallAIWebhookView    → InboundWebhook inbox             │  │
│  │  event_handlers.py      → handle_recall_bot_done()         │  │
│  │                           handle_recall_chat_message()     │  │
│  │  tasks.py               → post_meeting_email_task()        │  │
│  │  RecallAIService        → Recall REST API wrapper          │  │
│  │  AttendeeEmailResolver  → participant email resolution      │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────┐    ┌──────────────────────────────────┐    │
│  │  RecallBot model │    │  Integration / IntegrationConn.  │    │
│  │  (new table)     │    │  (existing, DIRECT type)         │    │
│  └──────────────────┘    └──────────────────────────────────┘    │
│                                                                  │
│  ┌──────────────────┐    ┌──────────────────────────────────┐    │
│  │  Source model    │    │  InboundWebhook model            │    │
│  │  (existing)      │    │  (existing)                      │    │
│  └──────────────────┘    └──────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
         │                              │
         │ AgentCommandClient           │ Svix webhooks
         ▼                              ▼
┌──────────────────┐         ┌─────────────────────┐
│   Agent SDK      │         │     Recall AI API    │
│                  │         │  {region}.recall.ai  │
│  meeting-notes   │         └─────────────────────┘
│  action-extractor│
│  extract-decisions│
│  bot-mention-    │
│  responder       │
└──────────────────┘
         │
         ▼ completion webhook
┌──────────────────────────────┐
│  /api/v1/context/webhooks/   │
│       completion/            │
│  transcription_complete      │
│  meeting_notes_generated     │
│  actions_extracted           │
└──────────────────────────────┘
```

---

## Data Model

### New Model: `RecallBot`

File: `integrations/custom/recall_ai/models.py`

```python
class RecallBotStatus(models.TextChoices):
    JOINING          = "joining",          "Joining"
    IN_WAITING_ROOM  = "in_waiting_room",  "In Waiting Room"
    IN_CALL          = "in_call",          "In Call"
    RECORDING        = "recording",        "Recording"
    CALL_ENDED       = "call_ended",       "Call Ended"
    DONE             = "done",             "Done"
    FATAL            = "fatal",            "Fatal"


class RecallBot(TimeStampedModel):
    id                   = models.UUIDField(primary_key=True, default=uuid.uuid4)
    organization         = models.ForeignKey("core.Organization", on_delete=models.CASCADE,
                                             related_name="recall_bots")
    created_by           = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                             null=True, related_name="recall_bots_created")
    project              = models.ForeignKey("context.Project", on_delete=models.SET_NULL,
                                             null=True, blank=True, related_name="recall_bots")
    source               = models.OneToOneField("context.Source", on_delete=models.SET_NULL,
                                                null=True, blank=True, related_name="recall_bot")

    # Recall API fields
    recall_bot_id        = models.CharField(max_length=255, unique=True, db_index=True)
    meeting_url          = models.URLField(max_length=1000)
    bot_name             = models.CharField(max_length=255, default="Parallelloop Notetaker")
    status               = models.CharField(max_length=64, choices=RecallBotStatus.choices,
                                            default=RecallBotStatus.JOINING, db_index=True)
    recall_metadata      = models.JSONField(default=dict)  # full Recall bot metadata echoed back
    bot_metadata         = models.JSONField(default=dict)  # metadata we sent at creation time

    # Recording / transcript references
    recording_url        = models.URLField(max_length=2000, blank=True)
    transcript_url       = models.URLField(max_length=2000, blank=True)
    transcript_s3_key    = models.CharField(max_length=500, blank=True)

    # Participant data
    participants         = models.JSONField(default=list)  # [{name, email?, joined_at, left_at}]
    chat_messages        = models.JSONField(default=list)  # [{sender, text, timestamp}]

    # Lifecycle
    joined_at            = models.DateTimeField(null=True, blank=True)
    call_ended_at        = models.DateTimeField(null=True, blank=True)
    done_at              = models.DateTimeField(null=True, blank=True)
    error_message        = models.TextField(blank=True)

    class Meta:
        db_table = "recall_bots"
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["recall_bot_id"]),
        ]

    def update_status(self, new_status: str) -> None:
        self.status = new_status
        self.save(update_fields=["status", "updated_at"])
```

### Integration DB Record (Migration / Fixture)

```python
Integration.objects.get_or_create(
    name="recall_ai",
    defaults={
        "display_name": "Recall AI Meeting Bot",
        "integration_type": IntegrationType.DIRECT,
        "is_enabled": True,
        "default_available": False,
        "mcp_config_template": {
            "sensitive_env_keys": ["RECALL_API_KEY"],
            "env_keys": ["RECALL_REGION"],
        },
    }
)
```

### Source Model — No Changes Required

Existing fields map perfectly:

| Field | Value for Recall Source |
|---|---|
| `upload_type` | `"meeting"` |
| `source_type` | `SourceType.AUDIO` |
| `origin` | `SourceOrigin.INTEGRATION` |
| `integration_provider` | `"recall_ai"` |
| `external_reference` | `recall_bot.recall_bot_id` |
| `title` | `"Meeting — {date} — {meeting_platform}"` |
| `status` | `SourceStatus.PENDING` → `PROCESSING` → `PROCESSED` |

### Database Schema

```sql
CREATE TABLE recall_bots (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id     UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    created_by_id       INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
    project_id          UUID REFERENCES context_projects(id) ON DELETE SET NULL,
    source_id           UUID UNIQUE REFERENCES context_sources(id) ON DELETE SET NULL,

    recall_bot_id       VARCHAR(255) UNIQUE NOT NULL,
    meeting_url         VARCHAR(1000) NOT NULL,
    bot_name            VARCHAR(255) NOT NULL DEFAULT 'Parallelloop Notetaker',
    status              VARCHAR(64) NOT NULL DEFAULT 'joining',
    recall_metadata     JSONB NOT NULL DEFAULT '{}',
    bot_metadata        JSONB NOT NULL DEFAULT '{}',

    recording_url       VARCHAR(2000),
    transcript_url      VARCHAR(2000),
    transcript_s3_key   VARCHAR(500),

    participants        JSONB NOT NULL DEFAULT '[]',
    chat_messages       JSONB NOT NULL DEFAULT '[]',

    joined_at           TIMESTAMPTZ,
    call_ended_at       TIMESTAMPTZ,
    done_at             TIMESTAMPTZ,
    error_message       TEXT,

    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX recall_bots_org_status ON recall_bots(organization_id, status);
CREATE INDEX recall_bots_recall_bot_id ON recall_bots(recall_bot_id);
```

---

## New Module: `integrations/custom/recall_ai/`

### File Structure

```
integrations/custom/recall_ai/
├── __init__.py
├── apps.py
├── models.py          # RecallBot model
├── migrations/
│   └── 0001_initial.py
├── serializers.py     # BotCreateSerializer, BotStatusSerializer
├── services.py        # RecallAIService, AttendeeEmailResolver
├── views.py           # BotCreateView, BotListView, RecallAIWebhookView
├── urls.py
├── event_handlers.py  # @register_handler("recall_ai", ...)
└── tasks.py           # post_meeting_email_task, retry logic
```

---

## API Design

### Endpoints

#### 1. Create Bot (Dispatch bot to meeting)

```
POST /api/v1/integrations/recall-ai/bots/
Auth: IsAuthenticated, IsOrganizationMember
```

**Request:**
```json
{
  "meeting_url": "https://meet.google.com/abc-defg-hij",
  "project_id": "uuid",          // optional — links meeting to project
  "bot_name": "Parallelloop Notetaker"  // optional — org default if omitted
}
```

**Response (202 Accepted):**
```json
{
  "id": "uuid",
  "recall_bot_id": "bot_abc123",
  "status": "joining",
  "meeting_url": "https://meet.google.com/abc-defg-hij",
  "created_at": "2026-04-19T10:00:00Z"
}
```

**Internal flow:**
```python
class BotCreateView(APIView):
    permission_classes = [IsAuthenticated, IsOrganizationMember]

    def post(self, request):
        serializer = BotCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        connection = get_recall_connection(request.org)  # raises if not connected
        api_key = connection.get_decrypted_credentials()["RECALL_API_KEY"]

        service = RecallAIService(api_key=api_key, region=connection.settings.get("region", "us-east-1"))

        # Pre-create Source record so we have source_id for bot metadata
        source = SourceService().create_placeholder(
            organization=request.org,
            project=project,
            upload_type="meeting",
            title=f"Meeting — {date.today()}",
            origin=SourceOrigin.INTEGRATION,
            integration_provider="recall_ai",
        )

        bot_metadata = {
            "org_id": str(request.org.id),
            "user_id": str(request.user.id),
            "project_id": str(project.id) if project else None,
            "source_id": str(source.id),
        }

        recall_bot_data = service.create_bot(
            meeting_url=validated["meeting_url"],
            bot_name=validated.get("bot_name") or org_settings.recall_bot_name,
            metadata=bot_metadata,
        )

        bot = RecallBot.objects.create(
            organization=request.org,
            created_by=request.user,
            project=project,
            source=source,
            recall_bot_id=recall_bot_data["id"],
            meeting_url=validated["meeting_url"],
            bot_name=recall_bot_data["bot_name"],
            bot_metadata=bot_metadata,
            recall_metadata=recall_bot_data,
        )

        return Response(BotStatusSerializer(bot).data, status=HTTP_202_ACCEPTED)
```

#### 2. List Bots

```
GET /api/v1/integrations/recall-ai/bots/?project_id=uuid&status=done
Auth: IsAuthenticated, IsOrganizationMember
Response: paginated list of RecallBot records
```

#### 3. Get Bot Status

```
GET /api/v1/integrations/recall-ai/bots/{id}/
Auth: IsAuthenticated, IsOrganizationMember
Response: full RecallBot detail including participants, status, linked source_id
```

#### 4. Svix Webhook Receiver

```
POST /api/v1/integrations/recall-ai/webhooks/
Auth: None (AllowAny) — Svix signature verified internally
```

**Implementation:**
```python
@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def recall_ai_webhook(request):
    # Step 1: Verify Svix signature
    if not verify_svix_signature(request):
        return Response({"error": "invalid signature"}, status=HTTP_400_BAD_REQUEST)

    payload  = request.data
    event    = payload.get("event")               # "bot.done", "bot.in_call_recording", etc.
    bot_id   = payload.get("data", {}).get("bot", {}).get("id")

    if not bot_id or not event:
        return Response({"error": "malformed payload"}, status=HTTP_400_BAD_REQUEST)

    # Step 2: Deduplicate (Svix retry-safe)
    external_id = f"{bot_id}:{event}:{payload.get('data', {}).get('data', {}).get('sub_code', '')}"
    if InboundWebhook.find_duplicate("recall_ai", external_id):
        return Response({"status": "duplicate"}, status=HTTP_200_OK)

    # Step 3: Persist and acknowledge
    webhook = InboundWebhook.objects.create(
        source="recall_ai",
        event_type=event,
        external_id=external_id,
        payload=payload,
        status=WebhookStatus.PENDING,
    )
    process_inbound_webhook.delay(str(webhook.id))

    return Response({"status": "received"}, status=HTTP_200_OK)  # Must return within 15s
```

#### 5. Recall AI Connect (API Key setup)

```
POST /api/v1/integrations/recall-ai/connect/
Auth: IsAuthenticated, IsOrganizationAdmin
```

**Request:**
```json
{
  "api_key": "recallai_xxx",
  "region": "us-east-1",
  "bot_name": "Parallelloop Notetaker"  // optional org-level default
}
```

**Internal flow:** Creates / updates `IntegrationConnection` with encrypted `RECALL_API_KEY` via `set_encrypted_credentials()`.

---

## Service Layer

### `RecallAIService`

File: `integrations/custom/recall_ai/services.py`

```python
class RecallAIService:
    BASE_URL_TEMPLATE = "https://{region}.recall.ai/api/v1"
    MAX_RETRY_ATTEMPTS = 10
    RETRY_INTERVAL_SECONDS = 30

    def __init__(self, api_key: str, region: str = "us-east-1"):
        self.api_key = api_key
        self.base_url = self.BASE_URL_TEMPLATE.format(region=region)
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Token {api_key}",
            "Content-Type": "application/json",
        })

    def create_bot(self, meeting_url: str, bot_name: str, metadata: dict) -> dict:
        """
        POST /api/v1/bot
        Handles 507 capacity errors with retry (up to 10 attempts, 30s apart).
        Returns full Recall bot response dict.
        """
        payload = {
            "meeting_url": meeting_url,
            "bot_name": bot_name,
            "metadata": metadata,
            "recording_config": {
                "transcript": {
                    "provider": {"meeting_captions": {}}
                }
            },
        }
        for attempt in range(self.MAX_RETRY_ATTEMPTS):
            resp = self.session.post(f"{self.base_url}/bot", json=payload)
            if resp.status_code == 507:
                if attempt < self.MAX_RETRY_ATTEMPTS - 1:
                    time.sleep(self.RETRY_INTERVAL_SECONDS)
                    continue
                raise RecallCapacityError("Recall AI at capacity after max retries")
            resp.raise_for_status()
            return resp.json()

    def get_bot(self, bot_id: str) -> dict:
        """GET /api/v1/bot/{bot_id}"""
        resp = self.session.get(f"{self.base_url}/bot/{bot_id}")
        resp.raise_for_status()
        return resp.json()

    def send_chat_message(self, bot_id: str, message: str) -> dict:
        """POST /api/v1/bot/{bot_id}/send_chat_message"""
        resp = self.session.post(
            f"{self.base_url}/bot/{bot_id}/send_chat_message",
            json={"message": message}
        )
        resp.raise_for_status()
        return resp.json()

    def download_transcript(self, transcript_url: str) -> bytes:
        """Download transcript from Recall's media_shortcuts URL (authenticated)."""
        resp = self.session.get(transcript_url)
        resp.raise_for_status()
        return resp.content
```

### `AttendeeEmailResolver`

```python
class AttendeeEmailResolver:
    def resolve(self, participants: list[dict], org_id: str) -> list[dict]:
        """
        Input: [{"name": "John Smith", "email": "john@example.com"}, ...]
        Some participants may have email=None (Recall gives display name only).
        Output: [{"name": "...", "email": "...", "member_id": "..."}, ...]
        """
        resolved = []
        members_by_name = self._build_member_name_index(org_id)

        for participant in participants:
            email = participant.get("email")
            name  = participant.get("name", "")

            if not email:
                # Fallback: fuzzy match display name → Parallelloop member
                member = members_by_name.get(name.lower().strip())
                if member:
                    email = member.email
            if email:
                resolved.append({
                    "name": name,
                    "email": email,
                    "member_id": participant.get("member_id"),
                })
        return resolved

    def _build_member_name_index(self, org_id: str) -> dict:
        from core.models import TeamMembership
        members = TeamMembership.objects.filter(
            organization_id=org_id, is_active=True
        ).select_related("user")
        return {
            f"{m.user.first_name} {m.user.last_name}".lower().strip(): m.user
            for m in members
        }
```

---

## Webhook Event Handlers

File: `integrations/custom/recall_ai/event_handlers.py`

### `bot.done` Handler

```python
@register_handler("recall_ai", "bot.done")
def handle_recall_bot_done(webhook: InboundWebhook) -> dict:
    payload    = webhook.payload
    bot_id     = payload["data"]["bot"]["id"]
    bot_record = RecallBot.objects.select_related("source", "organization").get(
        recall_bot_id=bot_id
    )

    # 1. Confirm done via Recall API
    connection = get_recall_connection(bot_record.organization)
    service    = RecallAIService.from_connection(connection)
    bot_data   = service.get_bot(bot_id)

    if bot_data["status"]["code"] != "done":
        raise ValueError(f"Bot {bot_id} not done yet: {bot_data['status']}")

    # 2. Extract transcript URL and participant data
    transcript_url  = bot_data["recordings"][0]["media_shortcuts"]["transcript"]["data"]["download_url"]
    participants    = _extract_participants(bot_data)  # from status_changes / participant list
    chat_messages   = bot_data.get("chat_messages", [])

    # 3. Download transcript → upload to S3
    transcript_bytes = service.download_transcript(transcript_url)
    s3_key           = S3Service().upload_bytes(
        data=transcript_bytes,
        key=f"recall_transcripts/{bot_record.organization_id}/{bot_id}/transcript.json",
        content_type="application/json",
    )

    # 4. Update RecallBot record
    bot_record.status            = RecallBotStatus.DONE
    bot_record.transcript_url    = transcript_url
    bot_record.transcript_s3_key = s3_key
    bot_record.participants      = participants
    bot_record.chat_messages     = chat_messages
    bot_record.done_at           = timezone.now()
    bot_record.save()

    # 5. Update the pre-created Source record (reuse audio upload flow)
    source = bot_record.source
    source.external_reference    = bot_id
    source.integration_provider  = "recall_ai"
    source.status                = SourceStatus.PENDING
    source.save(update_fields=["external_reference", "integration_provider", "status", "updated_at"])

    # 6. Queue processing via existing audio pipeline
    queue_source_processing_task.delay(
        str(source.id),
        str(bot_record.created_by_id),
        {
            "participants": participants,
            "external_participants": _extract_external_participants(participants, bot_record.organization),
            "number_of_participants": len(participants),
            "recall_bot_id": bot_id,
            "chat_messages": chat_messages,
        }
    )

    # 7. Queue post-meeting email (Phase 2)
    post_meeting_email_task.apply_async(
        args=[str(source.id)],
        countdown=300  # 5 min delay — wait for notes to be generated
    )

    return {"status": "queued", "source_id": str(source.id)}
```

### Bot Status Update Handlers

```python
@register_handler("recall_ai", "bot.in_call_recording")
def handle_bot_recording_started(webhook: InboundWebhook) -> dict:
    bot_id = webhook.payload["data"]["bot"]["id"]
    RecallBot.objects.filter(recall_bot_id=bot_id).update(
        status=RecallBotStatus.RECORDING,
        joined_at=timezone.now(),
    )
    return {"status": "updated"}


@register_handler("recall_ai", "bot.call_ended")
def handle_bot_call_ended(webhook: InboundWebhook) -> dict:
    bot_id = webhook.payload["data"]["bot"]["id"]
    RecallBot.objects.filter(recall_bot_id=bot_id).update(
        status=RecallBotStatus.CALL_ENDED,
        call_ended_at=timezone.now(),
    )
    return {"status": "updated"}


@register_handler("recall_ai", "bot.fatal")
def handle_bot_fatal(webhook: InboundWebhook) -> dict:
    bot_id    = webhook.payload["data"]["bot"]["id"]
    sub_code  = webhook.payload.get("data", {}).get("data", {}).get("sub_code", "")
    RecallBot.objects.filter(recall_bot_id=bot_id).update(
        status=RecallBotStatus.FATAL,
        error_message=f"Fatal error: {sub_code}",
    )
    return {"status": "fatal_recorded"}
```

### Chat Message Handler (Phase 2)

```python
@register_handler("recall_ai", "chat.message")
def handle_recall_chat_message(webhook: InboundWebhook) -> dict:
    payload  = webhook.payload
    bot_id   = payload["data"]["bot"]["id"]
    message  = payload["data"]["message"]["text"]
    sender   = payload["data"]["message"]["sender"]

    bot_record = RecallBot.objects.get(recall_bot_id=bot_id)
    bot_name   = bot_record.bot_name.lower()

    # Only respond to @mentions
    if not message.lower().strip().startswith(f"@{bot_name}"):
        return {"status": "ignored"}

    query = message[len(f"@{bot_name}"):].strip()

    # Dispatch to bot-mention-responder skill (existing)
    connection = get_recall_connection(bot_record.organization)
    service    = RecallAIService.from_connection(connection)

    AgentCommandClient().send(
        command_key="bot.mention.respond",
        payload={
            "query": query,
            "org_id": str(bot_record.organization_id),
            "project_id": str(bot_record.project_id) if bot_record.project_id else None,
            "context_type": "project" if bot_record.project_id else "org",
            "response_channel": "recall_chat",
            "response_metadata": {
                "bot_id": bot_id,
                "recall_api_key": connection.get_decrypted_credentials()["RECALL_API_KEY"],
                "recall_region": connection.settings.get("region", "us-east-1"),
            },
        }
    )
    return {"status": "dispatched"}
```

---

## Celery Tasks

File: `integrations/custom/recall_ai/tasks.py`

```python
@shared_task(bind=True, name="recall_ai.post_meeting_email", max_retries=3,
             default_retry_delay=60)
def post_meeting_email_task(self, source_id: str) -> dict:
    """
    Sends personalized meeting summary emails to all attendees.
    Triggered 5 minutes after bot.done to allow notes generation to complete.
    """
    try:
        source     = Source.objects.select_related("project", "organization").get(id=source_id)
        bot_record = source.recall_bot

        if source.status != SourceStatus.PROCESSED:
            # Notes not ready yet — retry
            raise self.retry(countdown=120, exc=Exception("Source not processed yet"))

        participants = bot_record.participants
        resolved     = AttendeeEmailResolver().resolve(participants, str(source.organization_id))

        # Fetch action items from DB (Questions created by actions_extracted handler)
        all_actions  = list(source.project.questions.filter(
            source=source
        ).values("title", "description", "assignee_email"))

        entity_id    = _get_composio_entity_id(source.organization)

        for attendee in resolved:
            their_actions = [a for a in all_actions if a.get("assignee_email") == attendee["email"]]

            email_body = _render_meeting_email(
                attendee_name=attendee["name"],
                source=source,
                their_actions=their_actions,
                all_actions=all_actions,
            )

            composio_service.execute_tool(
                entity_id=entity_id,
                tool_name="GMAIL_SEND_EMAIL",
                params={
                    "to": attendee["email"],
                    "subject": f"Meeting Notes — {source.title}",
                    "body": email_body,
                    "content_type": "text/html",
                }
            )

        return {"status": "sent", "recipients": len(resolved)}

    except Source.DoesNotExist:
        return {"status": "source_not_found"}
```

---

## Reusing the Existing Audio Upload Flow

The Recall AI integration plugs into the **exact same pipeline** used by the manual audio upload flow:

| Step | Manual Upload | Recall AI Integration |
|---|---|---|
| Source creation | `SourceService.create_from_upload(upload, ...)` | `SourceService.create_placeholder(...)` — called at bot creation, not after |
| S3 storage | Client PUT to presigned URL | `S3Service().upload_bytes()` — in `handle_recall_bot_done()` |
| Processing trigger | `queue_source_processing_task.delay(source_id, ...)` | Same Celery task — identical call signature |
| Agent SDK command | `AgentCommandClient.send("source.process.audio", ...)` | Same command key — same payload schema |
| Completion webhook | `POST /api/v1/context/webhooks/completion/` | Same endpoint — same handlers |
| Source status | `PENDING → PROCESSING → PROCESSED` | Same status machine |
| Artifact creation | `ArtifactGeneratedHandler` | Same handler — no changes |

**Key design choice:** The Source record is pre-created at bot dispatch time (not after the meeting), so the UI can show the meeting as "pending" immediately. The transcript is attached to that pre-existing Source after `bot.done`.

---

## URL Routing

File: `integrations/custom/recall_ai/urls.py`

```python
from django.urls import path
from . import views

urlpatterns = [
    path("connect/",         views.RecallAIConnectView.as_view(),   name="recall_ai_connect"),
    path("disconnect/",      views.RecallAIConnectView.as_view(),   name="recall_ai_disconnect"),
    path("bots/",            views.BotCreateView.as_view(),         name="recall_bot_create"),
    path("bots/<uuid:id>/",  views.BotDetailView.as_view(),         name="recall_bot_detail"),
    path("webhooks/",        views.recall_ai_webhook,               name="recall_ai_webhook"),
]
```

Mount in `integrations/urls.py`:
```python
path("recall-ai/", include("integrations.custom.recall_ai.urls", namespace="recall_ai")),
```

---

## Security

### Authentication

| Endpoint | Auth Method |
|---|---|
| `POST /bots/` | `IsAuthenticated` + `IsOrganizationMember` JWT |
| `GET /bots/`, `GET /bots/{id}/` | `IsAuthenticated` + `IsOrganizationMember` |
| `POST /connect/` | `IsAuthenticated` + `IsOrganizationAdmin` |
| `POST /webhooks/` | `AllowAny` — Svix signature verification |

### Svix Signature Verification

```python
import svix
from django.conf import settings

def verify_svix_signature(request) -> bool:
    try:
        wh = svix.Webhook(settings.RECALL_AI_SVIX_SECRET)
        wh.verify(
            request.body,
            {
                "svix-id":        request.headers.get("svix-id"),
                "svix-timestamp": request.headers.get("svix-timestamp"),
                "svix-signature": request.headers.get("svix-signature"),
            }
        )
        return True
    except svix.WebhookVerificationError:
        return False
```

### API Key Storage

- Recall API key stored via `IntegrationConnection.set_encrypted_credentials({"RECALL_API_KEY": key})`
- Fernet encryption at rest, decrypted only within service layer
- Key never exposed in API responses or logs
- `settings.RECALL_AI_SVIX_SECRET` — Svix signing secret stored in env, not in DB

### Authorization

- Bots are scoped to `organization` — no cross-org access
- `get_recall_connection()` helper always filters by `request.org` before decrypting credentials
- Source records created by Recall inherit standard org-level ACL from existing Source model

### Data Protection

- Meeting transcript bytes are stored in org-scoped S3 path: `recall_transcripts/{org_id}/{bot_id}/`
- `chat_messages` stored in `RecallBot.chat_messages` JSONField — no PII beyond what Recall provides
- Participant email resolution is org-local (Parallelloop member directory) — no third-party email lookup

---

## Deployment

### Infrastructure

**New environment variables:**
```env
RECALL_AI_SVIX_SECRET=whsec_xxx   # Svix signing secret from Recall dashboard
# RECALL_API_KEY is stored per-org in IntegrationConnection, not in env
```

**Recall Dashboard setup (one-time):**
1. Create Svix webhook endpoint → `https://app.parallelloop.ai/api/v1/integrations/recall-ai/webhooks/`
2. Subscribe to events: `bot.done`, `bot.in_call_recording`, `bot.call_ended`, `bot.fatal`, `chat.message`
3. Copy Svix signing secret → set `RECALL_AI_SVIX_SECRET`

**Celery queues:**
- `handle_recall_bot_done` → `default` queue (existing)
- `post_meeting_email_task` → `default` queue (existing)
- No new queues required

**Django app registration (`INSTALLED_APPS`):**
```python
"integrations.custom.recall_ai",
```

### CI/CD Pipeline

- New migration: `integrations/custom/recall_ai/migrations/0001_initial.py` — add `recall_bots` table
- `Integration` seed record: add to `data_migrations` or management command `seed_integrations`
- No infrastructure changes — all runs on existing Celery workers and DB

---

## Testing Strategy

### Unit Tests

**`tests/integrations/recall_ai/test_services.py`**
- `RecallAIService.create_bot()` — mock Recall API, assert 507 retry logic (up to 10 attempts)
- `RecallAIService.send_chat_message()` — happy path and error handling
- `AttendeeEmailResolver.resolve()` — cases: email present, name match, no match

**`tests/integrations/recall_ai/test_handlers.py`**
- `handle_recall_bot_done()` — mock Recall API `get_bot()`, S3 upload, assert Source queued
- `handle_recall_bot_done()` — idempotency: duplicate webhook → no duplicate Source processing
- `handle_recall_chat_message()` — with `@BotName` prefix → dispatched; without → ignored

**`tests/integrations/recall_ai/test_views.py`**
- `recall_ai_webhook()` — valid Svix signature → 200; invalid → 400
- `BotCreateView` — no Recall connection → 400; valid → 202; Recall 507 all retries exhausted → 503

### Integration Tests

- Full flow: `POST /bots/` → mock Recall webhook `bot.done` → assert Source created + `queue_source_processing_task` called
- `post_meeting_email_task` — assert GMAIL_SEND_EMAIL called per resolved attendee, personalized content

### Existing Tests Unaffected

- Audio upload flow tests (`test_upload_presign`, `test_upload_finalize`) — unchanged; Recall uses a separate code path for Source creation
- `SourceService.queue_processing()` — no changes; Recall calls same function with same signature

---

## Performance Requirements

| Operation | Target | Notes |
|---|---|---|
| Webhook acknowledgement | < 500ms | Svix requires 2xx within 15s; we target < 500ms |
| Bot creation API response | < 3s | Recall API latency + 507 retry only on capacity |
| Transcript download + S3 upload | < 60s | Runs async in Celery; no user-facing wait |
| Source processing dispatch | < 5s after S3 upload | `queue_source_processing_task` Celery dispatch |
| Full bot.done → notes ready | < 5 min | Agent SDK processing time |
| Email delivery | < 10 min after bot.done | `post_meeting_email_task` with 5 min countdown delay |

**Celery task limits (consistent with existing tasks):**
- `post_meeting_email_task`: `max_retries=3`, `default_retry_delay=60`
- `process_inbound_webhook`: inherits existing `max_retries=3`, exponential backoff

---

## Open Questions

1. **Recall region config** — Is the Recall API key region-specific? Should `region` be stored per `IntegrationConnection` or org-wide? Default to `us-east-1` until confirmed.

2. **Source placeholder title** — At bot creation time we don't know the meeting title. Options: (a) use meeting URL domain + date, (b) use calendar event title (if available), (c) update title after `bot.done` using participant list. Recommend option (c): update Source title in `handle_recall_bot_done()` once Recall returns meeting metadata.

3. **Multiple bots per meeting** — Should we prevent duplicate bots for the same `meeting_url` within the same org? Recommend: check for existing `RecallBot` with same `meeting_url` and status not in `[fatal, done]` before dispatching.

4. **Gmail sender identity** — Which Gmail account sends the post-meeting emails? Requires org-level Gmail `IntegrationConnection` to be active. If not connected, skip email silently or notify organizer only.

5. **Bot name configurability** — Stored where? Options: (a) `IntegrationConnection.settings["bot_name"]`, (b) per-meeting override in `POST /bots/` request. Recommend both: org default in `settings`, per-bot override in request.

6. **Composio Recall MCP evaluation** — Evaluate Composio's Recall AI MCP tool set. If it covers `get_bot` + `send_chat_message`, Agent SDK skills could use it for Recall interactions without needing the `response_metadata.recall_api_key` passthrough pattern.

---

*Generated via context-chat — 2026-04-19*
