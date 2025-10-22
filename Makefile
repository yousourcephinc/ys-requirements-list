sync:
	pip install -r requirements.txt
	python scripts/sync_notion.py

mcp:
	pip install -r requirements.txt
	python mcp/guides_mcp.py

test-mcp:
	python tests/test_guides_mcp.py
