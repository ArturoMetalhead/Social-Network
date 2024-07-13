
class User :
    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email
        self.posts = []
        self.followers = []
        self.followings = []

    def add_post(self, post):
        self.posts.append(post)

    def add_follower(self, follower):
        self.followers.append(follower)

    def add_following(self, following):
        self.followings.append(following)

    def remove_follower(self, follower):
        self.followers.remove(follower)

    def remove_following(self, following):
        self.followings.remove(following)

    def __str__(self):
        return self.username