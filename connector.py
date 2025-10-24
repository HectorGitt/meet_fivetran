# c:\Users\USER\Documents\Codes\Python\devpost\connector.py
from fivetran_connector_sdk import Connector, Operations as op
from meet_client import MeetClient
import json
from datetime import datetime, timedelta
from google.apps.meet_v2.types import (
    ConferenceRecord,
    Participant,
    Recording,
    Transcript,
)


def validate_configuration(configuration: dict):
    """
    Validate the configuration dictionary to ensure it contains all required parameters.
    """
    required_configs = ["refresh_token", "client_secret", "client_id"]
    for key in required_configs:
        if key not in configuration:
            raise ValueError(f"Missing required configuration value: {key}")


def schema(configuration: dict) -> list:
    return [
        {
            "table": "conference_records",
            "primary_key": ["name"],
        },
        {
            "table": "participants",
            "primary_key": ["name"],
        },
        {
            "table": "recordings",
            "primary_key": ["name"],
        },
        {
            "table": "transcripts",
            "primary_key": ["name"],
        },
    ]


def update(configuration: dict, state: dict):
    validate_configuration(configuration)
    meet_client = MeetClient(configuration)

    # Get the last execution timestamp from the state, if available.
    # The API expects a timestamp in RFC3339 format, e.g., "2023-10-23T10:00:00Z"
    # We'll look back 7 days if no state is present.
    last_execution_utc = state.get(
        "last_execution_utc", (datetime.utcnow() - timedelta(days=7)).isoformat() + "Z"
    )

    # The Meet API filter expects a timestamp in RFC3339 format.
    filter_query = f'end_time > "{last_execution_utc}"'

    conference_records = meet_client.list_conference_records(filter_query=filter_query)

    if not conference_records:
        print("No new conference records found.")
        return

    latest_end_time = last_execution_utc
    for record in conference_records:
        record_dict = ConferenceRecord.to_dict(record)
        print(record_dict)
        op.upsert(table="conference_records", data=record_dict)

        conference_id = record_dict[
            "name"
        ]  # The 'name' field is the unique ID, e.g., 'conferenceRecords/...'

        # Fetch and upsert participants
        participants = meet_client.list_participants(conference_id)
        if participants:
            for participant in participants:
                participant_dict = Participant.to_dict(participant)
                print(participant_dict)
                op.upsert(table="participants", data=participant_dict)

        # Fetch and upsert recordings
        recordings = meet_client.list_recordings(conference_id)
        if recordings:
            for recording in recordings:
                recording_dict = Recording.to_dict(recording)
                print(recording_dict)
                op.upsert(table="recordings", data=recording_dict)

        # Fetch and upsert transcripts
        transcripts = meet_client.list_transcripts(conference_id)
        print(transcripts)
        if transcripts:
            for transcript in transcripts:
                transcript_dict = Transcript.to_dict(transcript)
                print(transcript_dict)
                # Get the document ID from the transcript object
                doc_id = transcript_dict.get("doc_id")
                if doc_id:
                    content = meet_client.get_doc_content(doc_id)
                    if content:
                        transcript_data = {
                            "name": transcript_dict.get("name"),
                            "docId": doc_id,
                            "content": content,
                            "conference_id": conference_id,
                        }
                        op.upsert(table="transcripts", data=transcript_data)

        # Keep track of the latest end time for the state checkpoint
        if record_dict.get("end_time") and record_dict["end_time"] > latest_end_time:
            latest_end_time = record_dict["end_time"]

    # Update the state with the end time of the latest processed record
    op.checkpoint({"last_execution_utc": latest_end_time})


# The Fivetran connector SDK will call the `connector` function to get the connector instance.
connector = Connector(update=update, schema=schema)

if __name__ == "__main__":
    # Open the configuration.json file and load its contents into a dictionary.
    try:
        with open("configuration.json", "r") as f:
            configuration = json.load(f)
    except FileNotFoundError:
        configuration = {}
    # Adding this code to your `connector.py` allows you to test your connector by running your file directly from your IDE.
    connector.debug(configuration=configuration)
