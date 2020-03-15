from django.db import models
from base.models import BaseModel
from user.models import UserProfile
from django.db.models import Q
from django.core.exceptions import ValidationError


class Post(BaseModel, models.Model):
    """
    This model stores the Posts of users
    """
    PRIVACY_CHOICES = [
        ('PUBLIC', 'Public'),
        ('PRIVATE', 'Private'),
        ('FRIENDS', 'Friends only'),
        ('CUSTOM', 'Custom')
    ]
    text = models.TextField()
    image = models.ImageField(upload_to="assets/posts/", null=True, blank=True)
    created_by = models.ForeignKey(UserProfile, related_name="posts", on_delete=models.CASCADE)
    privacy = models.CharField(max_length=10, choices=PRIVACY_CHOICES)
    custom_list = models.ManyToManyField(UserProfile, related_name="post_by_friends", blank=True)
    liked_by = models.ManyToManyField(UserProfile, related_name="likes", blank=True)

    def __str__(self):
        return "{}'s post on {}".format(self.created_by.first_name, self.created_at)


class Friend(models.Model):
    """
    This model stores the friends of a user
    """
    sender = models.ForeignKey(UserProfile, related_name="sender", on_delete=models.CASCADE)
    receiver = models.ForeignKey(UserProfile, related_name="receiver", on_delete=models.CASCADE)
    accepted = models.NullBooleanField(default=None)

    # class Meta:
    #     unique_together = ('sender', 'receiver')

    def __str__(self):
        return "{} to {}".format(self.sender, self.receiver)

    def clean(self):
        if (self.__class__.objects
                .filter(Q(sender_id=self.receiver_id, receiver_id=self.sender_id)
                        | Q(sender_id=self.sender_id, receiver_id=self.receiver_id))
                .exclude(id=self.id).exists()):
            raise ValidationError("Friendship already declared between {} and {}".format(self.sender.first_name, self.receiver.first_name))
        if self.sender_id == self.receiver_id:
            raise ValidationError("Can't declare friendship to yourself")
        
    def save(self, **kwargs):
        self.full_clean()
        super().save(**kwargs)
