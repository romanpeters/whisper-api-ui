import pynecone as pc

config = pc.Config(
    app_name="whisper_ui",
    db_url="sqlite:///pynecone.db",
    api_url="http://0.0.0.0:8000",
)
