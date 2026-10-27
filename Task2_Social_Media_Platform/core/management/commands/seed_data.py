from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Profile, Post, Comment, Like, Follow, Notification
import random


class Command(BaseCommand):
    help = 'Populates the database with realistic Gen-Z users, posts, comments, and interactions.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting VIBEUP seed data generator...")

        # 1. Create a primary demo superuser
        admin_user, created = User.objects.get_or_create(
            username='vibemaster',
            defaults={
                'email': 'vibemaster@vibeup.xyz',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password('password123')
        admin_user.save()
        admin_profile = admin_user.profile
        admin_profile.display_name = "Vibe Master ✨"
        admin_profile.bio = "Chief Vibe Architect @ VIBEUP. Keeping the platform chaotic and cozy. 💜"
        admin_profile.campus = "Metaverse University '26"
        admin_profile.vibe_tag = "Community Legend"
        admin_profile.pronouns = "they/them"
        admin_profile.interests = "Web Design, Synthwave, Matcha, Indie Games"
        admin_profile.save()

        # 2. Sample Gen-Z persona users
        users_data = [
            {
                'username': 'maya_codes',
                'email': 'maya@campus.edu',
                'name': 'Maya Lin 🍵',
                'bio': 'debugging React at 3am fueled by oat milk iced matcha & lo-fi beats. #buildinpublic',
                'campus': "UCLA CS '26",
                'vibe_tag': 'Matcha Fiend',
                'pronouns': 'she/her',
                'interests': 'Coding, Matcha, Lo-Fi, Figma, Indie Games'
            },
            {
                'username': 'kai_visuals',
                'email': 'kai@parsons.edu',
                'name': 'Kai Vance 🎞️',
                'bio': '35mm film obsessed. documenting blurry nights and candid moments. let us make art, not spreadsheets.',
                'campus': "Parsons Design '25",
                'vibe_tag': 'Aesthetic Curator',
                'pronouns': 'they/he',
                'interests': 'Film Photography, Streetwear, Typography, Thrifting, Art'
            },
            {
                'username': 'zara_beats',
                'email': 'zara@nyu.edu',
                'name': 'Zara Chen 🎧',
                'bio': 'bedroom music producer, synth collector, unhinged aux cord DJ. currently obsessed with hyperpop.',
                'campus': "NYU Clive Davis '26",
                'vibe_tag': 'Sound Alchemist',
                'pronouns': 'she/they',
                'interests': 'Music Production, Hyperpop, Vinyl, Festivals, Coffee'
            },
            {
                'username': 'leo_unhinged',
                'email': 'leo@austin.edu',
                'name': 'Leo Rivera 💀',
                'bio': 'it is what it is (it definitely is not). living on 2 hours of sleep, cold pizza and questionable optimism.',
                'campus': "UT Austin '27",
                'vibe_tag': 'Unhinged Realist',
                'pronouns': 'he/him',
                'interests': 'Skateboarding, Memes, Campus Grind, Tacos, Late Nights'
            },
            {
                'username': 'chloe_core',
                'email': 'chloe@columbia.edu',
                'name': 'Chloe Kim 📖',
                'bio': 'romanticizing library basement study sessions and autumn sweaters. reading 5 books at once.',
                'campus': "Columbia '25",
                'vibe_tag': 'Café Philosopher',
                'pronouns': 'she/her',
                'interests': 'BookTok, Specialty Coffee, Poetry, Philosophy, Stationery'
            },
            {
                'username': 'dev_noah',
                'email': 'noah@gatech.edu',
                'name': 'Noah Patel 🚀',
                'bio': 'building silly open-source tools that solve problems nobody asked for. hackathon gremlin.',
                'campus': "Georgia Tech '26",
                'vibe_tag': 'Hackathon Goblin',
                'pronouns': 'he/him',
                'interests': 'Open Source, Python, AI, Mechanical Keyboards, Startups'
            }
        ]

        created_users = [admin_user]
        for data in users_data:
            user, _ = User.objects.get_or_create(
                username=data['username'],
                defaults={'email': data['email']}
            )
            user.set_password('password123')
            user.save()

            prof = user.profile
            prof.display_name = data['name']
            prof.bio = data['bio']
            prof.campus = data['campus']
            prof.vibe_tag = data['vibe_tag']
            prof.pronouns = data['pronouns']
            prof.interests = data['interests']
            prof.save()
            created_users.append(user)

        self.stdout.write(f"Created {len(created_users)} users.")

        # 3. Create Posts
        posts_data = [
            (
                'maya_codes',
                "Why do my best ideas and cleanest code only arrive at 2:47 AM while my room is illuminated solely by VS Code syntax highlighting? 😭 #campuslife #midnightsesh #coding",
                '🎧 In My Zone'
            ),
            (
                'kai_visuals',
                "Just got my 35mm film scans back from last weekend's thrift crawl. The grain is immaculate, honestly. Throwing an impromptu gallery on campus Friday! 🎞️✨ #filmphotography #aesthetic #thrift",
                '🎨 Creative Surge'
            ),
            (
                'zara_beats',
                "Hot take: 8-bar synth loops hit harder than an entire 40-minute conceptual album when you're walking home in the rain. Working on a new track right now 🎹 #indiebeats #hyperpop #vibecheck",
                '🎧 In My Zone'
            ),
            (
                'leo_unhinged',
                "Professor said 'the midterm is straightforward and should only take 50 minutes'. I have been on question 2 for an hour and 15 minutes. It is so over for me bros. 💀 #finalsweek #campuslife #brainrot",
                '💀 Brain Rot'
            ),
            (
                'chloe_core',
                "Finding an empty corner table with a working outlet at the student union cafe is literally my Olympic gold medal. ☕📖 #coffeecore #studywithme #campuslife",
                '☕ Campus Grind'
            ),
            (
                'dev_noah',
                "Just spent 4 hours automating a 30-second daily task. Peak engineering efficiency achieved. Nobody can tell me anything. 💻⚡ #hacks #nerdenergy #opensource",
                '⚡ Unhinged Energy'
            ),
            (
                'vibemaster',
                "Welcome to VIBEUP! This is your zero-filter, all-vibe space. Drop hot takes, find people who share your weird hyperfixations, and celebrate campus chaos. ✨💜 #vibeup #welcome #community",
                '✨ Feeling Iconic'
            ),
            (
                'maya_codes',
                "Matcha latte ranking on campus: 1. Corner Kiosk (oat milk ratio is elite) 2. Library Cafe (too sweet) 3. Dining hall (straight grass water). Don't debate me on this. 🍵 #matchagang #campusfood",
                '✨ Feeling Iconic'
            ),
            (
                'kai_visuals',
                "Golden hour on the north quad lawn right now is unhinged. If you see someone lying flat on the grass with a camera, mind your business please. 🌞📷 #goldenhour #campusvibes",
                '🎨 Creative Surge'
            ),
            (
                'leo_unhinged',
                "Ordered late-night cookies at 1:30 AM and convinced myself it was an investment in my mental health and academic resilience. 🍪✨ #latenightcraving #collegelife",
                '🍕 Late Night Craving'
            ),
        ]

        created_posts = []
        user_map = {u.username: u for u in created_users}

        for author_user, content, mood in posts_data:
            if author_user in user_map:
                post, created = Post.objects.get_or_create(
                    author=user_map[author_user],
                    content=content,
                    defaults={'mood': mood}
                )
                created_posts.append(post)

        self.stdout.write(f"Created {len(created_posts)} posts.")

        # 4. Create Follows (cross-follow network)
        all_users = list(user_map.values())
        for u1 in all_users:
            others = [u for u in all_users if u != u1]
            # follow 3-5 users
            followees = random.sample(others, min(len(others), random.randint(3, 5)))
            for f_user in followees:
                Follow.objects.get_or_create(follower=u1, following=f_user)

        # 5. Create Comments
        sample_comments = [
            "REALEST THING I'VE READ ALL WEEK 💀",
            "no cap honestly the oat milk ratio is everything",
            "Wait drop the Spotify link expeditiously!!",
            "This is so real it hurts 😭",
            "The aesthetic here is immaculate ✨",
            "literally me during 8am lectures",
            "W post, keep cookin",
            "It's giving main character energy honestly 💅"
        ]

        for post in created_posts:
            # Add 2-4 comments per post
            commenters = [u for u in all_users if u != post.author]
            for commenter in random.sample(commenters, random.randint(2, min(4, len(commenters)))):
                Comment.objects.create(
                    post=post,
                    author=commenter,
                    content=random.choice(sample_comments)
                )

        # 6. Create Likes
        for post in created_posts:
            likers = random.sample(all_users, random.randint(2, min(6, len(all_users))))
            for liker in likers:
                Like.objects.get_or_create(user=liker, post=post)

        # 7. Create Notifications for admin_user
        for post in created_posts[:3]:
            if post.author != admin_user:
                Notification.objects.get_or_create(
                    recipient=admin_user,
                    actor=post.author,
                    notification_type='like',
                    post=post,
                    defaults={'is_read': False}
                )

        self.stdout.write(self.style.SUCCESS("[SUCCESS] Successfully seeded VIBEUP with lively Gen-Z data!"))
        self.stdout.write(self.style.SUCCESS("Demo credentials: username='vibemaster', password='password123' (or any seeded user with same password)."))
