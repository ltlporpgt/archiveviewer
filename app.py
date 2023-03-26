from flask import Flask, request
import json
import os

# This code would be 20x better if I used Jinja.

cache = {}

app = Flask(__name__)

title = '<title>&lt;(archiveviewer)&gt;</title>'
css_link = '<link href="/styles/general.css" rel="stylesheet">'
header = title+css_link

def sanitize(text):
	return text.replace("<","&lt;").replace(">","&gt;")

@app.route("/styles/<path:subpath>")
def load_style(subpath):
	style_file = open('styles/'+subpath, 'r')
	style = style_file.read()
	style_file.close()
	return style

@app.route("/<archive_name>/edit/<path:subpath>")
def load_page(archive_name, subpath):
	archive_name = f"archives/{archive_name}"
	if archive_name in cache:
		archive = cache[archive_name]
	else:
		try:
			archive_file = open(archive_name)
		except:
			return header+f"<p>Failed to load file {sanitize(archive_name)}</p>"
		archive = archive_file.read()
		archive_file.close()
		try:
			archive = json.loads(archive)
		except:
			return header+f"<p>Failed to decode file {sanitize(archive_name)}</p>"
		cache[archive_name] = archive
	try:
		return header+f"<p class='highlight'>{sanitize(subpath)}</p><br><p>{sanitize(archive[subpath])}</p>"
	except KeyError:
		return header+f"<p>The page {sanitize(subpath)} is not in archive {sanitize(archive_name)}.</p>"

@app.route("/<archive_name>/search")
def search_pages(archive_name):
	return header+f"<p>Please enter a search query.</p><br><form action='query' method='post'><input name='search' type='text'></form>"

@app.route("/<archive_name>/query", methods=['GET','POST'])
def query(archive_name):
	if request.method == 'POST':
		archive_file = open('archives/'+archive_name,'r')
		archive = archive_file.read()
		archive_file.close()
		archive = json.loads(archive)
		archive_keys = list(archive.keys())
		archive_values = list(archive.values())
		matches = []
		for vali in range(len(archive_values)):
			value = archive_values[vali]
			if request.form['search'].lower() in value.lower():
				matches.append(vali)
		for keyi in range(len(archive_keys)):
			key = archive_keys[key]
			if request.form['search'].lower() in key.lower():
				if not keyi in matches:
					matches.append(keyi)
		results = f"<p>Got {len(matches)} results.</p><br>"
		for match in matches:
			page = archive_keys[match]
			results += f"<a href='edit/{sanitize(page)}'>{sanitize(page)}</a><br>"
		return header+results
	else:
		return header+f"<p>No query given. Please use <a href='search'>the search function</a>."

@app.route("/")
def index():
	listing = os.listdir("archives")
	links = ""
	for link in listing:
		links += f"<a href='/{link}/search'>{link}</a><br>"
	return header+f"<p>Select an archive.</p><br><div class='archivelinks'>{links}</div>"
