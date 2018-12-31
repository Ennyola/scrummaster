from django.shortcuts import render
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User,Group
from django.http import HttpResponseRedirect,JsonResponse
from django.urls import reverse
from django.contrib import messages
from .models import *
from rest_framework import viewsets
from .serializers import *
from rest_framework.permissions import IsAuthenticatedOrReadOnly

# Create your views here.

def create_user(request):
	return render(request, "create_user.html")

def init_user(request):
	password = request.POST.get('password', None)
	rtpassword = request.POST.get('rtpassword', None)
	if password != rtpassword:
		messages.error(request, 'Error : Passwords Do not Match')
		return HttpResponseRedirect(reverse('medunoyeeniscrum:create_user'))

	user, created = User.objects.get_or_create(username = request.POST.get('username',None))
	if created:
		user.set_password(password)
		group = Group.objects.get(name = request.POST.get('usertype', None))
		group.user_set.add(user)
		user.save()
		scrum_user = ScrumUser(user = user, nickname = request.POST.get('full_name'), age = request.POST.get('age',None))
		scrum_user.save()
		messages.success(request, 'User Created Successfully.')
		return HttpResponseRedirect(reverse('medunoyeeniscrum:create_user'))
	else:
		messages.error(request, 'Error : Username Already exists')
		return HttpResponseRedirect(reverse('medunoyeeniscrum:create_user'))


def scrum_login(request):
	username = request.POST.get('username', None)
	password = request.POST.get('password', None)
	login_user = authenticate(request, username=username, password=password)
	if login_user is not None:
		login(request, login_user)
		return HttpResponseRedirect(reverse('medunoyeeniscrum:profile'))
	else:
		messages.error(request, 'Error: Invalid Credentials.')
		return HttpResponseRedirect(reverse('login'))

def profile(request):
	if request.user.is_authenticated:
		username = request.user.username
		user_info = request.user.scrumuser
		role = request.user.groups.all()[0].name
		goal_list = ScrumGoal.objects.order_by('user__nickname','-id')
		nums = [x for x in range(4)]
		final_list = []
		item_prev = None

		for item in goal_list:
			if item.user != item_prev:
				item_prev = item.user
				final_list.append((item, goal_list.filter(user = item.user).count()))
			else:
				final_list.append((item, 0))
		context = {'username': username , 'user_info' : user_info,"role":role, 'goal_list':final_list, 'nums_list': nums}
		return render(request, "profile.html", context)
	else:
		messages.error(request, "Please login first.")
		return HttpResponseRedirect(reverse('login'))
def scrum_logout(request):
	logout(request)
	return HttpResponseRedirect(reverse('login'))

def add_goal(request):
	if request.user.is_authenticated:
		name_goal = request.POST.get('name', None)
		group_name = request.user.groups.all()[0].name
		status_start = 0
		if group_name == "Admin":
			status_start = 1
		elif group_name == "Quality Analyst":
			status_start = 2
		goal = ScrumGoal(user=request.user.scrumuser, name = name_goal, status = status_start)
		goal.save()
		messages.success(request,'Goal Added Successfully')
		return HttpResponseRedirect(reverse('medunoyeeniscrum:profile'))
	else:
		messages.error(request, "Please login first.")
		return HttpResponseRedirect(reverse('login'))

def remove_goal(request,goal_id):
	if request.user.is_authenticated:
		if request.user.groups.all()[0].name == 'Developer':
			if request.user != ScrumGoal.objects.get(id = goal_id).user.user:
				messages.error(request, 'Permission Denied: Unauthorized Deletion of Goals')
				return HttpResponseRedirect(reverse('medunoyeeniscrum:profile'))
		del_goal = ScrumGoal.objects.get(id = goal_id)
		del_goal.delete()
		messages.success(request,'Goal Removed Successfully')
		return HttpResponseRedirect(reverse('medunoyeeniscrum:profile'))
	else:
		messages.error(request, "Please login first.")
		return HttpResponseRedirect(reverse('login'))

def move_goal(request,goal_id,to_id):
	if request.user.is_authenticated:
		goal_item = ScrumGoal.objects.get(id = goal_id)
		group = request.user.groups.all()[0].name
		from_allowed = []
		to_allowed = []

		if group == 'Developer':
			if request.user != goal_item.user.user:
				messages.error(request, 'Permission Denied: Unauthorized Movement of Goals')
				return HttpResponseRedirect(reverse('medunoyeeniscrum:profile'))

		if group == 'Owner':
			from_allowed = [0,1,2,3]
			to_allowed = [0,1,2,3]
		elif group == 'Admin':
			from_allowed = [1,2]
			to_allowed = [1,2]
		elif group == 'Developer':
			from_allowed = [0,1,2]
			to_allowed = [0,1,2]
		elif group == 'Quality Analyst':
			from_allowed = [2,3]
			to_allowed = [2,3]

		if (goal_item.status in from_allowed) and (to_id in to_allowed):
			goal_item.status = to_id
		elif group == 'Quality Analyst' and goal_item.status == 2 and to_id == 0:
			goal_item.status = to_id
		else:
			messages.error(request, 'Permission Denied: Unauthorized Movement of Goals')
			return HttpResponseRedirect(reverse('medunoyeeniscrum:profile'))	

		goal_item.save()
		messages.success(request,'Goal Moved Successfully')
		return HttpResponseRedirect(reverse('medunoyeeniscrum:profile'))
	else:
		messages.error(request, "Please login first.")
		return HttpResponseRedirect(reverse('login'))

