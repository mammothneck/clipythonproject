import click # for easy cli work
import requests # To fetch data using a api
import random as rand   # To chose a random element from a list
from colorama import Fore, Style    # To print in different colors and styles 

@click.group() #A group allows a command to have subcommands attached.
def gamesearch():   # a click command 
    """This command encapsulates the cli"""

#the API link 
BASE_URL = 'https://www.freetogame.com/api/games'

#filter gemes from database
@click.option('-c', '--category', help='Filter games by categories ex- shooter, racing')
@click.option('-p', '--platform', help='Filter games by platform ex- PC, Moblie, Browser')
@click.option('-s', '--sort-by', help='Sort the filtered games by release-date, popularity, alphabetical or relevance')
@gamesearch.command()
def filter_search(category: str, platform: str, sort_by: str):
    params = {  # parameters for fetching the data using the api 
        'category': category,
        'platform': platform,
        'sort-by': sort_by
    }
    try:
        #fetching data using requests lib
        response = requests.get(url=f'{BASE_URL}', params=params)

        if response.status_code == 200: # 200-> data fetched sucessfully
            data = response.json()  #json to dict.
            #printing the recieved data
            for i in range(len(data)):
                print(Fore.MAGENTA+ f"{i+1} :"+ Style.RESET_ALL)
                for k,v in data[i].items():
                    if k == 'thumbnail' or k == 'freetogame_profile_url':
                        continue
                    print(Fore.LIGHTBLUE_EX+Style.BRIGHT+ k, end=': ')
                    print(Style.RESET_ALL+Style.NORMAL+ str(v))
        
            print(Style.BRIGHT+"For extra information on a game use the game id in the " + Fore.GREEN + "search-id"+
             Fore.RESET +" command"+Style.RESET_ALL)
        # response handling
        elif response.status_code == 404: # 404-> no data found
            print(Fore.LIGHTRED_EX+Style.DIM+'No Game found'+Style.RESET_ALL)
        else:   # 500-> server error 
            print(Fore.LIGHTRED_EX+Style.DIM+'Something wrong (unexpected server errors)'+Style.RESET_ALL)
    except:
        print(Fore.LIGHTRED_EX+Style.DIM+" Error in fetching (no internet)"+Style.RESET_ALL)

#Edit Distance diff_calculator
def edit_distance(string1, string2):
    #create the 2-d matrix of size (string1+1)x(string2+1)
    dp = [ [float("inf")] * (len(string2)+1) for i in range((len(string1)+1)) ]

    #fill the lower values
    for j in range(len(string2)+1):
        dp[ len(string1) ][j] = len(string2) - j
    for i in range(len(string1)+1):
        dp[ i ][len(string2)] = len(string1) - i

    for i in range(len(string1)-1, -1, -1):    
        for j in range(len(string2)-1, -1, -1):
            if string1[i] == string2[j]: #same characters
                dp[i][j] = dp[i+1][j+1]
            else:
                dp[i][j] = 1+ min( dp[i+1][j], dp[i][j+1], dp[i+1][j+1])    #cases of insert, delete, replace
    
    return int(dp[0][0])

