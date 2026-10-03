# AI assistance: GitHub Copilot helped draft and refine this application.

import os
import sqlite3
from pathlib import Path

from flask import Flask, abort, g, render_template, request


SOURCE_URL = "https://uhgi.org/"
SOURCE_NAME = "Ukrainian History Global Initiative, project overview"

TOPICS = [
    ("yamna", "Yamna", "Prehistory", "A prehistoric culture whose expansion is among the connections UHGI highlights in the spread of Indo-European languages."),
    ("indo-european-languages", "Indo-European languages", "Language", "A language-family story that connects the lands of contemporary Ukraine with developments across a wider region."),
    ("scythia", "Scythia", "Antiquity", "A region and set of peoples that UHGI places in conversation with the Bosporan Kingdom and ancient Athens."),
    ("bosporan-kingdom", "Bosporan Kingdom", "Antiquity", "A polity around the Black Sea whose connections help frame the ancient history of the region."),
    ("ancient-athens", "Ancient Athens", "Antiquity", "A wider classical-world connection in UHGI's account of Scythia and the Bosporan Kingdom."),
    ("rus", "Rus", "Middle Ages", "A medieval state described by UHGI as a synthesis of Slavic, Viking, Byzantine, Khazar, and western European elements."),
    ("slavic-peoples", "Slavic peoples", "Middle Ages", "One of the cultural and political elements UHGI names in its description of Rus."),
    ("vikings", "Vikings", "Middle Ages", "A northern European connection included in UHGI's description of the formation of Rus."),
    ("byzantium", "Byzantium", "Middle Ages", "A significant neighboring influence in UHGI's description of Rus."),
    ("khazars", "Khazars", "Middle Ages", "A people named among the varied elements that shaped the formation of Rus."),
    ("western-europe", "Western Europe", "Middle Ages", "A broader European connection in UHGI's account of Rus."),
    ("cossacks", "Cossacks", "Early modern period", "UHGI presents the Cossacks as an early anti-colonial or proto-national entity."),
    ("anti-colonial-or-proto-national-entities", "Anti-colonial or proto-national entities", "Historical theme", "A theme through which UHGI frames the Cossacks as an early example."),
    ("soviet-union", "Soviet Union", "20th century", "UHGI considers Ukraine's centrality to Soviet ideas of global transformation."),
    ("nazi-germany", "Nazi Germany", "20th century", "UHGI considers Ukraine's centrality to Nazi views of global transformation."),
    ("global-transformation", "Global transformation", "20th century", "A theme UHGI uses to describe the significance of Ukraine to Soviet and Nazi views."),
    ("global-economy-and-politics", "Global economy and politics", "Modern history", "A wider context UHGI connects to developments surrounding the present war."),
    ("russo-ukrainian-war", "Russo-Ukrainian war", "Modern history", "UHGI's project concludes with treatment of the war while emphasizing creation and longer historical developments."),
]

CONNECTIONS = [
    ("yamna", "indo-european-languages", "Associated with the spread of", "UHGI highlights the role of the Yamna in the spread of what would become Indo-European languages."),
    ("scythia", "bosporan-kingdom", "Connected with", "UHGI treats Scythia and the Bosporan Kingdom together as part of the ancient history of the region."),
    ("bosporan-kingdom", "ancient-athens", "Synthesized with", "UHGI describes a synthesis of Scythia and the Bosporan Kingdom with ancient Athens in the development of classical culture."),
    ("scythia", "ancient-athens", "Part of a cultural synthesis with", "UHGI describes a synthesis of Scythia and the Bosporan Kingdom with ancient Athens in the development of classical culture."),
    ("rus", "slavic-peoples", "Formation included", "UHGI describes Rus as a unique medieval state with Slavic elements."),
    ("rus", "vikings", "Formation included", "UHGI describes Rus as a unique medieval state with Viking elements."),
    ("rus", "byzantium", "Formation included", "UHGI describes Rus as a unique medieval state with Byzantine elements."),
    ("rus", "khazars", "Formation included", "UHGI describes Rus as a unique medieval state with Khazar elements."),
    ("rus", "western-europe", "Formation included", "UHGI describes Rus as a unique medieval state with western European elements."),
    ("cossacks", "anti-colonial-or-proto-national-entities", "Presented as an early example of", "UHGI describes the Cossacks as an early anti-colonial or proto-national entity."),
    ("soviet-union", "global-transformation", "A perspective on", "UHGI discusses Ukraine's centrality to Soviet views of global transformation."),
    ("nazi-germany", "global-transformation", "A perspective on", "UHGI discusses Ukraine's centrality to Nazi views of global transformation."),
    ("russo-ukrainian-war", "global-economy-and-politics", "Considered in a wider context of", "UHGI connects the present war with larger developments in the global economy and politics."),
]


