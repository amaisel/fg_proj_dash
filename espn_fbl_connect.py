#!pip install pybaseball
# pip install espn_api

def league_connect(year = 2024):
    from espn_api.baseball import League
    import pandas as pd

    s2 = 'AEBLRaiU8XDatjHAGXM8JcOw23vsrTiSc9SL6HZDuCvPjKJWEDW7BXRpVZ8m2IZOwxDgvKaUu1U%2B5w%2BlGJoLu%2FUJBqcul1h%2BQahvZz45y%2BGkpOBmn6SpOrL8zO8%2FRDQwSltCziiDWzUEleipDT%2BD44g11SHhAIWYsCpHs45iNMpBWR1n%2FZQcrlPMtgALvI2DsN%2FlHA0FqzYMgaQglGc7NjTvb%2Bg47u%2Fiu1oXoeW%2FhceNPnW4E6aT1BmCBYiTa53OgxQSHcF87zk6hbEBlWTF2mHD'
    swid = '{4A2101AD-432A-49A5-A0B5-727A6F21B2F2}'
    my_league = League(league_id=180852, year=year, espn_s2=s2, swid=swid)
   

    return my_league

#my_team.__dict__

def fg_league_connect(league,is_offszn = False):

    from fantasydash.import_fg_projections import pull_projections

    projections = pull_projections(is_offszn=is_offszn)

    bat_proj = projections['atc_bat']
    pitch_project = projections['atc_pitch']

    my_league = league_connect(2024)
    

 
    teams = my_league.teams
    # get data for opposing teams
    other_teams = [team for team in teams if team.team_name.strip() != 'Frisky Felines']

    my_team = [team for team in teams if team.team_name.strip() == 'Frisky Felines'][0]

    # get free agents

    free_agents = my_league.free_agents(size=1000)

    # get my team's roster
    my_roster = my_team.roster






    

