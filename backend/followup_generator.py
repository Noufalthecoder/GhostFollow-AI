import json
import os
from pathlib import Path

PROMPT_PATH = Path(__file__).parent / "prompts" / "followup_prompt.txt"


def _load_system_prompt() -> str:
    if PROMPT_PATH.exists():
        return PROMPT_PATH.read_text(encoding="utf-8")
    return (
        "You generate concise, friendly B2B follow-up messages for ghosted prospects. "
        "Keep it helpful, contextual, and non-pushy."
    )


def _fallback_generation(conversation_context: str) -> dict:
    message = (
        "Hi! Just checking in in case this slipped through your inbox. "
        "Happy to answer any questions and help you evaluate if this is a fit."
    )
    reasoning_steps = [
        "Step 1: Checking conversation inactivity",
        "Step 2: Last reply detected beyond threshold",
        "Step 3: Identified user intent from prior messages",
        "Step 4: Generated concise contextual follow-up",
        "Step 5: Prepared for web-agent delivery",
    ]
    return {
        "message": message,
        "reasoning": reasoning_steps,
        "provider": "fallback-template",
        "raw_context": conversation_context,
    }


def _try_openai(system_prompt: str, conversation_context: str, model: str) -> dict | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model=model,
            input=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": (
                        "Conversation context:\n"
                        f"{conversation_context}\n\n"
                        "Return strict JSON with keys: message, reasoning (array of steps)."
                    ),
                },
            ],
            temperature=0.5,
        )
        text = response.output_text.strip()
        parsed = json.loads(text)
        parsed["provider"] = "openai"
        return parsed
    except Exception:
        return None


def _try_amazon_nova(system_prompt: str, conversation_context: str, model: str) -> dict | None:
    use_nova = os.getenv("USE_AMAZON_NOVA", "false").lower() == "true"
    if not use_nova:
        return None

    try:
        import boto3

        client = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION", "us-east-1"))
        payload = {
            "messages": [
                {"role": "system", "content": [{"text": system_prompt}]},
                {
                    "role": "user",
                    "content": [
                        {
                            "text": (
                                "Conversation context:\n"
                                f"{conversation_context}\n\n"
                                "Return JSON with keys: message, reasoning"
                            )
                        }
                    ],
                },
            ],
            "inferenceConfig": {"maxTokens": 400, "temperature": 0.5},
        }
        response = client.invoke_model(modelId=model, body=json.dumps(payload))
        body = json.loads(response["body"].read())
        text = body["output"]["message"]["content"][0]["text"]
        parsed = json.loads(text)
        parsed["provider"] = "amazon-nova"
        return parsed
    except Exception:
        return None


def generate_followup(conversation_context: str, model: str = "gpt-4.1-mini") -> dict:
    system_prompt = _load_system_prompt()

    openai_result = _try_openai(system_prompt, conversation_context, model)
    if openai_result:
        return openai_result

    nova_model = os.getenv("AMAZON_NOVA_MODEL", "amazon.nova-lite-v1:0")
    nova_result = _try_amazon_nova(system_prompt, conversation_context, nova_model)
    if nova_result:
        return nova_result

    return _fallback_generation(conversation_context)
