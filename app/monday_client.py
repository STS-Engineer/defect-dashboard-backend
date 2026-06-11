import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

MONDAY_API_TOKEN = os.getenv("MONDAY_API_TOKEN")
MONDAY_API_URL = "https://api.monday.com/v2"


def monday_request(query: str, variables: dict | None = None):
    if not MONDAY_API_TOKEN:
        raise RuntimeError("MONDAY_API_TOKEN missing in .env")

    headers = {
        "Authorization": MONDAY_API_TOKEN,
        "Content-Type": "application/json",
        "API-Version": "2025-01",
    }

    response = requests.post(
        MONDAY_API_URL,
        headers=headers,
        json={
            "query": query,
            "variables": variables or {},
        },
        timeout=60,
    )

    if response.status_code != 200:
        raise RuntimeError(f"Monday API error: {response.status_code} {response.text}")

    data = response.json()

    if "errors" in data:
        raise RuntimeError(json.dumps(data["errors"], indent=2, ensure_ascii=False))

    return data["data"]


def fetch_board_items(board_id: int):
    all_items = []
    cursor = None

    while True:
        query = """
        query ($board_id: ID!, $cursor: String) {
          boards(ids: [$board_id]) {
            items_page(limit: 500, cursor: $cursor) {
              cursor
              items {
                id
                name
                created_at
                updated_at
                group {
                  id
                  title
                }
                column_values {
                  id
                  type
                  text
                  value
                  ... on BoardRelationValue {
                    display_value
                  }
                  ... on MirrorValue {
                    display_value
                  }
                  ... on FormulaValue {
                    display_value
                  }
                }
              }
            }
          }
        }
        """

        data = monday_request(
            query,
            {
                "board_id": str(board_id),
                "cursor": cursor,
            },
        )

        page = data["boards"][0]["items_page"]
        all_items.extend(page["items"])

        cursor = page["cursor"]
        if not cursor:
            break

    return all_items


def fetch_board_groups(board_id: int):
    query = """
    query ($board_id: [ID!]) {
      boards(ids: $board_id) {
        groups {
          id
          title
        }
      }
    }
    """

    data = monday_request(query, {"board_id": [str(board_id)]})
    return data["boards"][0]["groups"]


def fetch_items_by_group(board_id: int, group_id: str):
    all_items = []
    cursor = None

    while True:
        query = """
        query ($board_id: ID!, $group_id: String!, $cursor: String) {
          boards(ids: [$board_id]) {
            groups(ids: [$group_id]) {
              items_page(limit: 500, cursor: $cursor) {
                cursor
                items {
                  id
                  name
                  created_at
                  updated_at
                  group {
                    id
                    title
                  }
                  column_values {
                    id
                    type
                    text
                    value
                    ... on BoardRelationValue {
                      display_value
                    }
                  ... on MirrorValue {
                    display_value
                  }
                  ... on FormulaValue {
                    display_value
                  }
                }
              }
            }
            }
          }
        }
        """

        data = monday_request(
            query,
            {
                "board_id": str(board_id),
                "group_id": group_id,
                "cursor": cursor,
            },
        )

        page = data["boards"][0]["groups"][0]["items_page"]
        all_items.extend(page["items"])

        cursor = page["cursor"]
        if not cursor:
            break

    return all_items
