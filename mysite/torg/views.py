from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login
from .forms import UserRegistrationForm, UserEditForm, \
                   ProfileEditForm, TournamentRegistrationForm, AddPlayerTeamForm, \
                   MatchForm, ScoreForm, YTForm, DescriptionForm
from django.contrib.auth.decorators import login_required
from .models import Profile, Tournament, PlayerTeam, Match
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.shortcuts import redirect
import datetime
from . import functions


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            profile = Profile.objects.create(user=new_user)
            return render(request, 'account/register_done.html',
                          {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request,
                  'account/register.html',
                  {'user_form': user_form})

@login_required
def dashboard(request):
    ong_tour = len(Tournament.status_ongoing.filter(author = request.user))
    fin_tour = len(Tournament.status_completed.filter(author=request.user))
    pen_tour = len(Tournament.status_waiting.filter(author=request.user))

    return render(request, 'account/dashboard.html',
                  {'section': 'dashboard',
                   'ong_tour': ong_tour,
                   'fin_tour': fin_tour,
                   'pen_tour': pen_tour,
                   })

@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile,
                                       data=request.POST,
                                       files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
    else:
        user_form=UserEditForm(instance=request.user)
        profile_form=ProfileEditForm(instance=request.user.profile)
    return render(request,
                  'account/edit.html',
                  {'user_form': user_form,
                   'profile_form': profile_form})

@login_required
def create_tournaments(request):
    if request.method == 'POST':
        users = get_user_model()
        obj = users.objects.get(id=request.user.id)
        tournament_form = TournamentRegistrationForm(initial={'author':obj}, data=request.POST)
        if tournament_form.is_valid():
            new_tournament = tournament_form.save(commit=False)
            new_tournament.author = obj
            try:
                assert new_tournament.tournament_type == 'tree' and new_tournament.num_of_players in [2,4,8,16,32]
                new_tournament.save()

            except IntegrityError:
                message = "Turniej o podanej nazwie ju?? istnieje, prosz?? zmie?? nazw?? dla nowego turnieju"
                return render(request,
                              'account/create_tournaments.html',
                                          {'tournament_form': tournament_form,
                                          "message": message})

            except:
                message = "Liczba graczy/dru??yn dla turnieju drzewkowego powinna wynosi?? 2,4,8,16 lub 32."
                return render(request,
                              'account/create_tournaments.html',
                                          {'tournament_form': tournament_form,
                                          "message": message})


            return redirect('/waiting_tournaments/')
    else:
        tournament_form = TournamentRegistrationForm()

    return render(request,
                  'account/create_tournaments.html',
                  {'tournament_form': tournament_form})

@login_required
def edit_tournaments(request, year, month, day, tournament, id):
    tournament = get_object_or_404(Tournament, slug=tournament,
                                                created__year=year,
                                                created__month=month,
                                                created__day=day,
                                                id=id)

    if request.method == 'POST':
        users = get_user_model()
        obj = users.objects.get(id=request.user.id)
        tournament_form = TournamentRegistrationForm(request.POST, request.FILES, instance=tournament)
        if tournament_form.is_valid():
            tournament_form.save()
            return redirect(request.path.rstrip('edit/'))
            # return redirect('/account/waiting_tournaments/')

    tournament_form = TournamentRegistrationForm(instance=tournament)

    return render(request,
                  'account/edit_tournaments.html',
                  {'tournament_form': tournament_form})

@login_required
def ongoing_tournaments(request):
    tournaments = Tournament.status_ongoing.filter(author = request.user)

    return render(request,
                  'account/ongoing_tournaments.html',
                  {'tournaments':tournaments
                   })


@login_required
def completed_tournaments(request):
    tournaments = Tournament.status_completed.filter(author = request.user)
    return render(request,
                  'account/completed_tournaments.html',
                  {'tournaments':tournaments})

@login_required
def waiting_tournaments(request):
    tournaments = Tournament.status_waiting.filter(author = request.user)
    return render(request,
                  'account/waiting_tournaments.html',
                  {'tournaments':tournaments})


def tournament_detail(request, year, month, day, tournament, id):
    tournament = get_object_or_404(Tournament, slug=tournament,
                                                created__year=year,
                                                created__month=month,
                                                created__day=day,
                                                id=id)

    all_players = PlayerTeam.objects.all()
    all_matches = Match.objects.filter(tournament = tournament).values_list('name', flat=True)
    match_detail = Match.objects.filter(tournament=tournament)

    players = [player for player in all_players if (player.tournament.name == tournament.name and
                                                    player.tournament.author == request.user)]

    if tournament.json_data == {} and tournament.tournament_status == 'ongoing':
        tournament.json_data = functions.prep_json(players)
        tournament.save()
    else:
        pass
        # print("Juz nie zapisuje")
    # print(tournament.json_data)

    match_form = MatchForm(initial={'tournament': tournament}, data=request.POST)

    if match_form.is_valid():
        # print("Zaczynam tworzy?? mecze")
        for column in tournament.json_data.keys():
            # print("FAZA:",column)
            # print(tournament.json_data[column])
            for matches in tournament.json_data[column].keys():
                match_form = MatchForm(initial={'tournament': tournament}, data=request.POST)
                new_match = match_form.save(commit=False)
                # print("MECZ:",matches)
                new_match.name = matches
                # print(tournament.json_data[column][matches])
                for player in tournament.json_data[column][matches]:
                    # print("GRACZ:",player)
                    if not new_match.player_team_1:
                        new_match.player_team_1 = player
                    else:
                        new_match.player_team_2 = player

                new_match.tournament = tournament
                # print("Utorzy??em mecze")
                if new_match.name not in all_matches:
                    new_match.save()


    if request.method == 'POST':
        player_team_form = AddPlayerTeamForm(initial={'tournament': tournament}, data=request.POST)
        if player_team_form.is_valid():
            new_player_team = player_team_form.save(commit=False)
            new_player_team.tournament = tournament
            try:
                new_player_team.save()

            except IntegrityError:
                message = "Gracz lub dry??yna o podanej nazwie ju?? istnieje w tym turnieju, prosz?? zmieni?? nazw??"
                return render(request,
                                      'account/tournament_detail.html',
                                      {'tournament': tournament,
                                       'players': players,
                                        'player_team_form': player_team_form,
                                       'message': message})
            return HttpResponseRedirect(request.path_info)

    else:
        player_team_form = AddPlayerTeamForm()

    if request.method == "POST" and request.POST.get('delete_items'):
        items_to_delete = request.POST.getlist('delete_items')
        PlayerTeam.objects.filter(pk__in=items_to_delete).delete()
        return HttpResponseRedirect(request.path_info)


    for match_2 in match_detail:
        if match_2.phase == '':
            print(match_2, match_detail)
            match_2.phase = functions.rename_match_name(match_2, match_detail)
            match_2.save(update_fields=['phase'])



    return render(request,
                  'account/tournament_detail.html',
                  {'tournament': tournament,
                   'players': players,
                    'player_team_form': player_team_form,
                    'match_form': match_form,
                   'all_matches': all_matches,
                   'match_detail': match_detail,
                   'winner':tournament.winner,
                   })

@login_required
def tournament_delete(request, year, month, day, tournament, id):
    tournament = get_object_or_404(Tournament, slug=tournament,
                                                created__year=year,
                                                created__month=month,
                                                created__day=day,
                                                id=id)

    if request.method == 'POST' and request.POST.get('delete'):
        tournament.delete()
        return redirect('/')

    return render(request,
                  'account/tournament_delete.html',
                  {'tournament': tournament})

@login_required
def tournament_complete(request, year, month, day, tournament, id):
    tournament = get_object_or_404(Tournament, slug=tournament,
                                                created__year=year,
                                                created__month=month,
                                                created__day=day,
                                                id=id)

    if request.method == 'POST' and request.POST.get('complete'):
        tournament.tournament_status = 'complete'
        tournament.save()
        return redirect('/completed_tournaments/')

    return render(request,
                  'account/tournament_complete.html',
                  {'tournament': tournament})

@login_required
def tournament_start(request, year, month, day, tournament, id):
    tournament = get_object_or_404(Tournament, slug=tournament,
                                                created__year=year,
                                                created__month=month,
                                                created__day=day,
                                                id=id)
    if request.method == 'POST' and request.POST.get('start'):
        tournament.tournament_status = 'ongoing'
        tournament.start_date = datetime.datetime.today()
        tournament.save()
        return redirect('/ongoing_tournaments/')

    return render(request,
                  'account/tournament_start.html',
                  {'tournament': tournament})



def match_detail(request, match):
    match = get_object_or_404(Match, slug=match)
    tournaments = Tournament.objects.filter(author=request.user)
    print(tournaments)
    print(match.tournament)

    if request.method == 'POST' and request.POST.get('desc'):
        desc_form = DescriptionForm(request.POST, request.FILES, instance=match)
        video_form = YTForm(request.POST, request.FILES, instance=match)
        if desc_form.is_valid() and video_form.is_valid():
            new_desc = desc_form.save(commit=False)
            new_desc.save()
            new_video = video_form.save(commit=False)
            new_video.save()
            return HttpResponseRedirect(request.path_info)

    video_form = YTForm(instance=match)
    score_form = ScoreForm(instance=match)
    desc_form = DescriptionForm(instance=match)

    if request.method == 'POST' and request.POST.get('save'):
        score_form = ScoreForm(request.POST, request.FILES, instance=match)

        if score_form.is_valid():
            new_score = score_form.save(commit=False)
            try:
                assert new_score.score_1 >= 0
                assert new_score.score_2 >= 0
                assert new_score.score_1 != None
                assert new_score.score_2 != None

                try:
                    assert new_score.score_1 != new_score.score_2
                    new_score.save()
                    return HttpResponseRedirect(request.path_info)
                except:
                    message = "W turnieju nie mo??e by?? remisu, wynik nie zostanie zapisany"
                    return render(request,
                                  'account/match_detail.html',
                                  {'match': match,
                                   'phase': match.phase,
                                   'score_form': score_form,
                                   'message': message,
                                   'tournaments':tournaments})

            except:
                message = "Nie podano wynik??w dla obu dru??yn lub wynik jest mniejszy od 0"
                return render(request,
                              'account/match_detail.html',
                              {'match': match,
                               'phase': match.phase,
                               'score_form': score_form,
                               'message': message,
                               'video_form': video_form,
                                'desc_form': desc_form,
                               'tournaments':tournaments})




    match_detail = Match.objects.filter(tournament=match.tournament)
    all_matches = Match.objects.filter(tournament=match.tournament).values_list('name', flat=True)



    for match_2 in match_detail:
        functions.the_winner_is(match_2, match_detail)

    if match_detail and (match_detail.last().score_1 != None and match_detail.last().score_2 != None):
        match.tournament.tournament_status = 'complete'
        if match_detail.last().score_1 > match_detail.last().score_2:
            match.tournament.winner = match_detail.last().player_team_1
        else:
            match.tournament.winner = match_detail.last().player_team_2
        match.tournament.save(update_fields=['tournament_status', 'winner'])

    return render(request,
                  'account/match_detail.html',
                  {'match': match,
                   'score_form': score_form,
                   'phase': match.phase,
                   'video_form': video_form,
                   'desc_form': desc_form,
                   'tournaments':tournaments})

