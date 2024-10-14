from flask import Flask, render_template, request, redirect, url_for, session
from config import Config  # Import the config file
from datetime import datetime
import random

app = Flask(__name__)
app.config.from_object(Config)  # Load configuration from Config class

@app.route('/')
def index():
    # Filter artworks for the current month
    current_month = datetime.now().month
    current_year = datetime.now().year
    current_month_artworks = [
        artwork for artwork in images
        if artwork['upload_date'].month == current_month and artwork['upload_date'].year == current_year
    ]

    # If there are no artworks for the current month, fallback to the previous month
    if not current_month_artworks:
        previous_month = current_month - 1 if current_month > 1 else 12
        previous_year = current_year if current_month > 1 else current_year - 1
        current_month_artworks = [
            artwork for artwork in images
            if artwork['upload_date'].month == previous_month and artwork['upload_date'].year == previous_year
        ]

    # Sort artworks by rating, descending (if ratings are available)
    current_month_artworks.sort(key=lambda x: x.get('average_rating', 0), reverse=True)

    # Select the top 5 based on rating, or all if less than 5
    featured_artworks = current_month_artworks[:5] if current_month_artworks else None

    # If no rating-based artworks, randomly select 5 or fewer artworks
    if not featured_artworks:
        all_artworks = random.sample(images, min(len(images), 5)) if images else None
    else:
        all_artworks = None

    # Ensure the featured artworks include metadata
    featured_artworks = featured_artworks or all_artworks or images[:5]

    return render_template('index.html', featured_artworks=featured_artworks)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get metadata from the form
        title = request.form['title']
        artist = request.form['artist']
        date = request.form['date']
        medium = request.form['medium']
        inspiration = request.form['inspiration']
        culturalContext = request.form['culturalContext']
        subjectMatter = request.form['subjectMatter']
        artistStatement = request.form['artistStatement']
        
        # Process file upload
        file = request.files['file']
        if file:
            filename = file.filename
            file.save(f'static/images/{filename}')
            
            # Store metadata (in a real application, this would be saved in a database)
            images.append({
                'filename': filename,
                'upload_date': datetime.now(),  # Replace with current date dynamically
                'title': title,
                'artist': artist,
                'date': date,
                'medium': medium,
                'inspiration': inspiration,
                'culturalContext': culturalContext,
                'subjectMatter': subjectMatter,
                'artistStatement': artistStatement,
                'average_rating': 0  # Initialize with no rating
            })
            return redirect(url_for('gallery'))

    return render_template('upload.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html', images=images)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == app.config['USERNAME'] and password == app.config['PASSWORD']:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            error = 'Invalid credentials. Please try again.'
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    images = []  # Example data structure to hold image info, replace with a database in a real scenario
    app.run(debug=True)
