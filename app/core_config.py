from pydantic import BaseModel, Field


class Settings(BaseModel):
    app_name: str = Field(default="AI Product Copilot")
    app_version: str = Field(default="0.1.0")
    default_top_k_feedback: int = Field(default=25)
    default_embedding_dim: int = Field(default=512)
    cluster_count_cap: int = Field(default=6)


settings = Settings()
