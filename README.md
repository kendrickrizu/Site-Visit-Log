# Site Visit Log

A small custom Frappe app with one DocType, "Site Visit Log", built as an onboarding task. It has server-side validation in Python, a client-side script in JavaScript, and tests.

Most of my time went on setting up Frappe on Windows rather than the code itself. I got stuck at several points, which are listed below along with how I fixed them.

## What I built

- A custom Frappe app, `site_visit_log`, on a local Frappe v15 bench, running in Ubuntu (WSL) on Windows
- A Site Visit Log DocType with Client Name, Visit Date, Purpose, Follow-up Needed (checkbox), Follow-up Date, and a read-only Status. Client Name, Visit Date and Purpose are mandatory.
- Server-side rules in `validate` (`site_visit_log.py`):
  - Status is set to "Follow-up Pending" when the box is ticked, otherwise "No Follow-up"
  - Follow-up Date is required when follow-up is needed
  - Follow-up Date cannot be before Visit Date
  - Follow-up Date is rejected when follow-up is not needed
- Client script (`site_visit_log.js`): Follow-up Date is shown and required only when Follow-up Needed is ticked, and it is cleared when the box is unticked. It runs on both `refresh` and the checkbox change, so saved records display correctly when reopened.
- Four tests in `test_site_visit_log.py`: Status flips in both directions, plus one test for each server rule.
- A module named "Site Visit" to hold the DocType.

I added Follow-up Date and Status myself so the two pieces of logic had something to act on.

## How I worked

I used Claude AI, majorly for guidance because the framework is new to me. It walked me through setup step by step and helped me debug errors I could not solve myself. For the code, I wrote the logic myself from descriptions of what the Python and JS should do, and used AI to correct my syntax errors since Python is not my core programming language. I learnt some Python syntax while at it. I wrote the validate rules, the client script and this README myself, and used AI to review them and to explain what the tests do.

## What I learned

- Bench, site and app are different things. The bench is the workspace, a site is one database plus config, and an app is the code. `bench new-app` creates the code, but `bench install-app` is what switches it on for a site.
- Frappe generates a lot from one DocType: the table, form, list view and API.
- `validate` runs before every save, whether the record comes from the form or the API.
- Python runs on the server and JS runs in the browser. A rule that exists only in JS is skipped by anyone using the API, so the Python rules are the real enforcement and the JS is a convenience.
- Code refers to fields by fieldname, not label, and fieldnames cannot contain hyphens. I had an issue with that on the Follow-up Needed and Follow-up Date fields while trying to save, so I set the fieldnames manually.
- WSL does not start MariaDB by itself, so after a restart I start it before `bench start`, the way I would start a database before running a React and Express project.

### What changing a fieldname does to existing data

- **What I tried:** I created a throwaway DocType with one field (`old_name`), saved a record, then renamed the fieldname to `new_name`, saved, and ran `bench migrate`.
- **What I saw in the database table:** Frappe did not rename the column. It kept `old_name` and added `new_name` beside it, and the two were never merged. The record I saved before the rename still had its value in `old_name`, with `new_name` empty, while a record saved after the rename went into `new_name`. The form only reads the current fieldname, so the old record shows an empty field even though its value is still in the database.
- **What I would do if the DocType already had a thousand records:** all thousand would look empty on the form while their values sat in the old column. I would write a patch, listed in `patches.txt`, that copies the values from the old column into the new one for every existing record. Frappe runs a patch once on every site that updates the app, so every installation gets the same fix. Frappe's `rename_field` utility does this, and the old column can be dropped afterwards.

### Design choice: where the follow-up check sits

I put all the date rules inside the `if follow_up_needed` check, so unticked records skip them. That left one gap: an unticked record with a stale follow-up date. I closed it by rejecting that on the server and by clearing the date in the browser when the box is unticked.

## Where I got stuck

Setup:

1. Docker Desktop would not start because of a virtualization error, so I used the standard Ubuntu install instead.
2. WSL was not enabled, and after enabling it, it needed a kernel update.
3. Ubuntu's default Python (3.14) is too new for Frappe v15, so I used pyenv to install Python 3.11.
4. `pyenv.run` was unreachable from my network, though GitHub worked, so I cloned pyenv from GitHub instead.
5. I installed Node 18 through nvm, plus Yarn, because Frappe v15 expects that version.
6. I typed bench commands inside the MariaDB shell by mistake, which did nothing.
7. After a failed first attempt, the site folder was left behind and the site's database user gave an access-denied error, so I dropped and recreated the site.
8. After a restart, `install-app` failed with "Connection refused" on port 3306 because MariaDB was not running. Starting the service fixed it.

Issues raised in code review, and how I fixed them:

9. **Typo in a fieldname.** A field was named `pupose`, in both the fieldname and the label. I corrected both to `purpose` and checked the rest of the code for the old name. I also worked out what a fieldname change does to existing data (see above).
10. **README said Status was read-only, but the DocType did not set it.** I set Read Only on the field and checked the DocType JSON against what I had written. This time I confirmed it says `"read_only": 1` before saying so.
11. **The follow-up date was required only in the browser.** A record created through the API would skip the rule. I added `frappe.throw` checks in `validate` so the rule holds on the server, plus a rule that the follow-up date cannot be before the visit date, and tests that prove both.
12. **Module named "My First App".** I gave it a meaningful name, "Site Visit". Doing this taught me that the module name has to match in three places (`modules.txt`, the module folder and the Module Def), and that the Module Def's App Name must be set, or Frappe writes the DocType files into its own core app. When that happened I moved the files into my app, fixed the nesting and restored Frappe's `modules.txt` with `git restore`.
13. **Hyphen in a fieldname.** I labelled a field "Follow-up Needed" and Frappe rejected `follow-up_needed` as a fieldname. Labels can have hyphens, fieldnames cannot.
14. **A logic bug in my first version of `validate`.** An `else` was attached to the wrong `if`, so a valid follow-up date was still rejected, and the comparison used today's date instead of the visit date. Tracing each case by hand and running all the scenarios found it.

## Running it

```bash
sudo service mariadb start
sudo service redis-server start
cd ~/frappe-bench
bench start
```

Then open http://dev.localhost:8000/app and log in as Administrator.

To install it on another bench:

```bash
bench get-app <this-repo-url> --branch main
bench --site <your-site> install-app site_visit_log
```

To run the tests:

```bash
bench --site <your-site> set-config allow_tests true
bench --site <your-site> run-tests --app site_visit_log
```