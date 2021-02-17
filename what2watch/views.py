from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import (
    TemplateView,
    CreateView,
    ListView,
    DetailView,
    RedirectView,
)
from django.utils.translation import gettext_lazy as _

from what2watch.forms import SignupForm
from what2watch.models import *


class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        result = super().get_context_data(**kwargs)
        episodes = Episode.objects.filter(
            show__in=Show.objects.filter(followers=self.request.user.id)
        )
        episodes_watched = EpisodeWatched.objects.all()
        for episode_watched in episodes_watched:
            episodes = episodes.exclude(episodewatched=episode_watched)
        unwatched_episodes = episodes.filter(release__lt=datetime.today()).order_by(
            "release"
        )
        min_range = datetime.today()
        max_range = min_range + timedelta(days=21)
        episodes = episodes.exclude(release__lt=datetime.today()).filter(
            release__range=[min_range, max_range]
        )
        result["unwatched_episodes"] = unwatched_episodes
        result["episodes"] = episodes
        recommendations = (
            Show.objects.exclude(followers=self.request.user.id)
            .filter(tags__in=Tag.objects.filter(followers=self.request.user.id))
            .distinct()
        )
        result["recommendations"] = recommendations
        return result

    def post(self, request, *args, **kwargs):
        if "watch" in request.POST and request.user.is_authenticated:
            episode = Episode.objects.get(id=request.POST["watch"])
            episode_watched = EpisodeWatched(episode=episode, user=self.request.user)
            episode_watched.save()
            messages.add_message(
                request, messages.SUCCESS, _("This episode has been noted as watched")
            )
        elif "follow" in request.POST and request.user.is_authenticated:
            show = Show.objects.get(id=request.POST["follow"])
            show.followers.add(self.request.user)
            show.save()
            messages.add_message(
                request, messages.SUCCESS, _("This show has been added to your list")
            )

        return HttpResponseRedirect(reverse_lazy("index"))


class SearchQuery(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        search = self.request.POST["s"]
        if search == "":
            return reverse_lazy("search")
        else:
            return reverse_lazy("search_results", kwargs={"s": search})


class SearchView(TemplateView):
    template_name = "search/index.html"

    def get_context_data(self, **kwargs):
        result = super().get_context_data(**kwargs)
        search = self.kwargs["s"]
        if search is not None:
            result["search_results"] = Show.objects.filter(name__icontains=search)
            result["search"] = search

        return result


class ShowsView(ListView):
    template_name = "shows/index.html"

    def get_queryset(self):
        return Show.objects.all().order_by("name")


class ShowDetailView(DetailView):
    template_name = "shows/detail.html"
    model = Show

    def get_context_data(self, **kwargs):
        result = super().get_context_data(**kwargs)
        result["is_user_following"] = Show.objects.filter(
            id=self.kwargs["pk"], followers=self.request.user.id
        )
        result["episodes"] = Episode.objects.filter(show_id=self.kwargs["pk"])
        result["episodes_watched"] = EpisodeWatched.objects.filter(
            user_id=self.request.user.id, episode__show_id=self.kwargs["pk"]
        )
        result["next_episode"] = (
            Episode.objects.filter(release__gte=datetime.today())
            .order_by("release")
            .first()
        )
        result["casting"] = ShowCasting.objects.filter(show_id=self.kwargs["pk"])
        result["ratings"] = Rating.objects.filter(show_id=self.kwargs["pk"]).order_by(
            "published_at"
        )
        result["your_rating"] = Rating.objects.filter(
            show_id=self.kwargs["pk"], user_id=self.request.user.id
        ).first()
        return result

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if "follow" in request.POST and request.user.is_authenticated:
            if request.POST["follow"] == "True":
                self.object.followers.add(request.user)
                self.object.save()
                messages.add_message(
                    request, messages.SUCCESS, _("You now follow this show")
                )
            else:
                self.object.followers.remove(request.user)
                self.object.save()
                messages.add_message(
                    request, messages.WARNING, _("You unfollowed this show")
                )
        if "update_episodes" in request.POST and request.user.is_authenticated:
            episodes_watched = EpisodeWatched.objects.filter(
                episode__show_id=self.kwargs["pk"], user_id=self.request.user.id
            )
            for episode in episodes_watched:
                episode.delete()

            for episode in request.POST.getlist("episodes_watched[]"):
                episode_watched = EpisodeWatched(
                    episode=Episode.objects.get(id=episode), user=self.request.user
                )
                episode_watched.save()
            messages.add_message(
                request, messages.SUCCESS, _("Your watched episodes have been updated")
            )
        if (
            "comment" in request.POST
            and "note" in request.POST
            and request.user.is_authenticated
        ):
            rating = Rating(
                user=self.request.user,
                show=Show.objects.get(id=self.kwargs["pk"]),
                note=request.POST["note"],
                comment=request.POST["comment"],
            )
            rating.save()
            messages.add_message(
                request, messages.SUCCESS, _("Your review has been published !")
            )
        if "delete" in request.POST and request.user.is_authenticated:
            rating = Rating.objects.get(id=request.POST["delete"])
            rating.delete()
            messages.add_message(
                request, messages.SUCCESS, _("Your review has been removed !")
            )

        return HttpResponseRedirect(
            reverse_lazy("shows_detail", kwargs={"pk": self.kwargs["pk"]})
        )


class ActorsView(ListView):
    template_name = "actors/index.html"

    def get_queryset(self):
        return Actor.objects.all().order_by("last_name")


class ActorDetailView(DetailView):
    template_name = "actors/detail.html"
    model = Actor

    def get_context_data(self, **kwargs):
        result = super().get_context_data(**kwargs)
        result["castings"] = ShowCasting.objects.filter(actor_id=self.kwargs["pk"])
        result["shows_count"] = (
            ShowCasting.objects.filter(actor_id=self.kwargs["pk"])
            .values("show")
            .annotate(Count("show"))
            .count()
        )
        return result


class ProfileView(DetailView):
    template_name = "profile/index.html"
    model = User

    def get_context_data(self, **kwargs):
        result = super().get_context_data(**kwargs)
        result["liked_shows"] = Show.objects.filter(followers=self.kwargs["pk"])
        result["ratings"] = Rating.objects.filter(user=self.kwargs["pk"])
        return result


class ProfileEditView(DetailView):
    template_name = "profile/edit.html"
    model = User

    def get_context_data(self, **kwargs):
        result = super().get_context_data(**kwargs)
        result["tags"] = Tag.objects.all()
        result["followed_tags"] = Tag.objects.filter(followers=self.request.user.id)
        return result

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if "update_tags" in request.POST and request.user.is_authenticated:
            followed_tags = Tag.objects.filter(followers=self.request.user.id)
            for tag in followed_tags:
                tag.followers.remove(request.user)

            for tag in request.POST.getlist("tags_followed[]"):
                t = Tag.objects.get(id=tag)
                t.followers.add(self.request.user)
                t.save()

            messages.add_message(
                request, messages.SUCCESS, _("Your tags has been updated")
            )

        return HttpResponseRedirect(
            reverse_lazy("profile_edit", kwargs={"pk": self.kwargs["pk"]})
        )


class AboutView(TemplateView):
    template_name = "about/index.html"


class SignupView(SuccessMessageMixin, CreateView):
    form_class = SignupForm
    success_url = reverse_lazy("login")
    success_message = _("%(username)s as been created")
    template_name = "registration/signup.html"
