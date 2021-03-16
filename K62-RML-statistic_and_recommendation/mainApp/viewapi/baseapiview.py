from rest_framework.decorators import api_view
from rest_framework.response import Response
from mainApp.models import Units, Generations, Majors, Courses, Major_Course, Semesters, StudentGroups, Years
from django.contrib.auth.decorators import login_required

# @api_view(["GET"])
# def list_course(request):
#     result = []
#     for unit in Units.objects.all():
#         unit_info = {
#             'unitID': unit.unitID,
#             'unitName': unit.unitName,
#             'majors': [],
#             'generations': []
#         }
#
#         for major in Majors.objects.filter(unit=unit):
#             courses = [{'courseID': courseID,
#                         'counseCode': counseCode,
#                         'courseName': courseName,
#                         } for courseID, counseCode, courseName in Major_Course.objects.filter(major=major)
#                 .values_list("course_id", "course__courseCode", "course__courseName")
#                        ]
#
#             unit_info['majors'].append({
#                 'majorID': major.majorID,
#                 'majorName': major.majorName,
#                 'courses': courses
#             })
#
#         for gen in Generations.objects.filter(unit=unit):
#             unit_info['generations'].append({
#                 'generationID': gen.generationID,
#                 'generationName': gen.generationName,
#             })
#
#         result.append(unit_info)
#     return Response(result)

@login_required(login_url='/login/')
@api_view(["GET"])
def list_generations(request, unit_id):
    result = [{'generationID': gen.generationID,
               'generationName': gen.generationName,
               } for gen in Generations.objects.filter(unit_id=unit_id)
              ]
    return Response(result)

@login_required(login_url='/login/')
@api_view(["GET"])
def list_majors(request, unit_id):
    result = [{'majorID': major.majorID,
               'majorName': major.majorName,
               } for major in Majors.objects.filter(unit_id=unit_id)
              ]
    return Response(result)

@login_required(login_url='/login/')
@api_view(["GET"])
def list_groups(request, generation_id):
    result = [{'groupID': group.groupID,
               'groupName': group.groupName,
               } for group in StudentGroups.objects.filter(generation_id=generation_id)
              ]
    return Response(result)

@login_required(login_url='/login/')
@api_view(["GET"])
def list_semester(request, generation_id):
    year_id = 1
    try:
        year_id = Generations.objects.get(generation_id=generation_id).beginningYear_id
    except:
        print("generation_id don't exsit")

    result = [{'semesterID': sem.semesterID,
               'semesterName': sem.semesterName,
               } for sem in Semesters.objects.filter(year_id__gte=year_id)
              ]
    return Response(result)

@login_required(login_url='/login/')
@api_view(["GET"])
def list_courses(request, major_id):
    result = [{'courseID': courseID,
               'counseCode': counseCode,
               'courseName': courseName,
               } for courseID, counseCode, courseName in Major_Course.objects.filter(major_id=major_id).values_list("course_id", "course__courseCode", "course__courseName")
              ]
    return Response(result)

@login_required(login_url='/login/')
@api_view(["GET"])
def list_years(request, type_sort='only', year_id=0):
    if type_sort == 'only':
        result = [{'yearID': year.yearID,
                'yearName': year.yearName,
                } for year in Years.objects.filter(yearID=year_id).order_by('yearName')
                ]
        return Response(result)
    elif type_sort == 'asc':
        result = [{'yearID': year.yearID,
                'yearName': year.yearName,
                } for year in Years.objects.all().order_by('yearName')
                ]
        return Response(result)
    elif type_sort == 'desc':
        result = [{'yearID': year.yearID,
                'yearName': year.yearName,
                } for year in Years.objects.all().order_by('-yearName')
                ]
        return Response(result)
        