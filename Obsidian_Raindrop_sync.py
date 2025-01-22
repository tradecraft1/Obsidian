
import os
import requests
import json
import hashlib
from datetime import datetime, timedelta

# Configuration
CLIENT_ID = "XXXX"  # Replace with your Raindrop client ID
CLIENT_SECRET = "XXXXX"  # Replace with your Raindrop client secret
REDIRECT_URI = "http://localhost/callback"  # Replace with your app's redirect URI
TOKEN_FILE = "raindrop_token.json"  # File to store tokens
VAULT_PATH = "/Path/To/Your/Vault/"  # Replace with your Obsidian vault path
OUTPUT_FILE = "/Path/To/Your/Vault/bookmarks.md"  # File for tagged bookmarks. Feel free to change the filename
UNTAGGED_FILE = "/Path/To/Your/Vault/bookmarks_untagged.md"  # File for untagged bookmarks
LOG_FILE = "sync_raindrop_to_obsidian.log"  # Log file name


# Raindrop API URLs
AUTH_URL = "https://raindrop.io/oauth/authorize"
TOKEN_URL = "https://raindrop.io/oauth/access_token"
API_BASE = "https://api.raindrop.io/rest/v1"

# Ensure the vault path exists
if not os.path.exists(VAULT_PATH):
    os.makedirs(VAULT_PATH)

# Log file path
script_dir = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(script_dir, LOG_FILE)

# Full paths to output files
output_file_path = os.path.join(VAULT_PATH, OUTPUT_FILE)
untagged_file_path = os.path.join(VAULT_PATH, UNTAGGED_FILE)


# Function to log messages
def log_message(message, success=True):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "SUCCESS" if success else "ERROR"
    with open(log_file_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"[{timestamp}] [{status}] {message}\n")
    print(f"[{timestamp}] [{status}] {message}")


# Authenticate and get a valid access token
def authenticate():
    token_data = load_token()
    if token_data:
        # Fallback: Calculate expiration if missing
        if "expiration" not in token_data:
            expires_in = token_data.get("expires_in", 3600)  # Default to 1 hour
            token_data["expiration"] = (datetime.now() + timedelta(seconds=expires_in)).timestamp()
            save_token(token_data)

        # Check if token is expired
        expiration_time = datetime.fromtimestamp(token_data["expiration"])
        if datetime.now() < expiration_time:
            log_message("Using saved access token.")
            return token_data
        else:
            log_message("Access token expired. Refreshing...")
            return refresh_access_token(token_data["refresh_token"])
    else:
        # Start OAuth2 flow
        log_message("No saved access token. Starting OAuth2 flow...")
        authorization_code = get_authorization_code()
        return get_access_token(authorization_code)


# Save token to a file
def save_token(token_data):
    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f)
    log_message("Access token saved.")


# Load token from a file
def load_token():
    try:
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "r") as f:
                return json.load(f)
        else:
            log_message("Token file not found.")
            return None
    except json.JSONDecodeError:
        log_message("Token file is corrupted or malformed.", success=False)
        return None


# Refresh access token
def refresh_access_token(refresh_token):
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    try:
        response = requests.post(TOKEN_URL, data=data)
        if response.status_code == 200:
            token_data = response.json()
            expires_in = token_data.get("expires_in", 3600)  # Default to 1 hour
            token_data["expiration"] = (datetime.now() + timedelta(seconds=expires_in)).timestamp()
            save_token(token_data)
            log_message(f"Access token refreshed successfully. Expiry: {expires_in} seconds.")
            return token_data
        else:
            log_message(f"Failed to refresh access token: {response.status_code} - {response.text}", success=False)
            return None
    except Exception as e:
        log_message(f"Error during token refresh: {e}", success=False)
        return None


# Fetch all collections from Raindrop.io
def fetch_collections(access_token):
    try:
        # Fetch top-level collections
        url_top = f"{API_BASE}/collections"
        headers = {"Authorization": f"Bearer {access_token}"}
        response_top = requests.get(url_top, headers=headers)
        response_top.raise_for_status()
        top_collections = response_top.json()["items"]
        log_message(f"Fetched top-level collections: {top_collections}")

        # Fetch sub-collections
        url_sub = f"{API_BASE}/collections/childrens"
        response_sub = requests.get(url_sub, headers=headers)
        response_sub.raise_for_status()
        sub_collections = response_sub.json()["items"]
        log_message(f"Fetched sub-collections: {sub_collections}")

        # Combine top-level and sub-collections
        all_collections = top_collections + sub_collections
        log_message(f"Combined collections: {all_collections}")

        # Composite collections and mapping from ID to composite ID
        composite_collections = {"-1": "Unsorted"}  # Special case for Unsorted
        id_to_composite = {"-1": "-1"}  # Map -1 directly to the composite ID

        # Helper function to generate a composite ID
        def generate_composite_id(path):
            return hashlib.md5(path.encode()).hexdigest()

        # Helper function to resolve the full path
        def resolve_full_path(collection, all_collections):
            # Ensure the collection is valid
            if not collection:
                log_message(f"Invalid collection passed to resolve_full_path: {collection}", success=False)
                return "Invalid Collection"

            # Extract parent ID from "parent" field
            parent_id = collection.get("parent", {}).get("$id") if collection.get("parent") else None
            log_message(f"Resolving path for '{collection.get('title', 'Unknown')}' (ID: {collection.get('_id', 'Unknown')}), Parent ID: {parent_id}")

            # Base case: If no parent ID, treat as top-level
            if not parent_id:
                log_message(f"No parent ID for '{collection.get('title', 'Unknown')}' (ID: {collection.get('_id', 'Unknown')}). Treating as top-level.")
                return collection.get("title", "Unknown")

            # Find the parent collection
            parent = next((c for c in all_collections if c["_id"] == parent_id), None)

            # Log whether the parent was found
            log_message(f"Parent found for '{collection.get('title', 'Unknown')}': {'Yes' if parent else 'No'}, Parent ID: {parent_id}")

            # If the parent exists, recursively resolve its full path
            if parent:
                parent_path = resolve_full_path(parent, all_collections)
                full_path = f"{parent_path}/{collection.get('title', 'Unknown')}"
                log_message(f"Resolved path for '{collection.get('title', 'Unknown')}': {full_path}")
                return full_path

            # If no parent is found, log a warning and treat as top-level
            log_message(f"Parent collection not found for '{collection.get('title', 'Unknown')}' (ID: {collection.get('_id', 'Unknown')}), Parent ID: {parent_id}. Treating as top-level.")
            return collection.get("title", "Unknown")

        for collection in all_collections:
            # Resolve the full path for each collection
            full_path = resolve_full_path(collection, all_collections)
            # Generate a composite ID for the full path
            composite_id = generate_composite_id(full_path)
            # Map the composite ID to the full path
            composite_collections[composite_id] = full_path
            # Map the collectionId to the composite ID
            id_to_composite[str(collection["_id"])] = composite_id

        log_message(f"Composite collections: {composite_collections}")
        return composite_collections, id_to_composite
    except Exception as e:
        log_message(f"Failed to fetch collections: {e}", success=False)
        raise

