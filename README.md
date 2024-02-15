truefinalsBot

Based on Nathan's work here: https://github.com/NRS048/Discord-TrueFinals-Webhook

This script integrates truefinals.com, discord and an OBS stream overlay.
The true finals API is polled for called, active and compelted matches.
A discord channel is notified via a webhook.
Data is witten to a json file for use in robot.html as a stream overlay.

True Finals API Docs: https://truefinals.com/docs.html
Discord webhook docs: https://discord.com/developers/docs/resources/webhook

TODO
- Get clock info from the arena timer.

KNOWN ISSUES
- This script is designed for only one match to be active at a time. There are issues with multiple matches being active at once.
