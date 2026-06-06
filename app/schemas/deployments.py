from pydantic import BaseModel


class DeploymentCreateRequest(BaseModel):
    model: str


class CompletionRequest(BaseModel):
    prompt: str


class CompletionResponse(BaseModel):
    output: str
    input_tokens: int
    output_tokens: int


class GetDeploymentResponse(BaseModel):
    deployment_id: str
    model: str
    status: str
    endpoint_url: str = None
    api_key: str = None