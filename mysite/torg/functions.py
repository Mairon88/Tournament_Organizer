import random

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


def the_winner_is(match, match_detail):
    if match.score_1 != None and match.score_2 != None:
        print(match.score_1 >=0)
        print(match.score_2 >= 0)
        if (match.score_1 > match.score_2) and (match.score_1 >=0 or match.score_2 >=0):
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

        elif (match.score_1 < match.score_2) and (match.score_1 >=0 and match.score_2 >=0):
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

#Przy wyzszych wartościach -3 wskazuje na "_" bo np. match_1_10
def rename_match_name(match, match_detail):
    phases = int(str(match_detail.last())[-3])
    if int(str(match)[-3]) == phases:
        phase = 'FINAŁ'
        return phase
    elif int(str(match)[-3]) == phases-1:
        phase = 'PÓŁFINAŁ - '+ str(match)[-1]
        return phase
    elif int(str(match)[-3]) == phases - 2:
        phase = 'ĆWIERĆFINAŁ - ' + str(match)[-1]
        return phase
    elif int(str(match)[-3]) == phases - 3:
        phase = '1/8 TURNIEJU - ' + str(match)[-1]
        return phase
    elif int(str(match)[-4]) == phases - 4:
        phase = '1/16 TURNIEJU - ' + str(match)[-2:]
        return phase
    elif int(str(match)[-4]) == phases - 5:
        phase = '1/32 TURNIEJU - ' + str(match)[-2:]
        return phase

