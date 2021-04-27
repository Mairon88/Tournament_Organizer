from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login
from .forms import LoginForm, UserRegistrationForm, UserEditForm, \
                   ProfileEditForm, TournamentRegistrationForm, AddPlayerTeamForm, MatchForm, ScoreForm
from django.contrib.auth.decorators import login_required
from .models import Profile, Tournament, PlayerTeam, Match
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.shortcuts import redirect
from django.core.exceptions import ValidationError
import random


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username = cd['username'], password = cd['password'])

            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Uwierzytelnianie zakończyło sie sukcesem')
                else:
                    return HttpResponse('Konto jest zablokowane.')
            else:
                return HttpResponse('Nieprawidłowe dane uwierzytelniające.')

    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})

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
    return render(request, 'account/dashboard.html',
                  {'section': 'dashboard'})

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
                message = "Turniej o podanej nazwie już istnieje, proszę zmień nazwę dla nowego turnieju"
                return render(request,
                              'account/create_tournaments.html',
                                          {'tournament_form': tournament_form,
                                          "message": message})

            except:
                message = "Liczba graczy/drużyn dla turnieju drzewkowego powinna wynosić 2,4,8,16 lub 32."
                return render(request,
                              'account/create_tournaments.html',
                                          {'tournament_form': tournament_form,
                                          "message": message})


            return redirect('/account/waiting_tournaments/')
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

@login_required
def tournament_detail(request, year, month, day, tournament, id):
    tournament = get_object_or_404(Tournament, slug=tournament,
                                                created__year=year,
                                                created__month=month,
                                                created__day=day,
                                                id=id)

    all_players = PlayerTeam.objects.all()
    all_matches = Match.objects.filter(tournament = tournament).values_list('name', flat=True)
    match_detail = Match.objects.filter(tournament=tournament)

    # print(match_detail)
    # print(list(all_matches))
    players = [player for player in all_players if (player.tournament.name == tournament.name and
                                                    player.tournament.author == request.user)]

    ##########################
    # Próba

    def prep_json(players):
        json_data = {}
        shuffle_players = players.copy()
        random.shuffle(shuffle_players)

        length = len(shuffle_players)
        i = length
        num_of_col = 0
        while i >= 1:
            num_of_col += 1
            i //= 2
            # print('Liczba meczy', i, 'w linii', num_of_col)
            for j in range(num_of_col):
                json_data.setdefault(str('column_' + str(num_of_col)), {})
                for k in range(i):
                    json_data[('column_' + str(num_of_col))].setdefault('match_' + (str(num_of_col)+'_'+str(k + 1)), {})
                    if num_of_col == 1:
                        json_data[('column_' + str(num_of_col))][('match_' + (str(num_of_col)+'_'+str(k + 1)))].setdefault(
                            str(shuffle_players.pop(0)))
                        json_data[('column_' + str(num_of_col))][('match_' + (str(num_of_col)+'_'+str(k + 1)))].setdefault(
                            str(shuffle_players.pop(0)))

        return json_data

    ##########################

    if tournament.json_data == {} and tournament.tournament_status == 'ongoing':
        tournament.json_data = prep_json(players)
        tournament.save()
        # print("Zapisałem dane")
    else:
        pass
        # print("Juz nie zapisuje")
    # print(tournament.json_data)

    match_form = MatchForm(initial={'tournament': tournament}, data=request.POST)

    if match_form.is_valid():
        # print("Zaczynam tworzyć mecze")
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
                # print("Utorzyłem mecze")
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
                message = "Gracz lub dryżyna o podanej nazwie już istnieje w tym turnieju, proszę zmienić nazwę"
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


    #===========================
    # Próba wypchnięcia zwyciezcow do nastepnych etapów
    def push_to_next_level(match):
        if match.score_1 and match.score_2:
            if (match.score_1 and match.score_2) and (match.score_1 > match.score_2):
                print("Przechodziiii", match.player_team_1)
                print("Zwycięzca", match.name)
                first_num = int(match.name[-3]) + 1
                if int(match.name[-1]) % 2 == 0:
                    second_num = int(match.name[-1]) // 2
                else:
                    second_num = (int(match.name[-1]) + 1) // 2
                new_name_match = match.name[:-3] + str(first_num) + "_" + str(second_num)

                for next_match in match_detail:
                    if new_name_match == next_match.name:
                        if not next_match.player_team_1:
                            next_match.player_team_1 = match.player_team_1
                            next_match.save(update_fields=['player_team_1'])
                        else:
                            if next_match.player_team_1 != match.player_team_1:
                                next_match.player_team_2 = match.player_team_1
                                next_match.save(update_fields=['player_team_2'])

            elif (match.score_1 and match.score_2) and (match.score_1 < match.score_2):
                print("Przechodzi", match.player_team_2)
                print("Zwycięzca", match.name)
                first_num = int(match.name[-3]) + 1
                if int(match.name[-1]) % 2 == 0:
                    second_num = int(match.name[-1]) // 2
                else:
                    second_num = (int(match.name[-1]) + 1) // 2
                new_name_match = match.name[:-3] + str(first_num) + "_" + str(second_num)

                for next_match in match_detail:
                    if new_name_match == next_match.name:
                        if not next_match.player_team_1:
                            next_match.player_team_1 = match.player_team_2
                            next_match.save(update_fields=['player_team_1'])
                        else:
                            if next_match.player_team_1 != match.player_team_2:
                                next_match.player_team_2 = match.player_team_2
                                next_match.save(update_fields=['player_team_2'])



    for match in match_detail:
        push_to_next_level(match)





    return render(request,
                  'account/tournament_detail.html',
                  {'tournament': tournament,
                   'players': players,
                    'player_team_form': player_team_form,
                    'match_form': match_form,
                   'all_matches': all_matches,
                   'match_detail':match_detail,
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
        return redirect('/account/ongoing_tournaments/')

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
        return redirect('/account/completed_tournaments/')

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
        tournament.save()
        return redirect('/account/ongoing_tournaments/')

    return render(request,
                  'account/tournament_start.html',
                  {'tournament': tournament})


@login_required
def match_detail(request, match):
    match = get_object_or_404(Match, slug=match)

    if request.method == 'POST':
        score_form = ScoreForm(request.POST, request.FILES, instance=match)

        if score_form.is_valid():
            new_score = score_form.save(commit=False)
            try:
                assert new_score.score_1 > 0
                assert new_score.score_2 > 0
                assert new_score.score_1 != None
                assert new_score.score_2 != None

                try:
                    assert new_score.score_1 != new_score.score_2
                    print("Jestem tutaj")
                    new_score.save()
                    return HttpResponseRedirect(request.path_info)
                except:
                    message = "W turnieju nie może być remisu, wynik nie zostanie zapisany"
                    return render(request,
                                  'account/match_detail.html',
                                  {'match': match,
                                   'score_form': score_form,
                                   'message': message})

            except:
                message = "Nie podano wyników dla obu drużyn lub wynik jest mniejszy od 0"
                return render(request,
                              'account/match_detail.html',
                              {'match': match,
                               'score_form': score_form,
                               'message': message})


    score_form = ScoreForm(instance=match)

    return render(request,
                  'account/match_detail.html',
                  {'match': match,
                   'score_form': score_form})

