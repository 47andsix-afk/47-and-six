import os

from google.genai import Client
from google.genai.errors import ClientError


def main() -> None:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY is not set. Configure it before running this script.")
        return

    client = Client(api_key=api_key)
    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    try:
        stream = client.models.generate_content_stream(
            model=model,
            contents="Explain quantum computing simply.",
        )

        for chunk in stream:
            print(getattr(chunk, "text", ""), end="", flush=True)
        print()
    except ClientError as exc:
        print(f"Gemini request failed: {exc}")
        if getattr(exc, "status_code", None) == 429:
            print("Quota exhausted. Check your Gemini API plan and billing details.")
    except Exception as exc:
        print(f"Unexpected error: {exc}")


if __name__ == "__main__":
    main()