#search by title
@click.argument('title_words', nargs=-1)
@gamesearch.command()
def title_search(title_words: str):

    #get the string title fromlist title_words
    title=''
    for i in range(len(title_words)):
        title+= title_words[i]
        if i != len(title_words)-1:
            title+=' '

    try:
        #fetching data using requests lib
        response = requests.get(url=f'{BASE_URL}')
        if response.status_code == 200: # 200-> data fetched sucessfully
            data = response.json()   #json to dict.
            query_results=[]  # for data with similar title

            game_title_list =[] #conatins the titles of all the games
            for i in range(len(data)):
                game_title_list.append( (edit_distance( title.lower() , data[i]['title'].lower()) ,data[i]) )   #tupple of diff, data
            
            game_title_list.sort(key= lambda x: x[0]) #sort the titles according to the edit distance diff
            
            #filling the query_results list with data 
            if(game_title_list[0][0]== 0):  #same title exist
                for x in game_title_list:
                    if (x[0]!=0):
                        break
                    else:
                        query_results.append(x[1]) #x[1] contains the data 
                if len(query_results)>0:
                    print(Fore.YELLOW+"Found results are: "+Style.RESET_ALL)
                
            else:   #same title does not exist
                for x in game_title_list:
                    if(x[0]<3):
                        query_results.append(x[1]) #x[1] contains the data 
                if len(query_results)>0:
                    print(Fore.YELLOW+" No result found, showing similar results :"+ Style.RESET_ALL)
                

            if len(query_results) >0:
                #print the query data            
                for i in range(len(query_results)):
                    print(Fore.MAGENTA+ f"{i+1} :"+ Style.RESET_ALL)
                    for k,v in query_results[i].items():
                        if k == 'thumbnail' or k == 'freetogame_profile_url':
                            continue
                        print(Fore.LIGHTBLUE_EX+Style.BRIGHT+ k, end=': ')
                        print(Style.RESET_ALL+Style.NORMAL+ str(v))
            else:
                print("No game found with Title: "+Fore.LIGHTYELLOW_EX+title+Style.RESET_ALL)
        # response handling
        elif response.status_code == 404: # 404-> no data found
            print(Fore.LIGHTRED_EX+Style.DIM+'No Game found'+Style.RESET_ALL)
        else:   # 500-> server error 
            print(Fore.LIGHTRED_EX+Style.DIM+'Something wrong (unexpected server errors)'+Style.RESET_ALL)
    except:
        print(Fore.LIGHTRED_EX+Style.DIM+" Error in fetching (no internet)"+Style.RESET_ALL)

#get a random game based on filters
@click.option('-c', '--category', help='Filter games by categories ex- shooter, racing')
@click.option('-p', '--platform', help='Filter games by platform ex- PC, Moblie, Browser')
@gamesearch.command()
def random(category: str, platform: str):
    params = {    # parameters for fetching the data using the api
        'category': category,
        'platform': platform,
    }
    try:
        #fetching data using requests lib
        response = requests.get(url=f'{BASE_URL}', params=params)

        if response.status_code == 200: # 200-> data fetched sucessfully
            data = response.json()   #json to dict.
            req_id = rand.choice(data)['id']    #get a random game from the database

            #fetch extra dat for the chosen game
            rand_response = requests.get(url=f'{BASE_URL[:-1]}', params={'id':req_id})
            
            if rand_response.status_code == 200:    # 200-> data fetched sucessfully
                rand_data = rand_response.json()     #json to dict.

                #printing the recieved data
                for k,v in rand_data.items():
                    if k=='thumbnail' or k=='short_description' or k=='freetogame_profile_url' or k=='screenshots':
                        continue
                    if k == 'minimum_system_requirements':
                        print(Fore.LIGHTBLUE_EX+Style.BRIGHT+ k, end=':\n   ')
                        requirements = rand_data[k]
                        for kr,vr in requirements.items():
                            print(Fore.LIGHTBLUE_EX+Style.BRIGHT+ kr, end=': ')
                            print(Style.RESET_ALL+Style.NORMAL+ str(vr), end='\n   ')
                        continue
                
                    print(Fore.LIGHTBLUE_EX+Style.BRIGHT+ k, end=': ')
                    print(Style.RESET_ALL+Style.NORMAL+ str(v))
            # response handling
            elif response.status_code == 404: # 404-> no data found
                print(Fore.LIGHTRED_EX+Style.DIM+'No Game found')
            else:   # 500-> server error 
                print(Fore.LIGHTRED_EX+Style.DIM+'Something wrong (unexpected server errors)')
        # response handling
        elif response.status_code == 404: # 404-> no data found
            print(Fore.LIGHTRED_EX+Style.DIM+'No Game found'+Style.RESET_ALL)
        else:   # 500-> server error 
            print(Fore.LIGHTRED_EX+Style.DIM+'Something wrong (unexpected server errors)'+Style.RESET_ALL)
    except:
        print(Fore.LIGHTRED_EX+Style.DIM+" Error in fetching (no internet)"+Style.RESET_ALL)

