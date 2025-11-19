"""Fixed AutoGen Studio server that includes message content in responses"""
import os
from fastapi import FastAPI
from autogenstudio.datamodel import Response
from autogenstudio.teammanager import TeamManager

app = FastAPI()
team_manager = TeamManager()


def serialize_message(message):
    """Serialize a message with its content"""
    # Serialize models_usage
    models_usage = None
    if message.models_usage:
        if hasattr(message.models_usage, 'model_dump'):
            models_usage = message.models_usage.model_dump()
        elif hasattr(message.models_usage, 'dict'):
            models_usage = message.models_usage.dict()
        else:
            # Manual serialization for RequestUsage
            models_usage = {
                "prompt_tokens": getattr(message.models_usage, 'prompt_tokens', 0),
                "completion_tokens": getattr(message.models_usage, 'completion_tokens', 0)
            }

    result = {
        "source": message.source,
        "models_usage": models_usage,
        "metadata": message.metadata if hasattr(message, 'metadata') else {}
    }

    # Try to extract content from the message
    try:
        # Try to get content field directly (works for TextMessage, etc.)
        if hasattr(message, 'content'):
            result['content'] = message.content
        # Try to convert to text
        elif hasattr(message, 'to_text'):
            result['content'] = message.to_text()
        elif hasattr(message, 'to_model_text'):
            result['content'] = message.to_model_text()
    except Exception as e:
        result['content'] = f"[Error extracting content: {e}]"

    return result


def serialize_task_result(task_result):
    """Serialize TaskResult with message content included"""
    messages = task_result.messages

    # Normalize messages (handle dict or list format)
    if isinstance(messages, dict):
        messages = [messages[k] for k in sorted(messages.keys(), key=lambda x: int(x) if str(x).isdigit() else 0)]

    serialized_messages = []
    for msg in messages:
        serialized_messages.append(serialize_message(msg))

    return {
        "messages": serialized_messages,
        "stop_reason": task_result.stop_reason
    }


@app.get("/predict/{task}")
async def predict(task: str):
    response = Response(message="Task successfully completed", status=True, data=None)
    try:
        team_file_path = os.environ.get("AUTOGENSTUDIO_TEAM_FILE")

        # Check if team_file_path is set
        if team_file_path is None:
            raise ValueError("AUTOGENSTUDIO_TEAM_FILE environment variable is not set")

        result = await team_manager.run(task=task, team_config=team_file_path)

        # Serialize the result with content included
        serialized_data = {
            "task_result": serialize_task_result(result.task_result),
            "usage": result.usage,
            "duration": result.duration
        }

        response.data = serialized_data
    except Exception as e:
        response.message = str(e)
        response.status = False
    return response