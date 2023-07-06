from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages # Django flash messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message, Profile
from .forms import RoomForm, UserForm, RegistrationForm, ProfileForm


# Create your views here.

# rooms = [
#     {"id": 1, "name": "Let's Learn Python"},
#     {"id": 2, "name": "Designers"},
#     {"id": 3, "name": "Fortnite Scrims"},
# ]

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get("username").lower() # lower cases the username. same cocept applied to register as well
        password = request.POST.get("password")

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "User does not exist") # A Django flash message

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Username Or Password Does Not Exist")
    context = {"page": page}
    return render(request, "core/login_register.html", context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.username = user.username.lower() # lowercases the username
            user.save()
            prof_instance = User.objects.get(username=user.username)
            profile = Profile(user=prof_instance)
            profile.save()
            login(request, user) # automatically login the user after registration
            messages.success(request, f"Registration was successful. logged in as {user.username}")
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration.')

    else:
        form = RegistrationForm()

    return render(request, 'core/login_register.html', {"form": form})

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else '' # search method: this sets topics to query url (remove the if statement and see what happens)
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | # Pretty awesome technique to search | represents for or and & represents for and
        Q(name__icontains=q) |
        Q(description__icontains=q)
    ) # makes the topic name non-sensitive

    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {"rooms": rooms, "topics": topics, "room_count": room_count, "room_messages": room_messages}
    return render(request, 'core/index.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all() # gets content from the child (Room is the parent class and _set.all comes after child model name without capitilization)
    participants = room.participants.all()
    if request.method == "POST":
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get("body")
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {'room': room, "room_messages": room_messages, "participants": participants}
    return render(request, 'core/room.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all() # gets the children (all the rooms that this user has) of a model using set method
    room_message = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, "rooms": rooms, "room_messages": room_message, "topics": topics}
    return render(request, 'core/profile.html', context)


@login_required(login_url="login")
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description=request.POST.get('description')
        )
        return redirect('home')


    context = {'form': form, 'topics': topics}
    return render(request, 'core/room_form.html', context)

@login_required(login_url="login")
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse("You are not allowed here!")

    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()

        return redirect('home')

    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, "core/room_form.html", context)

@login_required(login_url="login")
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("You are not allowed here!")

    if request.method == "POST":
        room.delete()
        return redirect('home')
    return render(request, "core/delete.html", {'obj': room})


@login_required(login_url="login")
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse("You are not allowed here!")

    if request.method == "POST":
        message.delete()
        return redirect('home')
    return render(request, "core/delete.html", {'obj': message})


@login_required(login_url="login")
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    try:
        user_profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        return HttpResponse("Invalid User Profile")

    if request.method == "POST":
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=user_profile)

        if user_form.is_valid() and profile_form.is_valid():
            finaluser = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = finaluser

            if 'image' in request.FILES:
                profile.image = request.FILES['image']
            profile.save()
            return redirect('user-profile', pk=user.id)

        else:
            messages.warning(request, "An error has occured")

    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(request.POST, instance=user_profile)

    context = {'user_form': user_form, 'profile_form': profile_form}
    return render(request, 'core/update_user.html', context)

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)

    return render(request, 'core/topics.html', {'topics': topics})


def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'core/activity.html', {'room_messages': room_messages})