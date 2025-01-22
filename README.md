# Raindrop.io to Obsidian Sync Script

This script enables seamless synchronization of your **Raindrop.io** bookmarks to markdown files in your **Obsidian** vault. Bookmarks are categorized and tagged automatically based on their Raindrop.io collections, making it easier to organize and reference them in Obsidian.

---

## Features

- **Sync Bookmarks**: Automatically copies all bookmarks from Raindrop.io to a markdown file of your choice in your Obsidian vault.
- **Automatic Tagging**: Creates tags for each bookmark based on the Raindrop.io collection name and folder hierarchy.
  - Example: A bookmark in `Bookmark Bar/Personal/Recipes` is tagged as `#Bookmark_Bar #Personal #Recipes`.
- **Unsorted Bookmarks Handling**: Bookmarks in the `Unsorted` collection or `Trash` folder are stored in a separate file (default: `bookmarks_untagged.md`).
- **Detailed Logging**: Comprehensive logging to help troubleshoot and monitor the synchronization process.

---

## Requirements

- **Python 3.7+**
- **Raindrop.io API Credentials**
  - [Create an OAuth app in Raindrop.io](https://app.raindrop.io/settings/integrations) to obtain your `CLIENT_ID` and `CLIENT_SECRET`.
- An existing **Obsidian vault**.

---

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/raindrop-to-obsidian.git
   cd raindrop-to-obsidian

2. Install required dependencies:
    ```bash
    pip install -r requirements.txt

3. Set up your Raindrop.io API credentials:
    Edit the CLIENT_ID, CLIENT_SECRET, and REDIRECT_URI in the script.

4. Update file paths:
    Set VAULT_PATH, OUTPUT_FILE, and UNTAGGED_FILE to the appropriate locations in your Obsidian vault.

## Usage
Run the script to sync bookmarks:

    python Obsidian_Raindrop_sync.py

## Key Operations
* Tagged Bookmarks: Saved to the file specified by OUTPUT_FILE (e.g., bookmarks.md).
* Untagged Bookmarks: Saved to the file specified by UNTAGGED_FILE (e.g., bookmarks_untagged.md).
* Real-Time Updates: Automatically syncs changes from Raindrop.io, including bookmark deletions or movements


## Example
Tagged Bookmark Entry
```bash
## [Delicious Recipe](https://example.com/recipe)
**Collection**: Bookmark Bar/Personal/Recipes
**Tags**: #Bookmark_Bar #Personal #Recipes

A delightful recipe for your favorite dish.
```

Untagged Bookmark Entry
```bash
## [Interesting Article](https://example.com/article)
**Collection**: Uncategorized
**Tags**: None
```

## Logging
Logs are saved to sync_raindrop_to_obsidian.log in the script's directory, providing detailed information about the synchronization process, including:
  * Successful API calls
  * Errors or issues
  * Bookmark updates or deletions

## Contribution
Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

## License
This project is licensed under the GPL3.

## Acknowledgements
Raindrop.io API Documentation
Obsidian for its incredible markdown-based organization platform.


