import os
import django
from django.core.files import File

settings_module = 'commerce.settings'
os.environ['DJANGO_SETTINGS_MODULE'] = settings_module

django.setup()
from auctions.models import *

# drop existing database (if any) and run latest migration
os.system('python ../../manage.py flush')
os.system('python ../../manage.py makemigrations')
os.system('python ../../manage.py migrate')

print('Creating users')
admin = User.objects.create_superuser('admin', password='admin')
admin.save()
finn = User.objects.create_user('finn', password='finnthehuman', first_name='Finn')
finn.save()
jake = User.objects.create_user('jake', password='baconpancakes', first_name='Jake')
jake.save()
iceking = User.objects.create_user('cool_wiz_9', password='wizardsrule', first_name='Simon')
iceking.save()

print('Creating categories')
weapons = Category(name='Weapons')
weapons.save()
armour = Category(name='Armour')
armour.save()
magic = Category(name='Magical Items')
magic.save()

print('Creating listings')
items = [
    'Cardboard_Armor.jpg', 'Demon_Blood_sword.png', 'Enchiridion.png',
    'Golden_sword_of_battle.png', 'Grass_Sword.png', 'Ice_Crown.png',
    'Lady_Armor.png', 'Metal_Armor.jpg', 'Root_Sword.png',
    'Samurai_Armor.jpg', 'Lumpy_Space_Princess.png'
]
for item in items:

    if 'armor' in item.lower():
        category = armour
        owner = jake
    elif 'sword' in item.lower():
        category = weapons
        owner = finn
    else:
        category = magic
        owner = iceking

    with open('lorem.txt', 'r') as f:
        description = f.read()

    title = item.split('.')[:-1]
    title = ' '.join(title)
    title = title.replace('_', ' ')

    path = os.path.join(os.path.dirname(__file__), 'img', item)
    if os.path.exists(path):
        photo = File(open(path, 'rb'))
    else:
        photo = None

    listing = Listing(
        title=title,
        category=category,
        starting_bid=100,
        owner=owner,
        description=description,
        photo=photo,
    )
    listing.save()

print('Creating comments')
listing = Listing.objects.get(title='Golden sword of battle')

comment = Comment(listing=listing, author=jake, content='Awesome sword bro')
comment.save()
comment = Comment(listing=listing, author=finn, content='Thanks. You interested?')
comment.save()
comment = Comment(listing=listing, author=iceking, content="It's not that great")
comment.save()
comment = Comment(listing=listing, author=finn, content='Shut up Ice King!')
comment.save()

listing = Listing.objects.get(title='Lumpy Space Princess')
comment = Comment(listing=listing, author=iceking, content="Sorry no photo, she's still trying to take the perfect selfie, but I swear, she's a top notch princess! You gotta take her!")
comment.save()
comment = Comment(listing=listing, author=finn, content='You get what you deserve Ice King!')
comment.save()
comment = Comment(listing=listing, author=iceking, content="No! please!!")
comment.save()
comment = Comment(listing=listing, author=jake, content='Ahh ahahahaahah!')
comment.save()
comment = Comment(listing=listing, author=admin, content="This listing will be closed. We don't condone princess trafficking")
comment.save()

print('Creating watchers')
for title in ('Golden sword of battle', 'Grass Sword', 'Enchiridion'):
    listing = Listing.objects.get(title=title)
    listing.watchers.add(jake)
    listing.save()
