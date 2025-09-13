# app.py
from flask import Flask, render_template, request, redirect, url_for
from datetime import date
import json
import os

app = Flask(__name__)

DATA_FILE = 'data.json'

# Your profile information
PROFILE = {
    "name": "Sivabharathi",
    "picture_url": "/static/profile.jpg",
    "course": "B.VOC in Software Development & Machine Learning"
}

def init_data():
    if not os.path.exists(DATA_FILE):
        default_data = {
            "subjects": [
                {"id": 1, "name": "Software Engineering"},
                {"id": 2, "name": "Mobile Applications"},
                {"id": 3, "name": "Data Structure"},
                {"id": 4, "name": "Mathematics"},
                {"id": 5, "name": "Information Security"},
                {"id": 6, "name": "Frontend Development"},
                {"id": 7, "name": "Basic Indian Language"},
                {"id": 8, "name": "Information Security lab"},
                {"id": 9, "name": "Frontend Development lab"},
                {"id": 10, "name": "Mobile Applications lab"},
                {"id": 11, "name": "Data Structure lab"},
                {"id": 12, "name": "Integral Yoga"}
            ],
            "study_sessions": [],
            "coding_problems": [],
            "projects": []
        }
        save_data(default_data)

def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        init_data()
        return load_data()

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.context_processor
def inject_profile():
    return dict(profile=PROFILE)

@app.template_filter('get_subject_name')
def get_subject_name(subject_id, subjects):
    for subject in subjects:
        if subject['id'] == subject_id:
            return subject['name']
    return "Unknown Subject"

@app.route('/')
def index():
    data = load_data()
    today = date.today().isoformat()
    today_sessions = [s for s in data['study_sessions'] if s.get('date') == today]
    pending_problems = [p for p in data['coding_problems'] if not p.get('completed', False)]
    active_projects = [p for p in data['projects'] if p.get('status') != 'Completed']
    
    return render_template('index.html',
                           subjects=data['subjects'],
                           today_sessions=today_sessions,
                           pending_problems=pending_problems,
                           active_projects=active_projects,
                           today=today)

@app.route('/add_study_session', methods=['POST'])
def add_study_session():
    data = load_data()
    new_session = {
        "id": len(data['study_sessions']) + 1,
        "subject_id": int(request.form['subject']),
        "date": request.form['date'],
        "duration": float(request.form['duration']),
        "topics": request.form['topics'],
        "notes": request.form.get('notes', '')
    }
    data['study_sessions'].append(new_session)
    save_data(data)
    return redirect(url_for('index'))

@app.route('/studies')
def studies():
    data = load_data()
    today = date.today().isoformat()
    return render_template('studies.html',
                           subjects=data['subjects'],
                           study_sessions=data['study_sessions'],
                           today=today)

@app.route('/add_coding_problem', methods=['POST'])
def add_coding_problem():
    data = load_data()
    new_problem = {
        "id": len(data['coding_problems']) + 1,
        "date": request.form['date'],
        "platform": request.form['platform'],
        "problem": request.form['problem'],
        "difficulty": request.form['difficulty'],
        "solution_link": request.form.get('solution_link', ''),
        "completed": False
    }
    data['coding_problems'].append(new_problem)
    save_data(data)
    return redirect(url_for('coding'))

@app.route('/coding')
def coding():
    data = load_data()
    today = date.today().isoformat()
    return render_template('coding.html',
                           coding_problems=data['coding_problems'],
                           today=today)

@app.route('/toggle_problem_status/<int:problem_id>')
def toggle_problem_status(problem_id):
    data = load_data()
    for problem in data['coding_problems']:
        if problem['id'] == problem_id:
            problem['completed'] = not problem.get('completed', False)
            break
    save_data(data)
    return redirect(url_for('coding'))

@app.route('/add_project', methods=['POST'])
def add_project():
    data = load_data()
    new_project = {
        "id": len(data['projects']) + 1,
        "name": request.form['name'],
        "description": request.form.get('description', ''),
        "status": request.form['status'],
        "start_date": request.form.get('start_date', ''),
        "due_date": request.form.get('due_date', ''),
        "notes": request.form.get('notes', '')
    }
    data['projects'].append(new_project)
    save_data(data)
    return redirect(url_for('projects'))

@app.route('/projects')
def projects():
    data = load_data()
    return render_template('projects.html', projects=data['projects'])

@app.route('/update_project_status/<int:project_id>', methods=['POST'])
def update_project_status(project_id):
    data = load_data()
    for project in data['projects']:
        if project['id'] == project_id:
            project['status'] = request.form['status']
            break
    save_data(data)
    return redirect(url_for('projects'))

@app.route('/reports')
def reports():
    data = load_data()
    
    # Calculate study time by subject
    study_time = {}
    for session in data['study_sessions']:
        subject_id = session.get('subject_id')
        subject_name = next((s['name'] for s in data['subjects'] if s['id'] == subject_id), "Unknown")
        study_time[subject_name] = study_time.get(subject_name, 0) + float(session.get('duration', 0))
    
    # Count problems by difficulty
    problem_stats = {"Easy": 0, "Medium": 0, "Hard": 0}
    for problem in data['coding_problems']:
        diff = problem.get('difficulty')
        if diff in problem_stats:
            problem_stats[diff] += 1
    
    # Project status counts
    project_stats = {"Not Started": 0, "In Progress": 0, "Completed": 0}
    for project in data['projects']:
        status = project.get('status')
        if status in project_stats:
            project_stats[status] += 1
    
    return render_template('reports.html',
                           study_time=study_time,
                           problem_stats=problem_stats,
                           project_stats=project_stats)

if __name__ == '__main__':
    init_data()
    app.run(debug=True)