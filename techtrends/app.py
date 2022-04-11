import os
import sqlite3
import logging
import sys
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

# Function to get a database connection.
# This function connects to database with the name `database.db`
db_connection_count = 0


def get_db_connection():
    global db_connection_count
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row

    db_connection_count += 1

    return connection

# Function to get a post using its ID


def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                              (post_id,)).fetchone()
    connection.close()

    return post


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application


@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Healthcheck endpoint


@app.route("/healthz")
def healthz():
    response = app.response_class(
        response=json.dumps({
            "result": "OK - healthy"
        }),
        status=200,
        mimetype='application/json'
    )
    return response

# Metrics Endpoint


@app.route("/metrics")
def metrics():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()

    response = app.response_class(
        response=json.dumps(
            {
                "db_connection_count": db_connection_count,
                "post_count": len(posts)
            }
        ),
        status=200,
        mimetype='application/json'
    )

    return response

# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown


@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)

    if post is None:
        app.logger.error("Article not found")
        return render_template('404.html'), 404
    else:
        app.logger.info("%r Article retrieved", post["title"])
        return render_template('post.html', post=post)

# Define the About Us page


@app.route('/about')
def about():
    app.logger.info("About page")
    return render_template('about.html')

# Define the post creation functionality


@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        app.logger.info('%s New article created: ', title)

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                               (title, content))
            connection.commit()
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')


# start the application on port 3111
if __name__ == "__main__":
    loglevel = os.getenv("LOGLEVEL", "DEBUG").upper()
    loglevel = (
        getattr(logging, loglevel)
        if loglevel in ["CRITICAL", "DEBUG", "ERROR", "INFO", "WARNING", ]
        else logging.DEBUG
    )

  # Set logger to handle STDOUT and STDERR
    stdout_handler = logging.StreamHandler(sys.stdout)  # STDOUT handler
    stderr_handler = logging.StreamHandler(sys.stderr)  # STDERR handler
    handlers = [stderr_handler, stdout_handler]

  # format output
    format_output = ('%(asctime)s - %(name)s - %(message)s')
    logging.basicConfig(format=format_output,
                        level=loglevel, handlers=handlers)
    app.run(host='0.0.0.0', port='3111')
