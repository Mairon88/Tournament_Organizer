from django.contrib import admin
from .models import Profile, Tournament, PlayerTeam, Match

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'photo']

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ['name','author', 'description', 'slug', 'created', 'start_date', 'end_date',
                    'tournament_status', 'tournament_type', 'num_of_players', 'json_data']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(PlayerTeam)
class PlayerTeamAdmin(admin.ModelAdmin):
    list_display = ['tournament', 'name']

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['tournament','name', 'player_team_1','score_1', 'player_team_2', 'score_2', 'phase', 'youtube']



