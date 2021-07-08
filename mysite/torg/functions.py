import random

def prep_json(players):
    print("TERAZ")
    json_data = {} # Tworzenie pustego słownika/ jsona
    shuffle_players = players.copy() # tworzenie kopii zawodnikow
    random.shuffle(shuffle_players) # przemieszanie zawodników w formi listy

    i = len(shuffle_players) # sprawdzenie dlugosci listy
    num_of_col = 0 # numer kolumny, czyli fazy turnieju
    while i >= 1: # dopoki liczba graczy w liscie jest wieksza rowna 1 to petla bedzie sie wykonywac
        num_of_col += 1 # tworzenie meczy dla kolumny pierwszej itd
        i //= 2 # Dzielimy liczbe graczy w pieerwszej fazie na 2 bo dwóch graczy przypada na jeden mecz
        # print('Liczba meczy', i, 'w linii', num_of_col)
        json_data.setdefault(str('column_' + str(num_of_col)), {}) # Tworzy slownik z kluczem kolumna + numer kolumny
        for k in range(i): # dla każdej pary druzyn/graczy w fazie tworzy sie mecze
            json_data[('column_' + str(num_of_col))].setdefault('match_' + (str(num_of_col)+'_'+str(k + 1)), {})
            # dla danego klucza kolumny tworzymy mecz z numerem. Jest to słownik, wartoscia bedzie para graczy
            if num_of_col == 1: # Jeżeli faza turnieju to 1, do meczy zostana przypisani gracze
                json_data[('column_' + str(num_of_col))][('match_' + (str(num_of_col)+'_'+str(k + 1)))].setdefault(
                    str(shuffle_players.pop(0)))
                json_data[('column_' + str(num_of_col))][('match_' + (str(num_of_col)+'_'+str(k + 1)))].setdefault(
                    str(shuffle_players.pop(0)))

    return json_data # Na podstawie tego jsona


def the_winner_is(match, match_detail):
    if match.score_1 != None and match.score_2 != None: # Sprawdzenie czy w trakcie zapisu formularza
        #spełniony jest warunek o tym ze musi byc podany poprawnie
        # print(match.score_1 >=0)
        # print(match.score_2 >= 0)
        if (match.score_1 > match.score_2) and (match.score_1 >=0 or match.score_2 >=0):
            # print("Przechodziiii", match.player_team_1)
            # print("Zwycięzca", match.name)
            first_num = int(match.name[-3]) + 1 # Sprawdzanie pierwsze numeru meczu np. match_1_1, 1 - pierwsza faza, 1 - pierwszy mecz
            if int(match.name[-1]) % 2 == 0: # Jeżeli drugi numer jest pazysty
                second_num = int(match.name[-1]) // 2 # Jezeli mecz miał numer 2 to przeniesiony jest do nastepnej fazy do meczu 1 poniewaz 2/2 = 1
            else:
                second_num = (int(match.name[-1]) + 1) // 2 # jezeli mecz mial numer 1 to dodajemy niego 1 i dzielimy przez dwa przez trafi do meczu 1 nastepnej fazy
            new_name_match = match.name[:-3] + str(first_num) + "_" + str(second_num) # nazwa nowego meczu do ktorego ma trafic zawodnik z meczy aktualnego

            for next_match in match_detail:
                if new_name_match == next_match.name: # szukanie nazwy meczu takie jak powstała nazwa w linijce 41
                    if not next_match.player_team_1: # jesli nie ma jeszcze graczy w kolejnym meczu to
                        next_match.player_team_1 = match.player_team_1 # przypisuje to pierwszego pola player_team_1
                        next_match.save(update_fields=['player_team_1'])
                    else:
                        if next_match.player_team_1 != match.player_team_1:
                            next_match.player_team_2 = match.player_team_1
                            next_match.save(update_fields=['player_team_2'])

        elif (match.score_1 < match.score_2) and (match.score_1 >=0 and match.score_2 >=0):
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

#Przy wyzszych wartościach -3 wskazuje na "_" bo np. match_1_10
def rename_match_name(match, match_detail):
    phases = int(str(match_detail.last())[-3])
    if len(str(match)) == 9:
        if int(str(match)[-3]) == phases:
            phase = ' FINAŁ'
            return phase
        elif int(str(match)[-3]) == phases - 1:
            phase = 'PÓŁFINAŁ - ' + str(match)[-1]
            return phase
        elif int(str(match)[-3]) == phases - 2:
            phase = 'ĆWIERĆFINAŁ - ' + str(match)[-1]
            return phase
        elif int(str(match)[-3]) == phases - 3:
            phase = '1/8 TURNIEJU - ' + str(match)[-1]
            return phase
        elif int(str(match)[-3]) == phases - 4:
            phase = '1/16 TURNIEJU - ' + str(match)[-1]
            return phase
    elif len(str(match)) == 10:
        if int(str(match)[-4]) == phases - 4:
            phase = '1/16 TURNIEJU - ' + str(match)[-2:]
            return phase



