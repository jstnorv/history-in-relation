# History in Relation
#### Video Demo: TBD — add your recorded walkthrough URL here
#### Description:
History in Relation is a lightweight Flask web application built to help users explore how the history of the lands of contemporary Ukraine connects to larger regional and global historical developments. Rather than treating Ukrainian history as a single isolated national story, the project presents it as a network of relationships: between ancient steppe cultures and language families, medieval states and trade routes, imperial powers and political memory, and modern conflict and international order. The app brings together a curated set of historical topics, a searchable index, and explanatory connections that help users see how one topic leads naturally into another.

The project was designed as an educational tool for a beginner-to-intermediate audience. Its goal is not to replace scholarly research or present a final and exhaustive account of Ukrainian history. Instead, it is a structured, readable entry point that encourages curiosity and comparison. Each topic includes a brief overview and a set of related connections, and the app presents those relationships in a way that is easy to navigate without overwhelming the reader. It is especially useful for illustrating the idea that historical change is often shaped by exchange, migration, conflict, diplomacy, language, and social adaptation rather than a single linear timeline.

The app’s content is built around a set of curated topics such as Yamna, Indo-European languages, Scythia, Rus, the Soviet Union, Vikings, Byzantium, and the Russo-Ukrainian war. These topics are intentionally arranged to support chronological and thematic exploration. The homepage presents a map of Ukraine beside an introductory explanation of the project’s broader concept. Visitors can browse all topics, search for terms, and click through to each topic page to read more detail and follow linked connections.

## What the project does

At the center of the project is a Flask app that serves a homepage and individual topic pages. The homepage shows a search bar and a grid of historical topics, each card summarizing the topic and linking to a deeper explanation. When a user clicks a topic, the app renders a full page with a long-form explanation and a list of associated topics. These relationships include a label describing the type of connection, a short explanation of why it matters, and a source citation pointing to an external reference or scholarly source.

One of the important design decisions was to make the historical content visible, legible, and adaptable. The app does not rely on a complicated database model or a production-level content-management workflow. Instead, it keeps the structure simple and readable: the project stores the main topic metadata in Python lists and renders the pages from templates. This makes it easier to edit, expand, and explain each topic during iterative development.

## File-by-file overview

- `app.py`: This is the heart of the project. It defines the Flask application, sets up the SQLite database, stores the topic list and historical content, builds the relationship graph between topics, and adds citation conversion for in-text references. It also handles the route logic for the homepage and each topic page. The file includes logic for seeding the database reliably so content updates are picked up without requiring a manual database reset.

- `templates/index.html`: This template creates the homepage. It includes the hero section, intro copy, map image, search form, and the topic card grid. It helps frame the project as a relational, comparative view of history rather than a static list of dates or events.

- `templates/topic.html`: This template renders each individual topic page. It shows the topic’s period and summary, the expanded explanation, and the list of connections leading to other topics. It also includes the source information for each connection.

- `static/styles.css`: This stylesheet controls the visual design of the entire site. It defines the color palette, card layout, map presentation, typography, spacing, and responsive behavior. It helps the site feel more like a polished educational interface than a raw prototype.

- `static/ukraine-map.png`: This is the Ukraine map asset used on the homepage, giving the app a clear geographic anchor and a visual connection to the place being studied.

- `static/ukraine-map.svg`: This is a vector version of the map created as part of the project’s earlier visual experiments. It documents an earlier iteration of the design and is kept alongside the PNG asset for flexibility.

- `run_local.sh`: This script is used to stop stale Flask processes that may still be running on the chosen port and then restart the app cleanly. It was created to solve a recurring local issue with port conflicts during development, especially on macOS, where a previous server instance can continue listening even after the app appears to have been updated.

- `.flaskenv`: This file stores Flask runtime environment settings, including the port and debug mode. It ensures the app starts consistently in a clean development configuration.

- `requirements.txt`: This lists the Python dependencies needed to run the app, including Flask and supporting packages.

- `test_app.py`: This contains automated tests for the homepage, search functionality, topic ordering, and citation rendering. It helps validate that key user-facing features continue to work as the project evolves.

## Design choices and trade-offs

One key decision was to keep the app simple and maintainable rather than over-engineer a more elaborate data model. Historical content is intentionally curated by hand in Python rather than pulled from a complex external database. This allows for quick edits, controlled narrative structure, and precise source attribution. Because the project is focused on teaching and exploration rather than large-scale publishing infrastructure, the streamlined approach is a good fit.

Another design decision involved balancing the project’s educational purpose with scholarly caution. The app makes no claim to be an authoritative encyclopedia or a substitute for primary and secondary scholarship. Instead, it situates each topic in a broader historical framework and clearly cites its sources. This helps avoid false certainty while still making historical relationships easy to understand.

The homepage map and topic layout were also important. The project wanted to make the geographic and relational nature of the content visible immediately. The map is not just decorative: it signals that Ukraine is not isolated from neighboring worlds but deeply embedded in Black Sea, steppe, Mediterranean, Eurasian, and European networks.

## Running the project locally

To run the app from this folder:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./run_local.sh
```

The app is configured to run on port `5050` and in debug-off mode to avoid the stale port listener problem often caused by Flask’s reloader in development. If you want to start it manually instead, you can use:

```bash
FLASK_DEBUG=0 python app.py
```

Then open the local URL shown in the console, typically `http://127.0.0.1:5050`.

## Conclusion

History in Relation is ultimately about helping people see history as connection rather than isolated fact. It explores the deeply interwoven story of Ukrainian history in relation to steppe societies, language families, trade routes, empires, migrations, state formation, industrial modernity, and contemporary conflict. The project is intentionally small but rich in structure: a searchable archive of historical topics, a map-based homepage, clear explanatory writing, and citations that anchor each relationship in source material.

This app is a conceptual and educational project, and it is best understood as a starting point for deeper historical inquiry. Its value lies in creating a structure in which users can ask bigger questions: How did people, goods, languages, and ideas move across the region? How did empires and states reshape local histories? And how do the ancient and medieval pasts continue to shape the present? These are the kinds of questions the project is designed to invite and support.
