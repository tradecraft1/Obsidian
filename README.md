# Obsidian
Scripts and tools for Obsidian

obsidian_raindrop_sync.py -- This script takes your Raindrop.io bookmarks and copies them to a file in your Obsidian vault. 

Copies all boomarks to a file of your choosing
Creates tags for each bookmark based on the Collection name and child folders
    A bookmark in Bookmark Bar/Personal/Recipes would be give the tags of #Bookmark_Bar #Personal #Recipes
If a bookmark is in the Raindrop.io Unsorted collection or the Trash folder it will be added to the bookmarks_untagged.md file (you can change the name of the file)
If a bookmark is moved or deleted in Raindrop.io it will be updated in Obsidian to match
There is a ton of logging enabled in the script to help ensure things are working as anticipated 