def init_db(database_path):
    """Create the schema and load the starter graph when the database is empty."""
    database_path = Path(database_path)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    try:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY,
                slug TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                period TEXT NOT NULL,
                summary TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS connections (
                id INTEGER PRIMARY KEY,
                from_topic_id INTEGER NOT NULL REFERENCES topics(id),
                to_topic_id INTEGER NOT NULL REFERENCES topics(id),
                relationship TEXT NOT NULL,
                explanation TEXT NOT NULL,
                source_url TEXT NOT NULL,
                source_name TEXT NOT NULL,
                UNIQUE (from_topic_id, to_topic_id, relationship)
            );
            """
        )
        if connection.execute("SELECT COUNT(*) FROM topics").fetchone()[0] == 0:
            connection.executemany(
                "INSERT INTO topics (slug, name, period, summary) VALUES (?, ?, ?, ?)",
                TOPICS,
            )
            topic_ids = dict(
                connection.execute("SELECT slug, id FROM topics").fetchall()
            )
            connection.executemany(
                """
                INSERT INTO connections
                    (from_topic_id, to_topic_id, relationship, explanation, source_url, source_name)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        topic_ids[source],
                        topic_ids[target],
                        relationship,
                        explanation,
                        SOURCE_URL,
                        SOURCE_NAME,
                    )
                    for source, target, relationship, explanation in CONNECTIONS
                ],
            )
        connection.commit()
    finally:
        connection.close()


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE=os.environ.get(
            "UHGI_DATABASE", str(Path(__file__).with_name("connections.sqlite3"))
        )
    )
    if test_config:
        app.config.update(test_config)
    init_db(app.config["DATABASE"])

    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(_error):
        database = g.pop("db", None)
        if database is not None:
            database.close()

    @app.get("/")
    def index():
        search = request.args.get("q", "").strip()
        database = get_db()
        if search:
            like = f"%{search}%"
            topics = database.execute(
                """
                SELECT * FROM topics
                WHERE name LIKE ? OR period LIKE ? OR summary LIKE ?
                ORDER BY name
                """,
                (like, like, like),
            ).fetchall()
        else:
            topics = database.execute(
                "SELECT * FROM topics ORDER BY name"
            ).fetchall()
        connection_count = database.execute(
            "SELECT COUNT(*) FROM connections"
        ).fetchone()[0]
        return render_template(
            "index.html",
            topics=topics,
            search=search,
            connection_count=connection_count,
        )

    @app.get("/topic/<slug>")
    def topic_detail(slug):
        database = get_db()
        topic = database.execute(
            "SELECT * FROM topics WHERE slug = ?", (slug,)
        ).fetchone()
        if topic is None:
            abort(404)
        connections = database.execute(
            """
            SELECT
                c.relationship,
                c.explanation,
                c.source_url,
                c.source_name,
                CASE WHEN c.from_topic_id = ? THEN target.name ELSE source.name END AS related_name,
                CASE WHEN c.from_topic_id = ? THEN target.slug ELSE source.slug END AS related_slug
            FROM connections AS c
            JOIN topics AS source ON source.id = c.from_topic_id
            JOIN topics AS target ON target.id = c.to_topic_id
            WHERE c.from_topic_id = ? OR c.to_topic_id = ?
            ORDER BY related_name, c.relationship
            """,
            (topic["id"], topic["id"], topic["id"], topic["id"]),
        ).fetchall()
        return render_template(
            "topic.html", topic=topic, connections=connections
        )

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
