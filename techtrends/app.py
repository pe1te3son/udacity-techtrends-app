import logging
import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.execute("INSERT INTO connection_audit (created) VALUES (CURRENT_TIMESTAMP)")
    connection.commit()
    connection.row_factory = sqlite3.Row
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

@app.route('/healthz')
def get_healthz():
    return jsonify({
        "result": 'OK - healthy'
    })

@app.route('/metric')
def get_metric():
    connection = get_db_connection()
    posts_count = connection.execute('SELECT COUNT(*) "count" FROM posts').fetchone()
    conn_count = connection.execute('SELECT COUNT(*) "count" FROM connection_audit').fetchone()
    connection.close()
    return jsonify({
        "db_connection_count": conn_count["count"],
        "post_count": posts_count["count"]
    })

# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      logging.error('Article with id {} does not exists'.format(post_id))
      return render_template('404.html'), 404
    else:
      logging.info('Article "{}" retrieved!'.format(post['title']))
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logging.info('"About Us" Page Retrieved')
    return render_template('about.html')

# Define the post creation functionality
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            logging.info('Article "{}" has been created'.format(title))

            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":
   logging.basicConfig(level=logging.DEBUG)
   app.run(host='0.0.0.0', port='3111')
