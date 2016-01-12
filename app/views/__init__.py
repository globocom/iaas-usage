from app import app
from flask import render_template, request


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/instances')
def instances():
    return render_template('instances/index.html')

@app.route('/instances/<project_name>')
def instances_project(project_name):
	project_id = request.args.get('project_id', '')
	return render_template('instances/project.html', project_name=project_name, project_id=project_id)