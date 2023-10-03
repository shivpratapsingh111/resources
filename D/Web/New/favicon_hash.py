#!/usr/bin/env python3
import mmh3
import sys
import requests

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} [Favicon URL]")
    sys.exit(1)  # Use non-zero exit code to indicate an error

try:
    response = requests.get(sys.argv[1])
    response.raise_for_status()  # Check if the request was successful (status code 200)
    favicon = response.content
    hash_value = mmh3.hash(str(favicon))  # Convert the content to a string before hashing
    print(f"Favicon Hash: {hash_value}")
except requests.exceptions.RequestException as e:
    print(f"Error occurred while fetching the favicon: {e}", file=sys.stderr)
    sys.exit(1)  # Use non-zero exit code to indicate an error
except Exception as e:
    print(f"An unexpected error occurred: {e}", file=sys.stderr)
    sys.exit(1)  # Use non-zero exit code to indicate an error
