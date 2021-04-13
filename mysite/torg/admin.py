from django.contrib import admin
from .models import Profile, Tournament, PlayerTeam

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'photo']


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ['author', 'name', 'description', 'slug', 'created']

@admin.register(PlayerTeam)
class PlayerTeamAdmin(admin.ModelAdmin):
    list_display = ['tournament', 'name']



