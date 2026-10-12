from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'apexserve_secret_key_change_in_production'

# In-memory database storing tickets with initial sample comments
tickets_db = [
    {
        'id': 12,
        'title': 'dsdsd',
        'description': 'sdsdsdsd...',
        'category': 'Software',
        'priority': 'Critical',
        'status': 'Open',
        'comments': [
            {'author': 'System', 'role': 'system', 'text': 'Ticket created and queued for agent review.'},
            {'author': 'User', 'role': 'user', 'text': 'Any update on this issue?'}
        ]
    }
]

next_ticket_id = 13

@app.route('/', methods=['GET', 'POST'])
def index():
    global next_ticket_id

    # Handle ticket creation
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        priority = request.form.get('priority')
        description = request.form.get('description')

        if title and description:
            new_ticket = {
                'id': next_ticket_id,
                'title': title,
                'description': description,
                'category': category,
                'priority': priority,
                'status': 'Open',
                'comments': [
                    {'author': 'System', 'role': 'system', 'text': 'Ticket submitted successfully.'}
                ]
            }
            tickets_db.append(new_ticket)
            next_ticket_id += 1
            return redirect(url_for('index'))

    role = session.get('role', 'user')
    error = session.pop('error', None)

    return render_template('index.html', role=role, tickets=tickets_db, error=error)


@app.route('/add_comment/<int:ticket_id>', methods=['POST'])
def add_comment(ticket_id):
    comment_text = request.form.get('comment')
    role = session.get('role', 'user')
    author_name = "IT Agent" if role == 'admin' else "Employee"

    if comment_text:
        for ticket in tickets_db:
            if ticket['id'] == ticket_id:
                ticket['comments'].append({
                    'author': author_name,
                    'role': role,
                    'text': comment_text
                })
                break
    return redirect(url_for('index'))


@app.route('/switch_role', methods=['POST'])
def switch_role():
    target_role = request.form.get('target_role')

    if target_role == 'admin':
        password = request.form.get('password')
        if password == 'admin123':
            session['role'] = 'admin'
        else:
            session['error'] = 'Invalid password! Access denied.'
    else:
        session['role'] = 'user'

    return redirect(url_for('index'))


@app.route('/resolve_ticket/<int:ticket_id>')
def resolve_ticket(ticket_id):
    if session.get('role') == 'admin':
        for ticket in tickets_db:
            if ticket['id'] == ticket_id:
                ticket['status'] = 'Resolved'
                ticket['comments'].append({
                    'author': 'IT Agent',
                    'role': 'admin',
                    'text': 'Ticket marked as RESOLVED.'
                })
                break
    return redirect(url_for('index'))


@app.route('/delete_ticket/<int:ticket_id>')
def delete_ticket(ticket_id):
    if session.get('role') == 'admin':
        global tickets_db
        tickets_db = [t for t in tickets_db if t['id'] != ticket_id]
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)