# search by provided game id
@click.option('-id', help='Find game with requested id')
@gamesearch.command()
def search_id(id:int):
    params = {  # parameters for fetching the data using the api
        'id':id
    }
    try:
        #fetching data using requests lib
        response = requests.get(url=f'{BASE_URL[:-1]}', params=params)

        if response.status_code == 200: # 200-> data fetched sucessfully
            data = response.json()   #json to dict.

            #printing the recieved data
            for k,v in data.items():
                if k=='thumbnail' or k=='freetogame_profile_url' or k=='screenshots':
                    continue
                if k == 'minimum_system_requirements':
                    print(Fore.LIGHTBLUE_EX+Style.BRIGHT+ k, end=':\n   ')
                    requirements = data[k]
                    for kr,vr in requirements.items():
                        print(Fore.LIGHTBLUE_EX+Style.BRIGHT+ kr, end=': ')
                        print(Style.RESET_ALL+Style.NORMAL+ str(vr), end='\n   ')
                    continue
            
                print(Fore.LIGHTBLUE_EX+Style.BRIGHT+ k, end=': ')
                print(Style.RESET_ALL+Style.NORMAL+ str(v))
        # response handling
        elif response.status_code == 404: # 404-> no data found
            print(Fore.LIGHTRED_EX+Style.DIM+'No Game found'+Style.RESET_ALL)
        else:   # 500-> server error 
            print(Fore.LIGHTRED_EX+Style.DIM+'Something wrong (unexpected server errors)'+Style.RESET_ALL)
    except:
        print(Fore.LIGHTRED_EX+Style.DIM+" Error in fetching (no internet)"+Style.RESET_ALL)

#find the top 10 games played in a filtered dataset
@click.option('-c', '--category', help='Filter games by categories ex- shooter, racing')
@click.option('-p', '--platform', help='Filter games by platform ex- PC, Moblie, Browser')
@gamesearch.command()
def top_10(category: str, platform: str):
    params = {  # parameters for fetching the data using the api
        'category': category,
        'platform': platform,
        'sort-by': 'popularity'
    }
    try:
        #fetching data using requests lib
        response = requests.get(url=f'{BASE_URL}', params=params)

        if response.status_code == 200: # 200-> data fetched sucessfully
            data = response.json()  #json to dict.
            #checking the input category for print
            if not category:
                category='all'
            if not platform:
                platform='PC and Browser'

            #printing the recieved data
            print(Style.BRIGHT + Fore.GREEN+f"Top 10 free games in {category} category for {platform} are: "+Style.RESET_ALL)
            for i in range(10):
                print(Fore.MAGENTA+ f"{i+1} :"+ Style.RESET_ALL)
                for k,v in data[i].items():
                    if k == 'thumbnail' or k == 'freetogame_profile_url':
                        continue
                    print(Fore.LIGHTBLUE_EX+Style.BRIGHT+ k, end=': ')
                    print(Style.RESET_ALL+Style.NORMAL+ str(v))
            print(Style.BRIGHT+"For extra information on a game use the game id in the " + Fore.GREEN + "search-id"+ Fore.RESET +" command"+Style.RESET_ALL)
        # response handling
        elif response.status_code == 404: # 404-> no data found
            print(Fore.LIGHTRED_EX+Style.DIM+'No Game found'+Style.RESET_ALL)
        else:   # 500-> server error 
            print(Fore.LIGHTRED_EX+Style.DIM+'Something wrong (unexpected server errors)'+Style.RESET_ALL)
    except:
        print(Fore.LIGHTRED_EX+Style.DIM+" Error in fetching (no internet)"+Style.RESET_ALL)
        
@gamesearch.command()
def categories():
    # print all the categories  
    print(Style.BRIGHT+Fore.GREEN+"selectable categories are: "+ Style.RESET_ALL)
    categories_list = ['mmorpg', 'shooter', 'strategy', 'moba', 'racing', 'sports', 'social', 'sandbox', 'open-world', 'survival', 'pvp', 'pve', 'pixel', 'voxel', 'zombie', 'turn-based', 'first-person', 'third-Person', 'top-down', 'tank', 'space', 'sailing', 'side-scroller', 'superhero', 'permadeath', 'card', 'battle-royale', 'mmo', 'mmofps', 'mmotps', '3d', '2d', 'anime', 'fantasy', 'sci-fi', 'fighting', 'action-rpg', 'action, military', 'martial-arts', 'flight', 'low-spec', 'tower-defense', 'horror', 'mmorts']
    for cat in categories_list:
        print(Style.BRIGHT+cat+Style.RESET_ALL, end='  ,')

if __name__ == '__main__':
    gamesearch(prog_name='gamesearch')
