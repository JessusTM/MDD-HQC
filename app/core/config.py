from pydantic_settings import BaseSettings 

class Config(BaseSettings):
    app_name : str = "RDD Hybrid Systems"

config = Config()