class ScrumUserViewSet(viewsets.ModelViewSet):
	queryset = ScrumUser.objects.all()
	serializer_class = ScrumUserSerializer

	def create(self, request):
		password = request.data['password']
		rtpassword = request.data['rtpassword']
		if password != rtpassword:
			return JsonResponse({'message': 'Error: Passwords Do not Match'})
		user, created = User.objects.get_or_create(username = request.data['username'])
		if created:
			user.set_password(password)
			group = Group.objects.get(name = request.data['usertype'])
			group.user_set.add(user)
			user.save()
			scrum_user = ScrumUser(user=user, nickname = request.data['full_name'], age = request.data['age'])
			scrum_user.save()
			return JsonResponse({'message': 'User Created Successfully.'})
		else:
			return JsonResponse({'message': 'Error: Username Already Exists.'})


def  filtered_users():
	users = ScrumUserSerializer(ScrumUser.objects.all(), many=True).data

	for user in users:
		user['scrumgoal_set'] = [x for x in user['scrumgoal_set'] if x['visible']==True]
	return users

class ScrumGoalViewSet(viewsets.ModelViewSet):
	queryset = ScrumGoal.objects.all()
	serializer_class = ScrumGoalSerializer
	permission_classes = [IsAuthenticatedOrReadOnly]




	def create(self,request):
		name_goal = request.data['name']
		group_name = request.user.groups.all()[0].name
		status_start = 0
		if group_name == "Admin":
			status_start = 1
		elif group_name == "Quality Analyst":
			status_start = 2
		goal = ScrumGoal(user=request.user.scrumuser, name = name_goal, status = status_start)
		goal.save()
		return JsonResponse({'message': 'Goal Added!', 'data' : filtered_users()})
		
	def patch(self,request):
		goal_id = request.data['goal_id']
		to_id = request.data['to_id']

		if to_id == 4:
			if request.user.groups.all()[0].name == 'Developer':
				if request.user != ScrumGoal.objects.get(id = goal_id).user.user:
					return JsonResponse({'message': 'Permission Denied : Unauthorized Deletion of Goals', 'data' : filtered_users()})
			del_goal = ScrumGoal.objects.get(id = goal_id)
			del_goal.visible = False
			del_goal.save()
			return JsonResponse({'message': 'Goal Removed Successfully!', 'data' : filtered_users()})
		else:
			goal_item = ScrumGoal.objects.get(id = goal_id)
			group = request.user.groups.all()[0].name
			from_allowed = []
			to_allowed = []

			if group == 'Developer':
				if request.user != goal_item.user.user:
					return JsonResponse({'message': 'Permission Denied : Unauthorized Deletion of Goals', 'data' : filtered_users()})
			if group == 'Owner':
				from_allowed = [0,1,2,3]
				to_allowed = [0,1,2,3]
			elif group == 'Admin':
				from_allowed = [1,2]
				to_allowed = [1,2]
			elif group == 'Developer':
				from_allowed = [0,1,2]
				to_allowed = [0,1,2]
			elif group == 'Quality Analyst':
				from_allowed = [2,3]
				to_allowed = [2,3]

			if (goal_item.status in from_allowed) and (to_id in to_allowed):
				goal_item.status = to_id
			elif group == 'Quality Analyst' and goal_item.status == 2 and to_id == 0:
				goal_item.status = to_id
			else:
				return JsonResponse({'message': 'Permission Denied : Unauthorized Movement of Goals', 'data' : filtered_users()})
			goal_item.save()
			return JsonResponse({'message': 'Goal Moved Successfully!', 'data' : filtered_users()})

		
	def put(self,request):
		if request.data['mode'] == 0:
			from_id = request.data['from_id']
			to_id = request.data['to_id']

			if request.user.groups.all()[0].name == 'Developer' or request.user.groups.all()[0].name == 'Quality Analyst':
				return JsonResponse({'message': 'Permission Denied : Unauthorized Reassignment of Goals', 'data' : filtered_users()})

			goal = ScrumGoal.objects.get(id = from_id)

			author = None
			if to_id[0] == 'u':
				author = ScrumUser.objects.get(id=to_id[1:])
			else:
				author = ScrumGoal.objects.get(id = to_id).user
			goal.user = author
			goal.save()
			return JsonResponse({'message': 'Goal Reassigned Successfully!', 'data' : filtered_users()})
		else:
			goal = ScrumGoal.objects.get(id = request.data['goal_id'])
			if request.user.groups.all()[0].name != 'Owner' and request.user != goal.user.user:
				return JsonResponse({'message': 'Permission Denied : Unauthorized Name Change of Goal', 'data' : filtered_users()})	
			
			goal.name = request.data['new_name']
			goal.save()
			return JsonResponse({'message': 'Goal Name Changed!', 'data' : filtered_users()})


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'role': user.groups.all()[0].name


       }