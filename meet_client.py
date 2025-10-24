# c:\Users\USER\Documents\Codes\Python\devpost\meet_client.py

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.apps import meet_v2
from googleapiclient.discovery import build as docs_build

TOKEN_URL = "https://oauth2.googleapis.com/token"


class MeetClient:
    def __init__(self, configuration: dict):
        self.config = configuration
        self.creds = self._get_credentials()
        self.meet_client = meet_v2.ConferenceRecordsServiceClient(
            credentials=self.creds
        )
        self.docs_service = docs_build("docs", "v1", credentials=self.creds)

    def _get_credentials(self):
        creds = Credentials(
            token=None,
            refresh_token=self.config.get("refresh_token"),
            token_uri=TOKEN_URL,
            client_id=self.config.get("client_id"),
            client_secret=self.config.get("client_secret"),
            scopes=[
                "https://www.googleapis.com/auth/meetings.space.readonly",
                "https://www.googleapis.com/auth/documents.readonly",
            ],
        )
        # Refresh the token
        creds.refresh(Request())
        return creds

    def list_conference_records(self, filter_query=""):
        """
        List all conference records.
        """
        request = meet_v2.ListConferenceRecordsRequest(filter=filter_query)
        response = self.meet_client.list_conference_records(request=request)
        return list(response.conference_records)

    def list_participants(self, conference_id):
        """
        List all participants for a specific conference.
        """
        request = meet_v2.ListParticipantsRequest(parent=conference_id)
        response = self.meet_client.list_participants(request=request)
        return list(response.participants)

    def list_recordings(self, conference_id):
        """
        List all recordings for a specific conference.
        """
        request = meet_v2.ListRecordingsRequest(parent=conference_id)
        response = self.meet_client.list_recordings(request=request)
        return list(response.recordings)

    def list_transcripts(self, conference_id):
        """
        List all transcripts for a specific conference.
        """
        request = meet_v2.ListTranscriptsRequest(parent=conference_id)
        response = self.meet_client.list_transcripts(request=request)
        return list(response.transcripts)

    def get_doc_content(self, doc_id):
        """
        Get the content of a Google Doc.
        """
        try:
            doc = self.docs_service.documents().get(documentId=doc_id).execute()
            content = ""
            for element in doc.get("body", {}).get("content", []):
                if "paragraph" in element:
                    for pe in element["paragraph"].get("elements", []):
                        if "textRun" in pe:
                            content += pe["textRun"]["content"]
            return content
        except Exception as e:
            print(f"An error occurred while fetching doc content for {doc_id}: {e}")
            return None
