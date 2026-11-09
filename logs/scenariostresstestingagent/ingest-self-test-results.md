# Self-test, step 2: scenariostresstestingagent

37 of 37 checks came out as expected. A check passes only if what was observed is what was expected; the deliberate breaks are meant to be caught. Every check ran on a temporary copy of the tree.

| Check | Expected | Observed | Result |
|---|---|---|---|
| 2 run on the sample corpus: exit 0 and the four files written | exit 0; 4 files under ingest/ | exit 0; 4 new files | as expected |
| 2 every request is ingested: 12 clean, 10 defective, no rejects | 12; 10; 0; 0 | 12; 10; 0; 0 | as expected |
| 2 the recipe's six step-2 output fields are present in both files | records, source_name, source_type, fetched_at, sample_mode, rejects | all present | as expected |
| 2 sample_mode is true and fetched_at is the pinned clock | true; 2026-11-09T00:00:00+00:00 | True; 2026-11-09T00:00:00+00:00 | as expected |
| 2 each record is its fixture, unchanged: body equal, SHA-256 equal to the manifest's | 22 of 22 equal | 22 of 22 equal | as expected |
| 2 record ids are unique and listed in order | 22 unique, sorted per folder | 22 unique | as expected |
| 2 a defective request ingests like any other (valid JSON); its shape is step 3's work | 10 read, none judged here | 10 read | as expected |
| 2 the four sources: webhook available, chat skipped, Alpha Vantage and Groq approval-required | Webhook Trigger available; When chat message received skipped; Fetch_Data approval-required; Groq Chat Model approval-required | Fetch_Data approval-required; Groq Chat Model approval-required; Webhook Trigger available; When chat message received skipped | as expected |
| 2 every source carries a reason, and none was contacted or approved | reasons; live_call_performed false; approved_for_live_action false | yes | as expected |
| 2 the handoff condition is met and no problems are listed | true; none | True; [] | as expected |
| 2 credential names are reported as not set when the environment has none | False; False | ALPHA_VANTAGE_API_KEY False; GROQ_API_KEY False | as expected |
| 2 only files under data/raw/<slug>/ingest/ were created | 4 files, all under ingest/ | 4 files; outside: [] | as expected |
| 2 idempotent: a second run with the clock pinned gives the same bytes | identical | identical | as expected |
| 2 --no-write writes nothing | exit 0; no new file | exit 0; 0 new | as expected |
| 2 --sample is accepted and changes nothing; an unknown flag is refused by argparse (exit 2) | exit 0; exit 2 | exit 0; exit 2 | as expected |
| 2 the script imports nothing that can reach a network or start a process | none of socket, urllib, http, requests, ssl, subprocess, ftplib, smtplib, asyncio, shutil | imports: ['__future__', 'argparse', 'datetime', 'hashlib', 'json', 'os', 'pathlib', 're', 'sys', 'typing'] | as expected |
| 2 the environment is only asked whether a name is set: every os.environ.get sits inside bool(), none is read by subscript | bool(os.environ.get(...)) only | 1 get call(s), all inside bool(): True; subscripts: 0 | as expected |
| 2 with both credentials set, each is reported as set | True; True | True; True | as expected |
| 2 the credential values appear in no output file and not on the screen | no value anywhere | found: none | as expected |
| 2 break caught: a fixture changed by one letter | exit 1; 'differs from the SHA-256 frozen' | exit 1; reason named | as expected |
| 2 the changed fixture is left out of the records and named in rejects; the other 11 still ingest | 11 records; 1 reject named c01 | 11 records; rejects ['c01-tech-crash-semiconductor-heavy.json'] | as expected |
| 2 break caught: a fixture deleted | exit 1; 'listed in the frozen manifest but not on disk' | exit 1; reason named | as expected |
| 2 break caught: an unlisted fixture added | exit 1; 'not in the frozen manifest' | exit 1; reason named | as expected |
| 2 break caught: a fixture that is not JSON, with the manifest updated to match | exit 1; 'not valid JSON' | exit 1; reason named | as expected |
| 2 break caught: the manifest removed | exit 1; 'frozen manifest is missing' | exit 1; reason named | as expected |
| 2 break caught: the run envelope says mode live | exit 1; 'sample mode only' | exit 1; reason named | as expected |
| 2 a refused scope writes nothing | no ingest folder | ingest folder exists: False | as expected |
| 2 break caught: the run envelope allows network | exit 1; 'network' | exit 1; reason named | as expected |
| 2 break caught: the run envelope allows live calls | exit 1; 'live_calls' | exit 1; reason named | as expected |
| 2 break caught: the run envelope removed | exit 1; 'run envelope is missing' | exit 1; reason named | as expected |
| 2 break caught: the declared workflow removed | exit 1; 'workflow JSON is missing' | exit 1; reason named | as expected |
| 2 break caught: the workflow declares no webhook trigger | exit 1; 'declares no webhook trigger' | exit 1; reason named | as expected |
| 2 a credentialed node of an unrecognised type is held back as approval-required, never passed as available | exit 0; Save Results approval-required; reason says 'unrecognised' | exit 0; approval-required; True | as expected |
| 2 an HTTP request to another host is still approval-required, with no credential name guessed | approval-required; 'none known' | approval-required; none known | as expected |
| 2 an approval record is noticed, but sample mode stays sample: still approval-required, nothing performed | approval_record_present true; statuses unchanged; live_call_performed false | True; ['available', 'skipped', 'approval-required', 'approval-required']; [False, False, False, False] | as expected |
| 2 the recipe's Flags cell for this step lists exactly the flags the script implements | --no-write, --now, --repo, --sample, --sample-dir, --workflow | --no-write, --now, --repo, --sample, --sample-dir, --workflow | as expected |
| 2 the recipe's Script Locations row points at this script, and the file exists | scripts/ingest/scenariostresstestingagent-ingest-inputs.py | present | as expected |
