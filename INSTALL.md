# Quick Install Guide

## For GitHub Copilot Users

The implementation guides are now available directly through GitHub Copilot in VS Code with a zero-setup configuration.

### Prerequisites

1.  **Visual Studio Code** with the **GitHub Copilot** extension installed and enabled.
2.  You are part of the `yousourcephinc` GitHub organization.

### Setup

**It's automatic!**

This repository contains a `.vscode/settings.json` file that configures Copilot to connect to the hosted Implementation Guides server.

1.  **Open this repository (`ys-requirements-list`) in VS Code.**
2.  If prompted, **trust the workspace** to allow the settings to be applied.
3.  Reload the VS Code window (Go to `View > Command Palette` or press `Cmd+Shift+P`, then type `Developer: Reload Window`).

That's it! The tool is now active.

### Usage

In the GitHub Copilot Chat panel, you can now use `@workspace` to access the guides:

*   **`@workspace What guide divisions are available?`**
*   **`@workspace Search for authentication guides`**
*   **`@workspace Recommend payment guides at Introduction 1 level for SE`**

See [COPILOT_SETUP.md](docs/COPILOT_SETUP.md) for more detailed usage examples and commands.

---

## Documentation

-   [GitHub Copilot Setup](docs/COPILOT_SETUP.md) - Detailed Copilot integration guide.
-   [REST API Documentation](docs/README_MCP.md) - Guide for direct API usage.
-   [Deployment Guide](docs/DEPLOYMENT.md) - Information about the backend infrastructure.
