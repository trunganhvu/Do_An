from mainApp.middlewares import checkInUrl
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from mainApp.models import Profiles, Generations, Courses, Majors

@login_required(login_url='/login/')
def scoreforecast_page(request):
    if checkInUrl(request, 'scoreforecast') is False:
        listFunction = request.user.list_function()
        return HttpResponseRedirect(reverse(listFunction[0]))
    if request.method == 'GET':
        unitRole = request.user.unit_role
        profiles = []
        isStudent = False
        generations = None
        majors = None
        if unitRole == 0:
            profiles = Profiles.objects.all().values('profileID', 'firstName', 'lastName', 'MSSV')
            generations = Generations.objects.order_by('unit').all()
            courses = Courses.objects.order_by('unit').all()
            majors = Majors.objects.order_by('unit').all
        elif unitRole is None:
            profiles = Profiles.objects.filter(user_id=request.user.id)#.values('profileID', 'firstName', 'lastName', 'MSSV')
            isStudent = True
            unitId = 0
            for pro in profiles:
                unitId = pro.major.unit.unitID
            courses = Courses.objects.filter(unit=unitId).order_by('courseCode').all()
        else:
            profiles = Profiles.objects.filter(major__unit_id=unitRole).values('profileID', 'firstName', 'lastName', 'MSSV')
            generations = Generations.objects.filter(unit=unitRole).all()
            courses = Courses.objects.filter(unit=unitRole).order_by('courseCode').all()
            majors = Majors.objects.filter(unit=unitRole).order_by('unit').all
        context = {
            'profiles': profiles,
            'isStudent': isStudent,
            'generations': generations,
            'courses': courses,
            'majors': majors,
        }
        
    return TemplateResponse(request, 'adminuet/scoreforecast.html', context=context)