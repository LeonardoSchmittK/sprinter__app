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

from .utils import list_sprint_files  
from .utils import upload_sprint_file_s3 
from .utils import remove_file_s3 

import uuid
import re
import json
import boto3


from django.db.models import Q

from django.contrib.auth import get_user_model

User = get_user_model()

def get_user_photo(email):
    return f"https://robohash.org/{email}"  


def upload_sprint_file(request, sprint_id):
    upload_sprint_file_s3(request,sprint_id)
    return redirect('mainPage')


def get_sprint_files(request, sprint_id):
    result = list_sprint_files(sprint_id)
    return JsonResponse(result)

def mainPage(request):
    if not request.user.is_authenticated:
        return redirect('account_login')  

    user = request.user  
    archived_filter = request.POST.get('archived', 'false')  

    if archived_filter == 'true':
        sprints = Sprint.objects.filter(Q(created_by=user) | Q(users=user), is_archived=True).distinct()
    else:
        sprints = Sprint.objects.filter(Q(created_by=user) | Q(users=user), is_archived=False).distinct()

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

        sprint_list.append({
            'id': sprint.id,
            'name': sprint.name,
            'start_date': sprint.start_date.strftime("%d/%m"),
            'end_date': sprint.end_date.strftime("%d/%m"),
            'created_by': sprint.created_by.username,
            'created_by_email': sprint.created_by.email,
            'users': users_info,
            'tasks': task_list,  
            'stats': stats,
            'description': sprint.description,
            'is_archived': sprint.is_archived,
        })

    context = {
        'is_authenticated': True,
        'username': user.get_short_name() or user.username,
        'email': user.email,
        'userPicture': get_user_photo(user.email),
        'sprints': sprint_list,
        'quantitySprints': len(sprint_list),
        'archived_filter': archived_filter,
    }
    return render(request, 'mainPage.html', context)


def remove_file(request):
    return remove_file_s3(request)


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
            s3_folder = f"{request.user.email.lower()}-{re.sub(r'[^a-zA-Z0-9]+', '-', name.lower())}-{uuid.uuid4().hex[:10]}"
        )
        
        sprint.users.add(request.user)
        
        return redirect('mainPage')

    return render(request, 'mainPage.html')



def create_task(request, sprint_id):
    if request.method == "POST":
        try:
            sprint = get_object_or_404(Sprint, id=sprint_id)
            task_name = request.POST.get("name")
            responsible_email = request.POST.get("responsible")  # email of the user
            story_points = request.POST.get("storyPoints")

            if not task_name or not responsible_email or not story_points:
                messages.error(request, "Todos os campos são obrigatórios para adicionar uma tarefa.")
                return redirect('mainPage')

            user_responsible = get_object_or_404(User, email=responsible_email)

            Task.objects.create(
                name=task_name,
                sprint=sprint,
                status="todo",
                assigned_to=user_responsible,
                storyPoints=story_points
            )

            messages.success(request, "Task created successfully!")
            return redirect('mainPage') 

        except IntegrityError:
            messages.error(request, f"Tente mais tarde, um Erro de banco de dados ocorreu ao criar a tarefa: {str(e)}")
        except Exception as e:
            messages.error(request, f"Erro ao criar a tarefa: {str(e)}")
        
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

def archive_sprint(request, sprint_id):
    sprint = get_object_or_404(Sprint, id=sprint_id)
    sprint.is_archived = True  
    sprint.save()
    send_sprint_finished_email()
    return redirect("mainPage")  

def remove_guest(request, sprint_id):
    if request.method == "POST":
        guest_email = request.POST.get("responsible")

        sprint = get_object_or_404(Sprint, id=sprint_id)

        try:
            guest_user = User.objects.get(email=guest_email)

            if guest_user in sprint.users.all():
                sprint_creator = sprint.created_by 

                tasks = sprint.tasks.filter(assigned_to=guest_user)
                tasks.update(assigned_to=sprint_creator)

                sprint.users.remove(guest_user)
                sprint.save()

                return redirect("mainPage") 
            else:
                return JsonResponse({"success": False, "message": "Usuário não faz parte desta Sprint"})

        except User.DoesNotExist:
            return JsonResponse({"success": False, "message": "Usuário não encontrado"})

        return redirect("mainPage") 


def send_sprint_finished_email():
    return
    ses = boto3.client('ses', region_name='sa-east-1')

    response = ses.send_email(
        Source="leoeyeschmittk@gmail.com",
        Destination={"ToAddresses": ["leoeyeschmittk@gmail.com","biaarevalofreitas@gmail.com"]},
        Message={
            "Subject": {"Data": "Sprint Finalizada 🚀"},
            "Body": {
                "Html": {
                    "Data": """
                    <!DOCTYPE html>
                    <html lang="pt-BR">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Sprint Concluída</title>
                        <style>
                            body {
                                font-family: Arial, sans-serif;
                                background-color: #f4f4f4;
                                padding: 20px;
                                text-align: center;
                            }
                            .container {
                                max-width: 600px;
                                background: #ffffff;
                                padding: 20px;
                                border-radius: 8px;
                                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
                                margin: auto;
                            }
                            h1 {
                                color: #2C3E50;
                            }
                            .button {
                                display: inline-block;
                                padding: 10px 20px;
                                color: #fff;
                                background: #3498db;
                                text-decoration: none;
                                border-radius: 5px;
                                margin-top: 20px;
                            }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            </br>
                        </div>
                    </body>
                    </html>
                    """
                }
            }
        }
    )



def update_task(request):
    if request.method == "POST":
        data = json.loads(request.body)

        task_id = data.get('idToEdit')
        new_name = data.get('newName')
        story_points = data.get('newStoryPoints')
        new_email = data.get('newEmail')
        try:
            task = Task.objects.get(id=task_id)

            if new_name:
                task.name = new_name

            if story_points is not None:
                task.storyPoints = story_points

            if new_email: 
                try:
                    new_user = User.objects.get(email=new_email)
                    task.assigned_to = new_user
                except User.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'User not found with this email.'})

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
                sprint.users.add(guest)
                return redirect('mainPage')  
            except User.DoesNotExist:
                messages.error(request, "Não é possível adicionar usuários não cadastrados.")
                return redirect('mainPage') 

        else:
            messages.error(request, "Por favor, informe um email válido.")
            return redirect('mainPage')  

    return redirect('mainPage')

def remove_task(request):
    data = json.loads(request.body)
    taskToRemove = get_object_or_404(Task, id=data["idToRemove"])
    taskToRemove.delete()
    
    return JsonResponse({"success": "Task removida com sucesso!"}, status=200)
