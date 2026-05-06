# Реализуйте здесь клиент для GraphQL.

PROJECT_CODE = "likes-s15"

def build_payload(query: str, variables: dict) -> dict:
    return {
        "query": query,
        "variables": variables
    }
