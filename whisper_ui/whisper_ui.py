import io
import os
from pcconfig import config
import pynecone as pc
import openai

filename = f"{config.app_name}/{config.app_name}.py"

cache_path = "/tmp/whisper"
if not os.path.exists(cache_path):
    os.makedirs(cache_path)


class State(pc.State):
    """The app state."""
    transcript: str
    audio_file: str
    api_key: str
    invalid_key: bool = False
    not_ready: bool = True
    transcript_processing: bool = False
    transcript_made: bool = False

    def validate_api_key(self, text):
        if not text.startswith("sk-"):
            self.invalid_key = True
        else:
            self.invalid_key = False

    def set_api_key(self, text):
        if not self.invalid_key:
            self.api_key = text
            if self.audio_file:
                self.not_ready = False

    def delete_api_key(self):
        self.api_key = ""
        self.invalid_key = False
        self.not_ready = True

    def process_transcript(self):
        """Set the transcription processing flag to true and indicate image is not made yet."""
        self.transcript_processing = True
        self.transcript_made = False        

    async def handle_upload(self, file: pc.UploadFile):
        upload_data = await file.read()
        outfile = f"{cache_path}/{file.filename}"

        # Save the file.
        with open(outfile, "wb") as f:
            f.write(upload_data)

        self.audio_file = file.filename
        if self.api_key and not self.invalid_key:
            self.not_ready = False

    def transcribe(self):
        self.transcript_processing = True
        self.transcript_made = False
        self.not_ready = True
        try:
            openai.api_key = self.api_key
            audio = open(f"{cache_path}/{self.audio_file}", "rb")
            self.transcript = openai.Audio.transcribe("whisper-1", audio).text
        except Exception as e:
            self.transcript = str(e)
        self.transcript_processing = False
        self.transcript_made = True


def index():
    return pc.center(
        pc.vstack(
            pc.heading("Whisper", font_size="1.5em", padding="2em"),

            ## API key
            pc.cond(
                State.api_key,
                pc.button("Remove API key", on_click=State.delete_api_key),
                pc.vstack(
                    pc.cond(
                        State.invalid_key,
                        pc.text("Invalid API key")),
                    pc.input(placeholder="Enter OpenAI API key",on_change=State.validate_api_key, on_blur=State.set_api_key))),

            ## Upload
            pc.upload(
                pc.vstack(
                    pc.button("Select File"),
                    padding="2em"),
                accept=["m4a","mp3","webm","mp4","mpga","wav","mpeg"],
                on_mouse_enter=lambda: State.handle_upload(pc.upload_files())),

            ## Transcribe
            State.audio_file,
            pc.vstack(
                pc.text(State.audio_file),
                pc.button("Transcribe", is_disabled=State.not_ready, on_click=State.transcribe, width="100%"),
                padding="2em"),
                    
            pc.divider(),
            pc.cond(
                State.transcript_processing,
                pc.circular_progress(is_indeterminate=True),
                pc.cond(
                     State.transcript_made,
                     pc.text(State.transcript))),
            bg="white",
            padding="2em",
            shadow="lg",
            border_radius="lg",
        ),
        width="100%",
        height="100vh",
        bg="radial-gradient(circle at 22% 11%,rgba(62, 180, 137,.20),hsla(0,0%,100%,0) 19%)",
    )

# Add state and page to the app.
app = pc.App(state=State)
app.add_page(index, title="Whisper")
app.compile()

