import os
from dotenv import load_dotenv

env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env.test"))
load_dotenv(dotenv_path=env_path, override=True)
