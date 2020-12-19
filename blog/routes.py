from flask import render_template, request, redirect, url_for, flash
from blog import app, db
from blog.models import Entry
from blog.forms import EntryForm
from faker import Faker


@app.route("/", methods=["GET"])
def homepage():
    posts = Entry.query.filter_by(is_published=True).order_by(
        Entry.pub_date.desc())
    return render_template("homepage.html", posts=posts)


def create_or_edit_entry(entry_id, entry, form):
    errors = None
    if request.method == "POST":
        if form.validate_on_submit() and entry_id:
            form.populate_obj(entry)
            db.session.commit()
            return redirect(url_for("homepage"))
        elif form.validate_on_submit():
            db.session.add(entry)
            db.session.commit()
            flash(f"Yeah, thanks!", 'success')
        else:
            errors = form.errors
            flash(f"Oops... See the following errors: {errors}", 'error')
    return render_template(
        "entry_form.html", form=form, errors=errors, entry_id=entry_id)


@app.route("/create", methods=["GET", "POST"])
def create_entry():
    form = EntryForm()
    entry_id = None
    entry = Entry(
        title=form.title.data,
        body=form.body.data,
        is_published=form.is_published.data
        )
    return create_or_edit_entry(entry_id, entry, form)


@app.route("/edit-post/<int:entry_id>", methods=["GET", "POST"])
def edit_entry(entry_id):
    entry = Entry.query.filter_by(id=entry_id).first_or_404()
    form = EntryForm(obj=entry)
    return create_or_edit_entry(entry_id, entry, form)


@app.route("/random/<entry_id>", methods=["POST"])
def generate_entry(entry_id):
    fake = Faker()
    try:
        int(entry_id)
        entry = Entry.query.filter_by(id=entry_id).first_or_404()
        entry.title = fake.sentence()
        entry.body = "\n".join(fake.paragraphs(15))
    except ValueError:
        entry = Entry(
            title=fake.sentence(),
            body="\n".join(fake.paragraphs(15)),
            is_published=True
            )
    db.session.add(entry)
    db.session.commit()
    return redirect(url_for("homepage"))