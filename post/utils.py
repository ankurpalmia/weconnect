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
        