# Fivetran Google Meet Connector

This is a custom Fivetran connector for Google Meet that pulls meeting artifacts including conference records, participants, recordings, and transcripts.

## Features

-   **Conference Records**: Fetches all conference/meeting records with metadata
-   **Participants**: Lists all participants for each conference
-   **Recordings**: Retrieves recording information for meetings
-   **Transcripts**: Pulls meeting transcripts and their content from Google Docs

## Prerequisites

-   Python 3.7 or higher
-   Google Cloud Project with the following APIs enabled:
    -   Google Meet API
    -   Google Docs API
-   OAuth 2.0 credentials (Client ID and Client Secret)

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
    - Google Meet API
    - Google Docs API
4. Create OAuth 2.0 credentials:
    - Go to "APIs & Services" > "Credentials"
    - Click "Create Credentials" > "OAuth client ID"
    - Choose "Desktop app" as application type
    - Note down your `client_id` and `client_secret`

### 3. Get Refresh Token

Run the `get_refresh_token.py` script to obtain a refresh token:

```bash
python get_refresh_token.py
```

This will open a browser window for you to authorize the application. After authorization, you'll receive a refresh token.

### 4. Configure the Connector

Create a `configuration.json` file with your credentials:

```json
{
	"client_id": "YOUR_CLIENT_ID",
	"client_secret": "YOUR_CLIENT_SECRET",
	"refresh_token": "YOUR_REFRESH_TOKEN"
}
```

### 5. Run the Connector

#### Using Fivetran CLI

```bash
fivetran debug --configuration configuration.json
```

#### Direct Python Execution

```bash
python connector.py
```

## Data Schema

The connector creates four tables:

### conference_records

-   Primary Key: `name`
-   Contains: Meeting metadata, start/end times, space information

### participants

-   Primary Key: `name`
-   Contains: Participant details, join/leave times, user information

### recordings

-   Primary Key: `name`
-   Contains: Recording metadata, start/end times, storage location

### transcripts

-   Primary Key: `name`
-   Contains: Transcript metadata, document ID, full text content, conference reference

## How It Works

1. The connector fetches conference records that ended after the last sync (defaults to 7 days back)
2. For each conference, it retrieves:
    - All participants who joined
    - Any recordings that were made
    - Transcripts (if enabled) along with their content from Google Docs
3. All data is converted from protobuf format to dictionaries for Fivetran compatibility
4. The connector checkpoints the latest `end_time` for incremental syncs

## Incremental Sync

The connector maintains state between syncs using the `last_execution_utc` timestamp. Only conferences that ended after this timestamp are fetched in subsequent syncs.

## Troubleshooting

### Authentication Errors

-   Ensure your OAuth scopes include:
    -   `https://www.googleapis.com/auth/meetings.space.readonly`
    -   `https://www.googleapis.com/auth/documents.readonly`
-   Regenerate your refresh token if it has expired

### No Data Returned

-   Check that you have meetings within the sync window (default: last 7 days)
-   Verify that the Google Meet API is enabled in your project
-   Ensure your account has access to the meetings you're trying to fetch

### Protobuf Conversion Errors

-   The connector uses `ConferenceRecord.to_dict()` and similar methods for proto-plus objects
-   Ensure you have the latest version of `google-apps-meet` installed

## Development

### Project Structure

```
├── connector.py          # Main Fivetran connector logic
├── meet_client.py        # Google Meet API client wrapper
├── get_refresh_token.py  # OAuth token generation script
├── requirements.txt      # Python dependencies
└── configuration.json    # Configuration file (not in repo)
```

### Testing

The connector includes a debug mode for local testing:

```bash
python connector.py
```

This will read from `configuration.json` and output results to the console.

## License

MIT
