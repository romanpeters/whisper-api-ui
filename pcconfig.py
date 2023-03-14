import pynecone as pc

config = pc.Config(
    app_name="whisper_ui",
    db_url="sqlite:///pynecone.db",
    api_url="http://10.10.20.20:8000",
#    env=pc.Env.DEV,
)
