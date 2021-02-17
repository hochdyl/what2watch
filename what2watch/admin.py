from django.contrib import admin

from what2watch.models import *


admin.site.register(User)
admin.site.register(Actor)
admin.site.register(Tag)
admin.site.register(Show)
admin.site.register(ShowCasting)
admin.site.register(Episode)
admin.site.register(EpisodeWatched)
admin.site.register(Rating)
