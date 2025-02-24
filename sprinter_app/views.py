from django.shortcuts import render
from allauth.socialaccount.models import SocialAccount
import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import Sprint
from .models import Task
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.http import JsonResponse

from django.contrib import messages
from django.core.mail import send_mail  
from .models import Sprint, User

from datetime import datetime
# def mainPage(request):
#     user = request.user

#     context = {
#         'is_authenticated': False,
#     }

#     if user.is_authenticated:
#         try:
#             social_account = SocialAccount.objects.get(user=user, provider='google')
#             extra_data = social_account.extra_data
#         except SocialAccount.DoesNotExist:
#             extra_data = {}

#         steam_games = []
#         steam_error = None
#         steam_id = extra_data.get('id')  

#         if steam_id:
#             url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
#             params = {
#                 'key': "3A3521710B5A489B9EED5681A92788CB",
#                 'steamid': 76561199015636727,
#                 'include_appinfo': True,
#                 'include_played_free_games': True,
#             }

#             try:
#                 response = requests.get(url, params=params)
#                 response.raise_for_status()
#                 data = response.json()
#                 print("DATA")
#                 steam_games = data.get('response', {}).get('games', [])
#                 print(steam_games)

#             except requests.RequestException as e:
#                 steam_error = str(e)

#         context = {
#             'is_authenticated': True,
#             'username': user.get_full_name(),
#             'email': user.email,
#             'google_data': extra_data,
#             'steam_games': steam_games,
#             'steam_error': steam_error,
#         }

#     return render(request, "mainPage.html", context)

from django.db.models import Q

from django.contrib.auth import get_user_model

User = get_user_model()

def get_user_photo(email):
    
    user_obj = User.objects.get(email=email)
    social_account = user_obj.socialaccount_set.first()
    if social_account:
        google_data = social_account.extra_data
        initials_avatar_url = f"https://robohash.org/{user_obj.email}"
        picture_url = google_data.get(initials_avatar_url, initials_avatar_url)
        return picture_url
    else:
        print("Este usuário não possui conta social associada.")

def mainPage(request):
    if not request.user.is_authenticated:
        return redirect('account_login')  

    user = request.user  
    sprints = Sprint.objects.filter(Q(created_by=user) | Q(users=user)).distinct()
    sprint_list = []
    for sprint in sprints:
        users_info = []
        creator_info = None  

        for participant in sprint.users.all():
            photo_url = get_user_photo(participant.email)
            participant_info = {
                'username': participant.username,
                'first_name': participant.first_name,
                'last_name': participant.last_name,
                'email': participant.email,
                'photo': photo_url,
                'initials': participant.first_name[0] + participant.last_name[0] if participant.first_name and participant.last_name else '',
                'isCreator': participant.email == sprint.created_by.email 
            }
            print(sprint.name)
            print(participant_info)

            if participant.email == sprint.created_by.email:
                creator_info = participant_info  
            else:
                users_info.append(participant_info)  

        if creator_info:
            users_info.insert(0, creator_info)

        tasks = sprint.tasks.all()
        tasks_done = sprint.tasks.filter(status="done")
        task_list = []

        for task in tasks:
            responsible = {
                'email': task.assigned_to.email,
                'name': task.assigned_to.first_name,
                'picture': get_user_photo(task.assigned_to.email),
            }
            task_list.append({
                'id': task.id,
                'name': task.name,
                'status': task.status,
                'responsible': responsible,
                'storyPoints': task.storyPoints
            })

        # Calculate stats
        if len(task_list) > 0:
            percentage_done = (len(tasks_done) / len(task_list)) * 100
            percentage_done = round(percentage_done)
        else:
            percentage_done = 0

        stats = {
            'percentageDone': percentage_done,
            'tasksQuantity': len(task_list),
            'doneTasksQuantity': len(tasks_done)
        }

        # Add sprint data to the list
        sprint_list.append({
            'id': sprint.id,
            'name': sprint.name,
            'start_date': sprint.start_date.strftime("%d/%m"),
            'end_date': sprint.end_date.strftime("%d/%m"),
            'created_by': sprint.created_by.username,
            'users': users_info,
            'tasks': task_list,  
            'stats': stats,
            'description': sprint.description
        })

    context = {
        'is_authenticated': True,
        'username': user.get_short_name(),
        'email': user.email,
        'userPicture': get_user_photo(user.email),
        'sprints': sprint_list,
        'quantitySprints': len(sprint_list),
    }
    return render(request, 'mainPage.html', context)



def finish_sprint(request, sprint_id):
    sprint = get_object_or_404(Sprint, id=sprint_id)
    sprint.delete()
    
    return JsonResponse({"message": "Sprint removida com sucesso!"}, status=200)


@login_required
def create_sprint(request):
    if request.method == 'POST':
        # Get data from the form
        name = request.POST.get('name')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        description = request.POST.get('description')

        sprint = Sprint.objects.create(
            name=name,
            start_date=start_date,
            end_date=end_date,
            description=description,
            created_by=request.user,
        )
        
        sprint.users.add(request.user)
        
        return redirect('mainPage')

    return render(request, 'mainPage.html')



def create_task(request, sprint_id):
    if request.method == "POST":
        sprint = get_object_or_404(Sprint, id=sprint_id)
        task_name = request.POST.get("name")
        responsible = request.POST.get("responsible") # email of the user
        userResponsible = get_object_or_404(User, email = responsible)
        storyPoints = request.POST.get("storyPoints")
        Task.objects.create(name=task_name, sprint=sprint, status="todo",assigned_to = userResponsible,storyPoints=storyPoints)
        return redirect('mainPage') 
        
    return render(request, 'mainPage.html')

def update_task_state(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)

        task_id = data.get('id')
        new_status = data.get('status')

        try:
            task = Task.objects.get(id=task_id)
            task.status = new_status.lower() 
            task.save()
            return JsonResponse({'success': True, 'message': 'Task updated successfully.'})
        except Task.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Task not found.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

def add_guest(request, sprint_id):
    sprint = get_object_or_404(Sprint, id=sprint_id)
    if request.method == "POST":
        email = request.POST.get("guestEmail")
        if email:

            try:
                guest = User.objects.get(email=email)
                print("GUEST")
                print(guest)
                sprint.users.add(guest)
                return redirect('mainPage') 

            except User.DoesNotExist:
                print("Usuario nao existe")

        else:
            messages.error(request, "Por favor, informe um email válido.")
    return render(request, 'mainPage.html') 