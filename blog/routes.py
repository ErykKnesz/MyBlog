from flask import render_template, request, redirect, url_for, flash, session
from blog import app, db
from blog.models import Entry
from blog.forms import EntryForm, LoginForm
from faker import Faker
import functools


def create_or_edit_entry(entry_id, entry, form):
    errors = None
    if request.method == 'POST':
        if form.validate_on_submit() and entry_id:
            form.populate_obj(entry)
            db.session.commit()
            return redirect(url_for('homepage'))
        elif form.validate_on_submit():
            db.session.add(entry)
            db.session.commit()
            flash(f"Yeah, thanks!", 'success')
        else:
            errors = form.errors
            flash(f"Oops... See the following errors: {errors}", 'error')
    return render_template(
        'entry_form.html', form=form, errors=errors, entry_id=entry_id)


def login_required(view_func):
    @functools.wraps(view_func)
    def check_permissions(*args, **kwargs):
        if session.get('logged_in'):
            return view_func(*args, **kwargs)
        return redirect(url_for('login', next=request.path))
    return check_permissions


@app.route("/", methods=['GET'])
def homepage():
    posts = Entry.query.filter_by(is_published=True).order_by(
        Entry.pub_date.desc())
    return render_template('homepage.html', posts=posts)


@app.route("/drafts")
@login_required
def list_drafts():
    drafts = Entry.query.filter_by(is_published=False).order_by(
        Entry.pub_date.desc())
    return render_template('drafts.html', drafts=drafts)


@app.route("/create", methods=['GET', 'POST'])
@login_required
def create_entry():
    form = EntryForm()
    entry_id = None
    entry = Entry(
        title=form.title.data,
        body=form.body.data,
        is_published=form.is_published.data
        )
    return create_or_edit_entry(entry_id, entry, form)


@app.route("/edit-post/<int:entry_id>", methods=['GET', 'POST'])
@login_required
def edit_entry(entry_id):
    entry = Entry.query.filter_by(id=entry_id).first_or_404()
    form = EntryForm(obj=entry)
    return create_or_edit_entry(entry_id, entry, form)



@app.route("/random/<entry_id>", methods=['POST'])
def generate_entry(entry_id):
    fake = Faker()
    try:
        int(entry_id)
        entry = Entry.query.filter_by(id=entry_id).first_or_404()
        form = EntryForm(obj=entry)
        if form.validate_on_submit():
            entry.title = fake.sentence()
            entry.body = '\n'.join(fake.paragraphs(15))
    except ValueError:
        form = EntryForm()
        form.title.data = fake.sentence()
        form.body.data = '\n'.join(fake.paragraphs(15))
        if form.validate_on_submit():
            entry = Entry(
                title=form.title.data,
                body=form.body.data,
                is_published=True
                )
    db.session.add(entry)
    db.session.commit()
    return redirect(url_for('homepage'))


@app.route("/delete/<int:draft_id>", methods=['POST'])
def delete_entry(draft_id):
    draft = Entry.query.filter_by(id=draft_id).first_or_404()
    db.session.delete(draft)
    db.session.commit()
    flash(f'Successfully deleted entry {draft.title}.', 'success')
    return redirect(url_for('homepage'))

@app.route("/login", methods=['GET', 'POST'])
def login():
   form = LoginForm()
   errors = None
   next_url = request.args.get('next')
   if request.method == 'POST':
       if form.validate_on_submit():
           session['logged_in'] = True
           session.permanent = True  # Use cookie to store session.
           flash('You are now logged in.', 'success')
           return redirect(next_url or url_for('homepage'))
       else:
           errors = form.errors
   return render_template("login_form.html", form=form, errors=errors)


@app.route('/logout/', methods=['GET'])
def logout():
    session.clear()
    flash("You are now logged out.", 'success')
    return redirect(url_for('homepage'))