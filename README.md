# export-private-deepwiki

> **Languages / 言語:** [English](README.md) | [日本語](docs/README_ja.md)

## 1. Overview

`export-private-deepwiki` is a CLI tool for locally saving DeepWiki content (repository wikis and chat logs) in Markdown format.
This project enables users to easily export information from DeepWiki and manage/utilize it in their local environment.

### 1.1. Purpose

1. Enable retrieval of DeepWiki chat logs in Markdown format.
2. Enable retrieval of DeepWiki Wiki content in Markdown format.
3. Properly convert and save Mermaid diagrams for reuse.

## Support for Private DeepWiki (Private Wiki on Devin)

Previously, only public DeepWiki was supported, but we've added a mode that can also retrieve private pages requiring login using Playwright's persistent context.

Key Points:
- Instead of the existing request-based approach, we launch a real browser (Chromium/Chrome) and access pages using logged-in sessions (Cookie/LocalStorage).
- For the first time, display the browser in headed mode (--headed) to complete login. Subsequently, by specifying the same user data directory (--user-data-dir), the login state will be maintained.
- While you can directly use existing Chrome profiles on macOS, we recommend creating a dedicated directory due to risks of concurrent startup and profile corruption.

### Usage

Prerequisites:
- macOS
- Python 3.12+
- Playwright package (included in this project's dependencies)

Setup Example:
1) Install dependencies
   ```bash
   pip install -r requirements.lock
   ```

2) Playwright browsers are not essential as we use system Chrome, but if using Chromium, `playwright install` may be required.

#### First Run (Manual Login)

Enable authentication mode and perform manual login with the following command:

```bash
python -m src.interface.cli wiki \
  "https://app.devin.ai/wiki/<your org>/<your repo>" \
  -o ./output \
  --auth \
  --headed \
  --browser-channel chrome \
  --user-data-dir "$HOME/.deepwiki-playwright-profile" \
  --manual-login \
  --wait-selector "#codebase-wiki-repo-page" \
  --wait-timeout-ms 300000
```

**Execution Steps:**
1. Complete login when the browser launches following these steps:
   - **For GitHub login**: Navigate to github.com if not already logged in, enter your credentials or use SSO
   - **For Devin login**: Navigate to app.devin.ai, sign in with your GitHub account or other authentication method
   - **Important**: Make sure you're logged into both GitHub AND Devin, as Devin often requires GitHub authentication to access private repositories
2. After completing login to both services, return to the terminal and press **Enter** to continue scraping

**Key Options:**
- `--auth`: Use persistent context to maintain login state
- `--headed`: Display browser (required for initial login)
- `--manual-login`: Confirm manual login completion before starting scraping
- `--browser-channel chrome`: Use system Google Chrome
- `--user-data-dir`: Directory to save login state (recommended to use any new directory)
- `--wait-selector`: Wait until specific element appears (for Devin)
- `--wait-timeout-ms`: Wait timeout (milliseconds)

#### Second Run and Beyond (Reuse Logged-in Profile for Automation)

Since the login state is saved, you can run automatically with the following command:

```bash
python -m src.interface.cli wiki \
  "https://app.devin.ai/wiki/<your org>/<your repo>" \
  -o ./output \
  --auth \
  --browser-channel chrome \
  --user-data-dir "$HOME/.deepwiki-playwright-profile" \
  --wait-selector "#codebase-wiki-repo-page" \
  --wait-timeout-ms 180000
```

**Note:**
- `--headed` and `--manual-login` are unnecessary (automatically runs headless)
- Reduced wait time (300s→180s)

#### Using Existing Chrome Profile on macOS (Advanced Users)

```bash
python -m src.interface.cli wiki \
  "https://app.devin.ai/wiki/<your org>/<your repo>" \
  -o ./output \
  --auth \
  --browser-channel chrome \
  --user-data-dir "$HOME/Library/Application Support/Google/Chrome"
```

**Warning:** Concurrent startup of existing Chrome with the same profile risks conflicts and corruption. Close Chrome in use before execution or use a dedicated profile directory.

#### Similarly Applicable to Chat Pages

**First time (manual login):**
```bash
python -m src.interface.cli chat \
  "<chat page URL>" \
  -o ./output \
  --auth \
  --headed \
  --browser-channel chrome \
  --user-data-dir "$HOME/.deepwiki-playwright-profile" \
  --manual-login
```

**Second time and beyond (automation):**
```bash
python -m src.interface.cli chat \
  "<chat page URL>" \
  -o ./output \
  --auth \
  --browser-channel chrome \
  --user-data-dir "$HOME/.deepwiki-playwright-profile"
```

#### Troubleshooting

**If `--browser-channel chrome` causes errors:**
- Verify that Chrome is installed on the system
- Alternative 1: Install Playwright's chrome channel (optional)
- Alternative 2: Use `--browser-channel chromium` (may require `python -m playwright install chromium`)

**Login Issues:**
- **GitHub Authentication Required**: Even for Devin wikis, you may need to log into GitHub first since Devin often uses GitHub for repository access authentication
- **Multiple Login Steps**: For private repositories, ensure you're logged into both:
  1. GitHub (github.com) - for repository access permissions
  2. Devin (app.devin.ai) - for the Devin platform itself
- **Session Timeout**: If scraping fails after successful login, the session may have expired. Re-run with `--manual-login` to refresh authentication

**About Navigation Extraction:**
- Even in UIs without sidebar navigation, fallback extraction of links under `/wiki/{org}/{repo}/` from the main content is performed
- Accuracy improves when the first URL opened is the repository's top Wiki (equivalent to table of contents)

### Known Limitations and Future Improvements
- When images in Wiki content are under authentication and cannot be saved locally, they remain referenced as external URLs in Markdown. Future plans include adding image downloads using Playwright page context and rewriting to local references.
- If the DOM structure on Devin changes, selector adjustments may be necessary.

## 2. Command Line Specification

The basic command syntax is as follows:
```bash
python -m src.interface.cli <subcommand> <URL> [-o <output base directory>]
```

* `<subcommand>`: Specify `wiki` or `chat`.
* `<URL>`: Specify the URL of the target DeepWiki page.
* `-o <output base directory>` (optional): Specify the base directory where Markdown files and images will be output. Default is `./output`.

**Examples:**

* **Repository Wiki Retrieval**:
    ```bash
    python -m src.interface.cli wiki https://deepwiki.com/yourgroup/yourrepo
    ```
    Output destination: `./output/wiki/yourgroup/yourrepo/`

* **Chat Log Retrieval**:
    ```bash
    python -m src.interface.cli chat https://deepwiki.com/search/yourchatid
    ```
    Output destination: `./output/chat/yourchatid/`

* **Repository Wiki Retrieval with Custom Output Base Directory**:
    ```bash
    python -m src.interface.cli wiki https://deepwiki.com/yourgroup/yourrepo -o /path/to/custom_output
    ```
    Output destination: `/path/to/custom_output/wiki/yourgroup/yourrepo/`

**Output Directory Structure Example:**

```
output/  # Default output directory
    wiki/
        yourgroup/
            yourrepo/
                1-overview.md
                2-details.md
                images/
                    diagram1.svg
    chat/
        yourchatid/
            chat.md
            images/
                diagram1.svg
```

## 3. Reference

This project is based on [deepwiki-to-md](https://github.com/suwa-sh/deepwiki-to-md) and modified as export-private-repository.
