from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from catalog_db import Category, Item, User, Base

engine = create_engine('postgresql://catalog:supersecret@localhost/catalog')

# Clear database
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create dummy user
user1 = User(name="Talon Jones", email="taloncjones@gmail.com",
             picture='https://pbs.twimg.com/profile_images/2671170543'
                     '/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(user1)
session.commit()

user2 = User(name="Bob Ross", email="bobross@gmail.com",
             picture='https://pbs.twimg.com/profile_images/2671170543'
                     '/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(user2)
session.commit()

# Items for Strings
category1 = Category(name="strings", user_id=1)

session.add(category1)
session.commit()

item1 = Item(name="violin", user_id=1,
             description="Violin, family of stringed musical instruments "
                         "having wooden bodies whose backs and fronts are "
                         "slightly convex, the fronts pierced by two-shaped "
                         "resonance holes. The instruments of the violin "
                         "family have been the dominant bowed instruments "
                         "because of their versatility, brilliance, "
                         "and balance of tone, and their wide dynamic range. "
                         "A variety of sounds may be produced, e.g., "
                         "by different types of bowing or by plucking the "
                         "string (see pizzicato). The violin has always been "
                         "the most important member of the family, from the "
                         "beginning being the principal orchestral "
                         "instrument and holding an equivalent position in "
                         "chamber music and as a solo instrument. The "
                         "technique of the violin was developed much earlier "
                         "than that of the viola or cello.",
             category=category1)

session.add(item1)
session.commit()

item2 = Item(name="viola", user_id=1,
             description="The viola is the alto instrument of the violin "
                         "family (violin, viola, cello). It is constructed "
                         "using the same components as the violin, the only "
                         "difference being the larger size. ... In other "
                         "words, the viola is too small in proportion to its "
                         "tuning and this is the reason for its distinctive "
                         "timbre.",
             category=category1)

session.add(item2)
session.commit()

item3 = Item(name="cello", user_id=1,
             description="The cello is used as a solo musical instrument, "
                         "as well as in chamber music ensembles, string "
                         "orchestras, as a member of the string section of "
                         "symphony orchestras, and some rock bands. It is "
                         "the second-largest bowed string instrument in the "
                         "modern symphony orchestra, the double bass being "
                         "the largest.",
             category=category1)

session.add(item3)
session.commit()

# Items for Woodwinds
category2 = Category(name="woodwinds", user_id=2)

session.add(category2)
session.commit()

item1 = Item(name="flute", user_id=2,
             description="A musical wind instrument consisting of a tube "
                         "with a series of fingerholes or keys, in which the "
                         "wind is directed against a sharp edge, either "
                         "directly, as in the modern transverse flute, "
                         "or through a flue, as in the recorder. an organ "
                         "stop with wide flue pipes, having a flutelike tone.",
             category=category2)

session.add(item1)
session.commit()

item2 = Item(name="piccolo", user_id=2,
             description="Piccolo, in full flauto piccolo, highest-pitched "
                         "woodwind instrument of orchestras and military "
                         "bands. It is a small transverse (horizontally "
                         "played) flute of conical or cylindrical bore, "
                         "fitted with Boehm-system keywork and pitched an "
                         "octave higher than the ordinary concert flute.",
             category=category2)

session.add(item2)
session.commit()

item3 = Item(name="oboe", user_id=1,
             description="The oboe is a woodwind instrument in the soprano "
                         "register. The blowing end of the oboe's slim "
                         "conical tube (head) turns into a small metal pipe "
                         "to which two reeds are affixed.",
             category=category2)

session.add(item3)
session.commit()

# Items for Percussion
category3 = Category(name="percussion", user_id=1)

session.add(category3)
session.commit()

item1 = Item(name="marimba", user_id=1,
             description="The marimba is a percussion instrument consisting "
                         "of a set of wooden bars struck with mallets to "
                         "produce musical tones. Resonators suspended "
                         "underneath the bars amplify their sound. ... This "
                         "instrument is a type of idiophone, but with a more "
                         "resonant and lower-pitched tessitura than the "
                         "xylophone.",
             category=category3)

session.add(item1)
session.commit()

item2 = Item(name="timpani", user_id=1,
             description="Timpani or kettledrums are musical instruments in "
                         "the percussion family. A type of drum, "
                         "they consist of a skin called a head stretched "
                         "over a large bowl traditionally made of copper. "
                         "They are played by striking the head with a "
                         "specialized drum stick called a timpani stick or "
                         "timpani mallet. Timpani evolved from military "
                         "drums to become a staple of the classical "
                         "orchestra by the last third of the 18th century. "
                         "Today, they are used in many types of musical "
                         "ensembles, including concert bands, marching "
                         "bands, orchestras, and even in some rock.",
             category=category3)

session.add(item2)
session.commit()

item3 = Item(name="xylophone", user_id=1,
             description="The xylophone is a musical instrument in the "
                         "percussion family that consists of wooden bars "
                         "struck by mallets.",
             category=category3)

session.add(item3)
session.commit()

# Items for Brass
category4 = Category(name="brass", user_id=1)

session.add(category4)
session.commit()

categories = session.query(Category).all()
for category in categories:
    print "Category: " + category.name
    items = session.query(Item).filter_by(category_id=category.id).all()
    for item in items:
        print "Item: " + item.name
