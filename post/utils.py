from post.models import Post, Friend
from django.db.models import Q

def get_friends(user):
    friends = Friend.objects.filter(Q(sender=user, accepted=True) | Q(receiver=user, accepted=True))
    friends_list = []
    for friend in friends:
        if(friend.sender == user):
            friends_list.append(friend.receiver)
        else:
            friends_list.append(friend.sender)
    return friends_list


def create_post_dict(all_posts):
    post_list = []
    for post in all_posts:
        post_list.append({
            'text': post.text,
            'image': post.image if post.image else None,
            'created_by': {
                'name': post.created_by.get_full_name(),
                'username': post.created_by.username
            },
            'likes': post.liked_by.count(),
            'liked_by': [person.get_full_name() for person in post.liked_by.all()],
            'created_at': post.created_at
        })
    return post_list
        