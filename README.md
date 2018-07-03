# Shmmywiki Auto-results

### Table of contents
* [Introduction](#introduction)
* [Progress](#progress)
* [Dependencies](#dependencies)
* [Project structure](#project-structure)
* [Usage](#usage)

### Introduction

Auto-results is a set of tools developed for the Shmmywiki platform. The desired functionality is to:
* Extract course exam dates from the schedule PDF file provided by the ECE School website
* Fetch shmmy forum posts where course exam results are announced by users
* Use keyword matching on each post's content to find the corresponding course
* Generate wiki code for results table with exam and announcement dates, difference in days between them and URL of announcement post as columns
* Post generated table to wiki using a pywikibot

### Progress

The project is still experimental with many core features missing or poorly implemented, such as:
* A better keyword matching algorithm, switching from a greedy to a more clever approach (e.g. keyword trees).
* Different course groups may have same exam dates but usually have different results dates. In this case, consider them as separate courses and implement keyword matching for each group.

### Dependencies

[Pywikibot](https://www.mediawiki.org/wiki/Manual:Pywikibot) is used to automate the editing of Shmmywiki pages. Installation steps:
* Download pywikibot by visiting the above link and decompress it to some `/path/to/folder`.
* Add that folder to your `PYTHONPATH` (e.g. add the line `export PYTHONPATH=${PYTHONPATH}:/path/to/folder` to `~/.bashrc`).
* `cd /path/to/folder`.
* Run `python pwb.py generate_family_file` and type the URL to the home page of your wiki in the prompt.
* Run `python pwb.py generate_user_files` and type the credentials to an account of that wiki in the prompt.
* Copy the generated `user-config.py` to the root folder of this repository.

### Project structure

The project is organized as follows:
* root folder:
    * `main.py`: Entry point. Usage: `python main.py [config id] [action,...]`. Config id is documented below in `config.json`. Actions are separated by comma without any space between them and may be any of the following:
        * `search`: Search for courses that match a query.
        * `build_keywords`: Navigate through the keyword database and add/edit/remove keywords.
        * `courses_update`: Parse the `db/courses.csv` file and include new courses in database.
        * `schedule`: Parse the schedule file of the selected configuration and update exam dates.
        * `print_schedule`: Print each course along with its exam date for the selected configuration.
        * `results`: Fetch posts from shmmy forum and update exam results dates.
        * `print_results`: Print each course along with its results date for the selected configuration.
        * `wiki`: Get exam and result dates from database and post them in wiki format to shmmywiki.
        * `export_wiki`: Get exam and result dates from database and save them in wiki format to `outputs/:id/export_wiki.txt` without posting them.
        * If no action argument is given, `results,wiki` is assumed.
    * `config.json`: Contains configuration parameters for all the exam periods that are managed by the application. Each configuration entry has an ID (`config id`) given by its key and a configuration dictionary. The dictionary needs to have the following keys:
        * `folder`: The folder in `outputs/` in which the outputs will be stored.
        * `schedule_file`: The pathname in `schedule/` folder for the schedule PDF file of this configuration.
        * `wiki_title`: The title of the shmmywiki article in which the results will be posted.
        * `forum_thread`: The thread to which the results for this exam period are posted by the users.
    * `config.py`: Module for accessing the configuration parameters of an exam period from `config.json`.
    * `utils.py`: Contains helper text functions for the keyword matching algorithm and for the extraction of exam results dates from forum posts.
* `db/`
    * `keywords.py`
        * `get()`: Returns the keyword dictionary parsed from `keywords.json`, which matches each keyword with a list of course IDs.
        * `print()`: Prints the keyword dictionary with `pprint`.
        * `write(j)`: Exports the updated keyword dictionary to `keywords.json`.
        * `match(text)`: Parse `text` and find the matching courses.
    * `courses.py`
        * `get()`: Returns the course dictionary parsed from `courses.csv`.
        * `print()`: Prints the course dictionary with `pprint`.
        * `update()`: Reads `courses.csv` and updates `keywords.json` to include any newly added courses. Each course has at least its title as a keyword in `keywords.json`.
    * `search_with_keyword.py`: Command-line module to search for courses that match a query.
    * `build_keywords.py`: Command-line module to navigate through keywords and perform add/edit/remove operations on them.
    * `keywords.json`: Contains the aforementioned keyword dictionary in JSON format.
    * `courses.csv`: A CSV that contains all course data. The columns of the CSV are [id, title, semester, flow, wiki title] in order.
* `results/`
    * `results.py`
        * `get()`: Returns result dates and URLs for the courses in `outputs/:id/results.json`, possibly overwritten by `outputs/:id/results.manual.json`.
        * `write(j)`: Writes a result dates and URLs dictionary to `outputs/:id/results.json`.
        * `fetch()`: Fetches result dates and URLs from forum posts and exports them to `outputs/:id/results.json`. Keeps the ID of last accessed post to calculate how many new entries there have been.
        * `getLast()`: Gets the ID of the most recently accessed shmmy forum post.
* `schedule/`
    * `schedule.py`
        * `get()`: Returns course exam dates for the courses in the schedule file, possibly overwritten by `outputs/:id/dates.manual.json`.
        * `write(j)`: Writes a course exam dates dictionary to `outputs/:id/dates.json`.
        * `parse()`: Parses schedule PDF file and exports course exam dates to `outputs/:id/dates.json`.
    * PDF schedule files are also stored here.
* `wiki/`
    * `wiki.py`
        * `get()`: Returns the exported wiki code of the results from `outputs/:id/export_wiki.txt`.
        * `export()`: Combines `dates.json` and `results.json` data to generate wiki code for results table and stores it in `outputs/:id/export_wiki.txt`.
        * `save()`: Logs in to Shmmywiki as ShmmywikiBot user and posts the generated table to the page of the selected exam period.
* `outputs/`: All the script outputs are stored here. Each exam period has its own directory named after its configuration ID. Each directory contains the following files:
    * `dates.json`: JSON that maps course IDs to exam dates. It is generated by `schedule/schedule.py`.
    * `dates.manual.json`: User generated JSON file that can be used to overwrite the course dates, in case of any wrong output.
    * `results.json`: JSON that maps course IDs to result dates and result URLs. It is generated by `results/results.py`.
    * `results.manual.json`: User generated JSON file that can be used to overwrite the result dates, in case of any wrong output.
    * `results.ignore.json`: User generated JSON array that can be used to ignore all shmmy forum posts whose ID is in the array.
    * `export_wiki.txt`: Wiki code for the results table. It is generated by `wiki/wiki.py`.
    * `last_result_id.txt`: The ID of the last announcement forum post is stored here, so that `results/results.py` can know whether new course results have been announced.
    * `pdf_texts.txt`: Debug file generated by `schedule/schedule.py` that contains all textboxes parsed from the PDF along with their coordinates and any possible course title matches.
    * `pdf_svg.html`: Debug SVG file that models how `schedule/schedule.py` views the schedule tables as a grid.

### Usage

To add a new exam period:
1. Include target schedule PDF in the `schedule/` folder.
1. Add a configuration entry in `config.json` with a unique key as the `config id` and the fields of `folder`, `schedule_file`, `wiki_title`, `forum_thread` as described above.

Now you can schedule `python main.py [config id]` to run periodically, so that new posts will be automatically fetched and the wiki page will be updated.