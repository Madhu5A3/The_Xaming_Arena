# Create your views here.

import random
import math

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q
from django.utils.http import base36_to_int
from django.utils.encoding import smart_str

from The_Xaming_Arena.exam.models import Subject, Question, Answer,ExamIdClass,SubmittedAnswers, Exam,CorrectAnswers
from The_Xaming_Arena.exam.forms import AnswerForm,BaseAnswerFormSet

from django.forms.formsets import formset_factory

from The_Xaming_Arena import settings

@csrf_protect
@login_required
def home(request, template_name = 'accounts/home.html'):
        """ This renders the home page"""
	content = {}
	return render_to_response(template_name,{'content':content})

@login_required
def topics(request, template_name = 'accounts/topics.html'):
        """ This function lists all the subjects that are present in the database"""
	topics = Subject.objects.all()
	return render_to_response(template_name, {"topics":topics})

@login_required
def select_topic(request, template_name = 'accounts/select_topic.html'):
        """ This function renders a page which also displays all the subjects"""
	topics = Subject.objects.all()
	return render_to_response(template_name, {"topics":topics})

@login_required
def sub_rep(request,template_name='accounts/sub_res.html'):
	topics = Subject.objects.all()
	return render_to_response(template_name,{"topics":topics})

@login_required
def reports(request, sub_code,template_name = 'accounts/reports.html'):
        """ This returns a page which contains all the previous results of a purticular user"""
	reports = Exam.objects.filter(user=request.user)
	reports = reports.filter(subject=sub_code)
	return render_to_response(template_name, {"reports":reports})

@login_required
def view_questions(request, sub_code, template_name = 'accounts/view_questions.html'):
        """ This returns a page which contains all the questions in the database to the subject selected"""
	questions = Question.objects.filter(subject_code=sub_code)
	return render_to_response(template_name, RequestContext(request,{"questions":questions}))

@login_required
def profile(request, template_name='accounts/profile.html'):
        """ This function returns a page which contains the profile of the student"""
	return render_to_response(template_name)
	
@csrf_protect
@login_required
def start_exam(request, sub_code, template_name = 'accounts/start_exam.html',answer_form=formset_factory(AnswerForm, formset=BaseAnswerFormSet, extra=10) ,current_app=None, extra_context=None,after_exam = 'accounts/exam_complete.html'):

	if request.method == "POST":
		answer_formset = answer_form(request.POST)
		if answer_formset.is_valid():
			so = answer_formset.clean()
		
		exam_id = request.POST['exam_id']

		if not Exam.objects.filter(exam_id=exam_id).count()==0:
			return render_to_response(template_name)
			
		e= ExamIdClass.objects.get(id=exam_id)
		id_list = [e.one,e.two,e.three,e.four,e.five,e.six,e.seven,e.eight,e.nine,e.ten]

		ans_list = []
		for i in range(10):
			a = Answer.objects.get(id=id_list[i])
			ans_list.append(a.answer)
		score =0
		for i in range(10):
			if ans_list[i]==so[i]:
				score +=1
		sa=SubmittedAnswers(id_exam=exam_id,one=so[0],two=so[1],three =so[2],four=so[3],five=so[4],six=so[5],seven=so[6],eight=so[7],nine =so[8], ten=so[9])

		sa.save()

		ca=CorrectAnswers(id_exam=exam_id,one=ans_list[0],two=ans_list[1],three =ans_list[2],four=ans_list[3],five=ans_list[4],six=ans_list[5], seven=ans_list[6],eight=ans_list[7],nine =ans_list[8], ten=ans_list[9])

		ca.save()

		eu = Exam(exam_id=exam_id, user = request.user, subject=sub_code, marks_obtained=score)

		eu.save()
		questions = Question.objects.filter(id__in = id_list)

		context = {'ca':ca,'sa':sa,'result':score,'questions':questions}

		return render_to_response(template_name,context) 
	else:
		questions = Question.objects.filter(subject_code = sub_code)
		n = questions.count()
		if (n < 10):
			return render_to_response(template_name)
		m = int(math.floor(n/10))
		position = 0
		temp_list=[]
		id_list = []
		for object in Question.objects.filter(subject_code = sub_code):
			temp_list.append(object.id)
		for i in range(10):
			id_list.append(temp_list[int(position+math.floor(random.random()*m))])
			position +=m
		questions = Question.objects.filter(id__in = id_list)
		id_table = ExamIdClass(one=id_list[0],two=id_list[1],three=id_list[2],four=id_list[3],five = id_list[4],six=id_list[5],seven=id_list[6], 									eight=id_list[7],nine=id_list[8], ten =id_list[9])

		id_table.save()
		id_table = ExamIdClass.objects.all()
		exam_id = id_table.count()
	    	context = {'formset': answer_form(initial={}), 'questions':questions,'exam_id':exam_id}
	    	context.update(extra_context or {})
    		return render_to_response(template_name, context, context_instance=RequestContext(request, current_app=current_app))


