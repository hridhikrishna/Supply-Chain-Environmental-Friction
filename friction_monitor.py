name: Supply Chain Friction Automation

on:
  schedule:
    - cron: '0 */3 * * *'
  workflow_dispatch:

jobs:
  run-monitor:
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install requests pandas folium tabulate

      - name: Run friction script
        run: |
          python friction_monitor.py

      - name: Publish Alert Summary to GitHub Dashboard
        run: |
          if [ -f alert_summary.md ]; then
            cat alert_summary.md >> $GITHUB_STEP_SUMMARY
          fi

      - name: Commit and push updated map
        run: |
          if [ -f index.html ]; then
            git config --global user.name "github-actions[bot]"
            git config --global user.email "github-actions[bot]@users.noreply.github.io"
            git add index.html logistics_friction_log.csv
            git commit -m "Auto-update friction map and metrics [skip ci]" || echo "No changes to commit"
            git pull origin main --rebase || echo "Rebase not needed"
            git push
          else
            echo "index.html not found, skipping commit."
          fi