# Fetch bookmarks from Raindrop.io
def fetch_bookmarks(access_token):
    try:
        url = f"{API_BASE}/raindrops/0"
        headers = {"Authorization": f"Bearer {access_token}"}
        page = 0
        all_bookmarks = []

        while True:
            # Append the page number to the API request
            response = requests.get(f"{url}?page={page}", headers=headers)
            response.raise_for_status()
            data = response.json()

            # Extract bookmarks from the response
            bookmarks = data.get("items", [])
            log_message(f"Fetched {len(bookmarks)} bookmarks from page {page}.")

            # Add to the complete list of bookmarks
            all_bookmarks.extend(bookmarks)

            # Break if there are no more bookmarks
            if not bookmarks:
                break

            # Increment the page number for the next request
            page += 1

        log_message(f"Fetched a total of {len(all_bookmarks)} bookmarks.")
        return all_bookmarks
    except Exception as e:
        log_message(f"Failed to fetch bookmarks: {e}", success=False)
        raise

# Synchronize bookmarks to the appropriate markdown files
def save_bookmarks_to_files(bookmarks, composite_collections, id_to_composite):
    tagged_count = 0
    untagged_count = 0

    with open(output_file_path, "w", encoding="utf-8") as tagged_file, open(untagged_file_path, "w", encoding="utf-8") as untagged_file:
        for bookmark in bookmarks:
            title = bookmark["title"]
            link = bookmark["link"]
            excerpt = bookmark.get("excerpt", "No description available.")
            collection_id = str(bookmark["collectionId"])

            # Ignore Trash (-99) and Unsorted (-1) collections
            if collection_id in ["-1", "-99"]:
                log_message(f"Ignoring bookmark '{title}' in collection ID: {collection_id}")
                continue

            # Find the composite ID and path
            composite_id = id_to_composite.get(collection_id, None)
            collection_path = composite_collections.get(composite_id, "Uncategorized")

            log_message(f"Bookmark '{title}' -> Collection ID: {collection_id}, Composite ID: {composite_id}, Collection Path: {collection_path}")

            # Generate tags for sub-folders only, excluding top-level collections
            if collection_path != "Uncategorized" and "/" in collection_path:
                folder_tags = [
                    f"#{folder.replace(' ', '_').replace('/', '_')}"
                    for folder in collection_path.split("/")[1:]
                ]
                tags = " ".join(folder_tags)
            else:
                tags = None

            # Markdown entry
            markdown_entry = (
                f"## [{title}]({link})\n"
                f"**Collection**: {collection_path}\n"
                f"**Tags**: {tags if tags else 'None'}\n\n"
                f"{excerpt}\n\n"
                "---\n\n"
            )

            if not tags:  # If no valid tags, write to untagged file
                untagged_file.write(markdown_entry)
                untagged_count += 1
            else:  # Otherwise, write to the tagged file
                tagged_file.write(markdown_entry)
                tagged_count += 1

    log_message(f"Saved {tagged_count} tagged bookmarks to {output_file_path}.")
    log_message(f"Saved {untagged_count} untagged bookmarks to {untagged_file_path}.")



    
# Main script execution
if __name__ == "__main__":
    try:
        log_message("Script started.")
        token_data = authenticate()
        if not token_data:
            log_message("Authentication failed. Exiting.", success=False)
            exit(1)

        access_token = token_data["access_token"]

        # Fetch collections
        composite_collections, id_to_composite = fetch_collections(access_token)

        # Fetch bookmarks
        bookmarks = fetch_bookmarks(access_token)

        # Save bookmarks to markdown files
        save_bookmarks_to_files(bookmarks, composite_collections, id_to_composite)

        log_message("Script completed successfully.")
    except Exception as e:
        log_message(f"Script failed: {e}", success=False)

