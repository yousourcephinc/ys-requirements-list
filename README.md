# ys-requirements-list
Repository of requirements list, implementation guides organized by software modules and maturity levels.

## Notion Sync

This repository includes a helper script to sync guides from a Notion database into a `guides/` folder.

1. Create a `.env` file with these variables:

```
NOTION_API_KEY="secret_..."
NOTION_DATABASE_ID="..."
```

2. Install deps and run:

```bash
pip install -r requirements.txt
python sync_notion.py
```

The script will create a `guides/` directory with one subfolder per module and guide.
# ys-requirements-list
Repository of requirements list, implementation guides organized by software modules and maturity levels; 
