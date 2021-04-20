from django.contrib import admin
from .models import Profile, Tournament, PlayerTeam

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'photo']


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ['name','author', 'description', 'slug', 'created', 'start_date', 'end_date',
                    'tournament_status', 'tournament_type', 'num_of_players']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(PlayerTeam)
class PlayerTeamAdmin(admin.ModelAdmin):
    list_display = ['tournament', 'name']



