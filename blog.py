from blog import app, db
from blog.models import Entry
from faker import Faker

fake = Faker()

def generate_entries(how_many=10):
    fake = Faker()

    for i in range(how_many):
        post = Entry(
            title=fake.sentence(),
            body='\n'.join(fake.paragraphs(15)),
            is_published=True
        )
        db.session.add(post)
    db.session.commit()


if __name__ == "__main__":
    app.run(debug=True)