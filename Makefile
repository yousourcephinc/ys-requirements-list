sync:
	pip install -r requirements.txt
	python sync_notion.py

mcp:
	pip install -r requirements.txt
	python guides_mcp.py

test-mcp:
	python test_guides_mcp.py
