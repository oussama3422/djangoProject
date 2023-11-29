from django.shortcuts import render,redirect
# from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth.models import User 
from base.forms import RoomForm, UserForm
from .models import Room,Topic
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from base.models import Message
# rooms=[
#     {'id':1,'name':"Let's learn Django"},
#     {'id':2,'name':"Let's learn PhP"},
#     {'id':3,'name':"Let's learn Flutter"},
# ]





def login_auth(request):
    page='login'
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method =='POST':
        username=request.POST.get('username').lower()
        password=request.POST.get('password')
        try:
            user=User.objects.get(username=username)
        except:
            messages.error(request,'User does not exists')
            
        user=authenticate(request,username=username,password=password)
        print(user)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'Username or password does not exists')
            
    context={'page':page}
    return render(request,"base/login_register.html",context)

def logout_user(request):
    logout(request)
    return redirect('home')




def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            messages.success(request, 'Registration successful. You are now logged in.')
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
            return redirect('register')
    else:
        form = UserCreationForm()

    context = {'form': form}
    return render(request, 'base/login_register.html', context)


def home(request):
    q=request.GET.get('q') if request.GET.get('q') != None else ''
    # filter by name or description or topic nae
    rooms=Room.objects.filter(Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(desc__icontains=q))
    topics=Topic.objects.all()
    room_count=rooms.count()
    room_messages=Message.objects.filter(Q(room__topic__name__icontains=q))
    context={'rooms':rooms,'topics':topics,'room_count':room_count,'room_messages':room_messages}
    return render(request,'base/home.html',context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        body = request.POST.get('body')
        if body:
            message = Message.objects.create(
                user=request.user,
                room=room,
                body=body
            )
        # Add the user as a participant only if they are not already in the room
        if request.user not in participants:
            room.participants.add(request.user)

        return redirect('room', pk=room.id)

    context = {'room': room, 'room_messages': room_messages, 'participants': participants}
    return render(request, 'base/room.html', context)


def user_profile(request,pk):
    user=User.objects.get(id=pk)
    rooms=user.room_set.all()
    room_messages=user.message_set.all()
    topics=Topic.objects.all()
    context={'user':user,'rooms':rooms,'room_messages':room_messages,'topics':topics}
    return render(request,'base/profile.html',context)




@login_required(login_url='login')

def createRoom(request):
    form=RoomForm()
    topics=Topic.objects.all()
    if request.method == 'POST':
        topic_name=request.POST.get('topic')
        # if not find it in database it will be created
        topic,created=Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(host=request.user,topic=topic,name=request.POST.get('name'),desc=request.POST.get('description'))
        return redirect('home')
    context={'form':form,'topics':topics}
    return render(request,'base/room_form.html',context)    

@login_required(login_url='login')

def updateRoom(request,pk):
    room=Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics=Topic.objects.all()
    if request.user != room.host :
        return HttpResponse('you are not allowed here')
    if request.method == 'POST':
        topic_name=request.POST.get('topic')
        # if not find it in database it will be created
        topic,created=Topic.objects.get_or_create(name=topic_name)
        
        room.name=request.POST.get('name')
        room.topic = topic
        room.desc=request.POST.get('description')
        room.save()
        return redirect('home')
        
    context={'form':form,'topics':topics,'room':room}    
    return render(request,'base/room_form.html',context)



@login_required(login_url='login')

def deleteRoom(request,pk):
    room=Room.objects.get(id=pk)
    if request.user != room.host :
        return HttpResponse('you are not allowed here')
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':room})


@login_required(login_url='login')
def deleteMessage(request,pk):
    message=Message.objects.get(id=pk)
    if request.user != message.user :
        return HttpResponse('you are not allowed here')
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':message})


@login_required(login_url='login')
def update_user(request):
    user = request.user
    form=UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST,instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile',pk=user.id)
    context={'form':form}
    return render(request,'base/update-user.html',context)
