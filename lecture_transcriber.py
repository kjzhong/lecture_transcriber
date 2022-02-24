from backend import azure
from pathlib import Path
import time


if __name__ == "__main__":
    file_path = Path(r"./audio/out.wav")

    data_storage = azure.DataStorage(file_path)
    data_storage.upload_file()
    data_storage.generate_sas_url()

    print(data_storage.blob_url)

    transcript_generator = azure.TranscriptGenerator(data_storage.blob_sas_url)
    transcript_generator.create_transcript()

    # track transcript
    completed = False

    while not completed:
        time.sleep(5)

        status = transcript_generator.check_transcription_status()

        print(status)

        if status in {"Failed", "Succeeded"}:
            completed = True

    if status == "Succeeded":
        transcript_generator.get_transcription_files()
        transcript_generator.create_text_file()
    else:
        print("something has gone wrong")

    data_storage.delete_container()
