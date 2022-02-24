from dotenv import load_dotenv

import os, uuid
from azure.storage.blob import (
    BlobServiceClient,
    BlobClient,
    ContainerClient,
    generate_blob_sas,
    BlobSasPermissions,
)

from datetime import datetime, timedelta
import json
import requests
from pathlib import Path

# load environment variables from .env
load_dotenv()

# azure storage api variables
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_STORAGE_API_KEY = os.getenv("AZURE_STORAGE_API_KEY")
AZURE_STORAGE_ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")

# speech api variables
AZURE_SPEECH_API_KEY_1 = os.getenv("AZURE_SPEECH_API_KEY_1")
AZURE_SPEECH_ENDPOINT = os.getenv("AZURE_SPEECH_ENDPOINT")
AZURE_SPEECH_LOCATION = os.getenv("AZURE_SPEECH_LOCATION")


class DataStorage:
    def __init__(self, path):
        self.path = path
        # set file name as local file name
        self.file_name = self.path.name

    # create a new blob container and upload files to it
    def upload_file(self):
        # currently only works on 1 file
        # TODO: Work on a folder of files

        # create a BlobServiceClient to create a container client
        self.blob_service_client = BlobServiceClient.from_connection_string(
            AZURE_STORAGE_CONNECTION_STRING
        )

        # create a unique name for the container
        self.container_name = str(uuid.uuid4())

        # create a container
        self.container_client = self.blob_service_client.create_container(
            self.container_name
        )

        # create a blob client using the local file name as the name for the blob
        self.blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name, blob=self.file_name
        )

        # create url for the created blob
        # https://stackoverflow.com/questions/16961933/how-to-get-blob-url-after-file-upload-in-azure
        self.blob_url = self.blob_client.url

        # use the blob client to upload the local file
        with open(self.path, "rb") as data:
            self.blob_client.upload_blob(data)

    def generate_sas_url(self):
        sas_blob = self._generate_blob_sas()

        blob_sas_url = f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{self.container_name}/{self.file_name}?{sas_blob}"

        self.blob_sas_url = blob_sas_url

    # create a sas to use to request a transcript
    def _generate_blob_sas(self):
        sas_blob = generate_blob_sas(
            account_name=AZURE_STORAGE_ACCOUNT_NAME,
            container_name=self.container_name,
            blob_name=self.file_name,
            account_key=AZURE_STORAGE_API_KEY,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(days=7),
        )

        return sas_blob

    def delete_container(self):
        # delete the created container
        self.container_client.delete_container()


class TranscriptGenerator:
    headers = {
        "accept": "application/json",
        "Ocp-Apim-Subscription-Key": AZURE_SPEECH_API_KEY_1,
    }

    def __init__(self, url):
        self.url = url

    def create_transcript(self):

        # create configuration parameters
        parameters = {
            "contentUrls": [self.url],
            "locale": "en-AU",
            "displayName": "Transcription of out.wav using default model for en-AU",
            "properties": {
                "profanityFilterMode": None,
                "punctuationMode": "DictatedAndAutomatic",
                "wordLevelTimestampsEnabled": False,
                "diarizationEnabled": False,
                "timeToLive": "P7D",  # ISO-8601
                # "destinationContainerUrl": container_client.url,
            },
        }

        request_url = "https://australiaeast.api.cognitive.microsoft.com/speechtotext/v3.0/transcriptions"

        # create a transcription request
        r = requests.post(
            request_url, headers=self.headers, data=json.dumps(parameters)
        )

        # return transcript id
        transcript_id = r.json()["self"].split("/")[-1]

        self.transcript_id = transcript_id

    def check_transcription_status(self):
        url = f"https://australiaeast.api.cognitive.microsoft.com/speechtotext/v3.0/transcriptions/{self.transcript_id}/"

        res = requests.get(url, headers=self.headers)

        return res.json()["status"]

    def get_transcription_files(self):
        url = f"https://australiaeast.api.cognitive.microsoft.com/speechtotext/v3.0/transcriptions/{self.transcript_id}/files"

        # this creates the transcript report and the transcription
        res = requests.get(url, headers=self.headers).json()

        values = res["values"]

        # mapped from json to transcript url manually
        transcription_url = values[1]["links"]["contentUrl"]

        res = requests.get(transcription_url)

        self.res = res.json()

    def create_text_file(self):
        res = self.res

        with open("./transcripts/transcript.txt", mode="w") as localfile:

            for phrase in res["recognizedPhrases"]:
                timestamp = phrase["offset"]
                text = phrase["nBest"][0]["display"]
                localfile.write(timestamp + "\n")
                localfile.write(text + "\n")
