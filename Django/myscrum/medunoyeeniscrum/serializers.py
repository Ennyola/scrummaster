from rest_framework import serializers
from .models import *

class ScrumGoalSerializer(serializers.ModelSerializer):
	"""docstring for UserSerializier"""
	class Meta:
		model = ScrumGoal
		fields = ('visible','id','name','status')


class ScrumUserSerializer(serializers.ModelSerializer):
	"""docstring for UserSerializier"""
	scrumgoal_set = ScrumGoalSerializer(many = True)
	class Meta:
		model = ScrumUser
		fields = ('nickname', 'id', 'scrumgoal_set')


