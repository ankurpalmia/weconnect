from django.db.models import Q

from post.models import Friend, Post


def get_friends(user):
    friends = Friend.objects.filter(Q(sender=user, accepted=True) | Q(receiver=user, accepted=True))
    friends_list = []
    for friend in friends:
        if(friend.sender == user):
            friends_list.append(friend.receiver)
        else:
            friends_list.append(friend.sender)
    return friends_list
