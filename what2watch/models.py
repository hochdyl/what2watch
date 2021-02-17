from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    avatar = models.ImageField(
        upload_to=settings.IMAGES_PATH,
        default=settings.IMAGES_PATH + "default-avatar.png",
        blank=True,
    )

    def __str__(self):
        return self.username


class Tag(models.Model):
    name = models.CharField(max_length=100)
    followers = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.name


class Actor(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    portrait = models.ImageField(
        upload_to=settings.IMAGES_PATH,
        default=settings.IMAGES_PATH + "default-banner.png",
        blank=True,
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Show(models.Model):
    name = models.CharField(max_length=100)
    summary = models.TextField(max_length=1000, null=True, blank=True)
    banner = models.ImageField(
        upload_to=settings.IMAGES_PATH,
        default=settings.IMAGES_PATH + "default-banner.png",
        blank=True,
    )
    STATUS = [
        ("finished", _("Finished")),
        ("still_running", _("Still running")),
        ("paused", _("Paused")),
        ("not_started", _("Not started")),
    ]
    status = models.CharField(max_length=13, choices=STATUS)
    actors = models.ManyToManyField(Actor, through="ShowCasting")
    tags = models.ManyToManyField(Tag, blank=True)
    followers = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.name


class ShowCasting(models.Model):
    show = models.ForeignKey(Show, on_delete=models.CASCADE)
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE)
    role_name = models.CharField(max_length=100)
    portrait = models.ImageField(
        upload_to=settings.IMAGES_PATH,
        default=settings.IMAGES_PATH + "default-banner.png",
        blank=True,
    )

    def __str__(self):
        return f"{self.actor} {_('in')} {self.show} {_('as')} {self.role_name}"


class Episode(models.Model):
    show = models.ForeignKey(Show, on_delete=models.CASCADE)
    season = models.PositiveIntegerField(default=1)
    episode = models.PositiveIntegerField(default=1)
    release = models.DateField(default=timezone.now)

    class Meta:
        unique_together = (("show", "season", "episode"),)

    def __str__(self):
        return (
            f"{self.show} - {_('Season ')} {self.season} {_('episode')} {self.episode}"
        )


class EpisodeWatched(models.Model):
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} {_('have watched')} {self.episode}"


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    show = models.ForeignKey(Show, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("user", "show"),)

    NOTES = [("0", "0"), ("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5")]
    note = models.CharField(max_length=2, choices=NOTES)
    comment = models.TextField(max_length=1000, null=True, blank=True)
    published_at = models.DateTimeField(auto_now_add=True)
    last_edit_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} {_('has rated')} {self.show}"
