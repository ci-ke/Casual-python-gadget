# Update this to match your data directory
ZOTERO_STORAGE = r"C:\Users\DTK\Zotero"
ZOTERO_STORAGE_FILES = r"D:\Workspace\OneDrive\vardtk\OneDrive\document\文献"

import sqlite3
import os

dbh = sqlite3.connect(ZOTERO_STORAGE + "/zotero.sqlite")

# Query all attachments
c = dbh.cursor()
c.execute(
    'select path from itemAttachments where contentType = "application/pdf" and linkMode = 2'
)

# Fetching all dirs as a set
files = dict(
    zip(
        [f.lower() for f in os.listdir(ZOTERO_STORAGE_FILES)],
        os.listdir(ZOTERO_STORAGE_FILES),
    )
)

for key in c.fetchall():
    filename = key[0].split(':')[1].lower()
    if filename in files:
        del files[filename]

# Loop over the non-existing files
orphans = sorted(files.values())
print("\n".join(orphans))
