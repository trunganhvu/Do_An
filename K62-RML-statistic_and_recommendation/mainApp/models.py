from django.db import models
import psycopg2
from psycopg2 import extras
from uuid import uuid4
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager

TRAIN_DATA_STORAGE = FileSystemStorage(location=settings.TRAIN_DATA_ROOT)
DUMPED_MODEL_STORAGE = FileSystemStorage(location=settings.DUMPED_MODEL_ROOT)


def get_current_semester():
    today = timezone.now().date()

    semesters = Semesters.objects.filter(beginDay__lte=today).order_by('-beginDay')

    if len(semesters) <= 0:
        semesters = Semesters.objects.filter(endDay__gte=today).order_by('endDay')

    if len(semesters) <= 0:
        current_semester = Semesters.objects.last()
    else:
        current_semester = semesters[0]

    return current_semester


def execute_values(conn, df, table):
    """
    Using psycopg2.extras.execute_values() to insert the dataframe
    """
    # Create a list of tupples from the dataframe values
    tuples = [tuple(x) for x in df.to_numpy()]
    # Comma-separated dataframe columns
    cols = '"' + '","'.join(list(df.columns)) + '"'
    # SQL quert to execute
    query = 'INSERT INTO public."%s"(%s) VALUES %%s' % (table, cols)
    cursor = conn.cursor()
    try:
        extras.execute_values(cursor, query, tuples)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    print("execute_values() done")
    cursor.close()


def model_field_exists(model, field):
    try:
        model._meta.get_field(field)
        return True
    except Exception as e:
        # print(e)
        return False


def create_from_DF(df, model: models.Model, searching_cols: list):
    # for col in df.columns:
    #     if ~model_field_exists(model, col):
    #         print("col: {}".format(col))
    #         df.drop(col, axis=1, inplace=True)
    #         print(df)
    # data for searching the data row
    search = dict.fromkeys(searching_cols)
    # other data use when create
    defaults = dict.fromkeys(list(set(df.columns) - set(searching_cols)))
    # Create a list of tupples from the dataframe values
    object_list = []
    for i, row in df.iterrows():
        for k in search.keys():
            search[k] = row[k]

        for k in defaults.keys():
            defaults[k] = row[k]
        obj, created = model.objects.get_or_create(**search, defaults=defaults)
        object_list.append(obj)
    return object_list


def update_from_DF(df, model: models.Model, searching_cols: list):
    # for col in df.columns:
    #     if ~model_field_exists(model, col):
    #         print("{} is not one of {} field".format(col, model.__name__))
    #         return 1
    # data for searching the data row
    search = dict.fromkeys(searching_cols)
    # other data use when create
    defaults = dict.fromkeys(list(set(df.columns) - set(searching_cols)))

    # Create a list of tupples from the dataframe values
    object_list = []
    for v in df.iterrows():
        for k in search.keys():
            search[k] = v[k]

        for k in defaults.keys():
            defaults[k] = v[k]
        obj, created = model.objects.update_or_create(**search, defaults=defaults)
        object_list.append(obj)
    return object_list


def semester_rank(current_semester_id=None, profile_id: int = None, group_id: int = None, generation_id: int = None,
                  year_id: int = None, semester_id: int = None):
    try:
        if current_semester_id is None:
            current_semester = get_current_semester()
        else:
            current_semester = Semesters.objects.get(pk=current_semester_id)

        if profile_id is not None and profile_id > 0:
            group_id = Profiles.objects.get(pk=profile_id).group_id

        if group_id is not None and group_id > 0:
            generation_id = StudentGroups.objects.get(pk=group_id).generation_id

        if generation_id is not None and generation_id > 0:
            year_id = Generations.objects.get(pk=generation_id).beginningYear_id

        if year_id is not None and year_id > 0:
            semester = Semesters.objects.filter(year_id=year_id).first()
        else:
            semester = Semesters.objects.get(pk=semester_id)

        if current_semester.pk == semester.pk:
            return 0

        sem_begin = semester.beginDay
        cur_sem_begin = current_semester.beginDay

        semester_rank = len(Semesters.objects.filter(endDay__gt=sem_begin, endDay__lt=cur_sem_begin))
        if semester_rank <= 0:
            semester_rank = -len(Semesters.objects.filter(endDay__gt=cur_sem_begin, endDay__lt=sem_begin))

        return semester_rank

    except Exception as e:
        print(e)
        return None


def transcript_path_and_rename(instance: models.Model, filename: str):
    folder_name = 'transcript/'
    filename = filename.replace('/', '_').replace('\\', '_')
    # get filename
    if instance.pk:
        filename = '{}_{}'.format(instance.pk, filename)
    else:
        # set filename as random string
        filename = '{}_{}'.format(uuid4().hex, filename)
    # return the whole path to the file
    return folder_name + filename


class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


class Years(models.Model):
    yearID = models.AutoField(primary_key=True)
    yearName = models.CharField(max_length=50)
    openingDay = models.DateField(null=False)
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.yearName

    def save(self, *args, **kwargs):
        other_years = Years.objects.filter(openingDay__year=self.openingDay.year)
        if len(other_years) > 1 or (len(other_years) == 1 and other_years[0].pk != self.pk):
            raise Exception("This year already have opening day")

        super(Years, self).save(*args, **kwargs)


class Semesters(models.Model):
    semesterID = models.AutoField(primary_key=True)
    semesterName = models.CharField(max_length=50)
    year = models.ForeignKey(Years, on_delete=models.CASCADE)
    beginDay = models.DateField(null=False)
    endDay = models.DateField(null=False)

    def __str__(self):
        return self.semesterName


class Units(models.Model):
    unitID = models.AutoField(primary_key=True)
    unitName = models.CharField(max_length=100) #unique=True
    unitDescription = models.CharField(max_length=500, default="", null=True)

    def __str__(self):
        return self.unitName


class Generations(models.Model):
    generationID = models.AutoField(primary_key=True)
    generationName = models.CharField(max_length=10)
    beginningYear = models.ForeignKey(Years, on_delete=models.CASCADE)
    unit = models.ForeignKey(Units, on_delete=models.CASCADE)

    def __str__(self):
        return self.generationName + ' - ' + self.unit.unitName


class StudentGroups(models.Model):
    groupID = models.AutoField(primary_key=True)
    groupName = models.CharField(max_length=25)
    generation = models.ForeignKey(Generations, on_delete=models.CASCADE)

    def __str__(self):
        return self.groupName + ' - ' + self.generation.unit


class Majors(models.Model):
    majorID = models.AutoField(primary_key=True)
    majorName = models.CharField(max_length=100)
    majorDescription = models.CharField(max_length=255, default="", null=True)
    unit = models.ForeignKey(Units, on_delete=models.CASCADE)

    def __str__(self):
        return self.majorName


class Courses(models.Model):
    courseID = models.AutoField(primary_key=True)
    unit = models.ForeignKey(Units, on_delete=models.CASCADE)
    courseCode = models.CharField(max_length=20, unique=True)
    courseName = models.CharField(max_length=100)
    credit = models.IntegerField(default=0)

    def __str__(self):
        return self.courseCode + ' - ' + self.courseName


class Major_Course(models.Model):
    """
    M???t mn?? h???c (course) trong m???i chuy??n ng??nh (major) c?? th??? ???????c ????? xu???t h???c trong nhi???u k??? kh??c nhau (semesterRecommended)
    """
    ID = models.AutoField(primary_key=True)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    major = models.ForeignKey(Majors, on_delete=models.CASCADE)
    semesterRecommended = models.IntegerField(default=0)


class Functions(models.Model):
    """
    Danh s??ch c??c ch???c n??ng h??? th???ng ????? d??ng trong vi???c ph??n quy???n
    """
    functionID = models.AutoField(primary_key=True)
    functionName = models.CharField(max_length=50)

    def __str__(self):
        return self.functionName


class Roles(models.Model):
    """
    Danh s??ch c??c vai tr?? trong h??? th???ng ????? ph??n quy???n theo vai tr??
    """
    roleID = models.AutoField(primary_key=True)
    roleName = models.CharField(max_length=50)
    roleDescription = models.CharField(max_length=255, default="", null=True)

    def __str__(self):
        return self.roleName


class Role_Function(models.Model):
    """
    Danh s??ch c??c ch???c n??ng ???????c ph??n cho c??c vai tr?? kh??c nhau
    """
    ID = models.AutoField(primary_key=True)
    role = models.ForeignKey(Roles, on_delete=models.CASCADE)
    function = models.ForeignKey(Functions, on_delete=models.CASCADE)
    # role = models.IntegerField(blank=False)
    # function = models.IntegerField(blank=False)


class CustomUser(AbstractUser):
    # id | password | last_login | username | date_joined | role_id
    is_superuser = None
    first_name = None
    last_name = None
    email = None
    is_staff = None
    # is_active = None
    groups = None
    user_permissions = None

    role = models.ForeignKey(Roles, null=True, on_delete=models.SET_NULL)
    unit_role = models.IntegerField(default=None, null=True)

    objects = CustomUserManager()

    dictFunctionName = {
        "Th???ng k?? GPA sinh vi??n": "statistical-gpa-student",
        "Th???ng k?? GPA kh??a": "statistical-gpa",
        "Th???ng k?? ??i???m trung b??nh": "course-avg",
        "Th???ng k?? ph??? ??i???m m??n h???c": "statistical",
        "G???i ?? m??n h???c": "suggestioncourse",
        "D??? b??o k???t qu??? h???c t???p": "scoreforecast",
        "Qu???n l?? vai tr??": "role",
        "Qu???n l?? ch???c n??ng": "function",
        "Qu???n l?? l???p": "group",
        "Qu???n l?? khung ????o t???o": "trainingframework",
        "Qu???n l?? m??n h???c": "course",
        "Qu???n l?? kh??a": "generation",
        "Qu???n l?? k??? h???c": "semester",
        "Qu???n l?? n??m h???c": "year",
        "Qu???n l?? tr?????ng": "unit",
        "Qu???n l?? ng??nh": "major",
        "Qu???n tr??? logs": "logs",
        "Ch???n m?? h??nh": "configmodel",
        "Qu???n tr??? k???t qu??? h???c t???p": "learningoutcome",
        "Qu???n tr??? ng?????i d??ng": "user",
        "T??nh to??n th???ng k?? GPA": "calculategpa",
        "Xem k???t qu??? h???c t???p": "viewlearningoutcome"
    }

    def list_function(self):
        if self.pk is None:
            return []

        functions = set(CustomUser_Function.objects.filter(user=self).values_list("function__functionName", flat=True))
        if self.role_id is not None:
            functions.update(Role_Function.objects.filter(role=self.role_id).values_list("function__functionName", flat=True))

        function_list = [self.dictFunctionName[funct] for funct in functions]
        return function_list

    def __str__(self):
        return self.username


class CustomUser_Function(models.Model):
    """
    Danh s??ch l??u user c?? th??m nh???ng function kh??c ngo??i Role ???? c?? c???a User
    """
    ID = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    function = models.ForeignKey(Functions, on_delete=models.CASCADE)


class Profiles(models.Model):
    profileID = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    firstName = models.CharField(max_length=30)
    lastName = models.CharField(max_length=100, null=True)
    email = models.CharField(max_length=254, null=True)
    MSSV = models.CharField(max_length=10, null=True)
    gender = models.CharField(max_length=10, choices=[
        ('Nam', 'Nam'),
        ('N???', 'N???'),
    ], default='Nam')
    birthday = models.DateField()
    group = models.ForeignKey(StudentGroups, on_delete=models.CASCADE, null=True)
    major = models.ForeignKey(Majors, on_delete=models.DO_NOTHING, null=True)

    def __str__(self):
        return self.MSSV


class TranscriptFiles(models.Model):
    """
    l?? b???ng l??u ???????ng d???n t???i file b???ng ??i???m c??c k??? c???a t???ng l???p
    """
    fileID = models.AutoField(primary_key=True)
    group = models.ForeignKey(StudentGroups, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semesters, on_delete=models.CASCADE)
    major = models.ForeignKey(Majors, on_delete=models.SET_NULL, null=True)
    transcript = models.FileField(upload_to=transcript_path_and_rename)
    extracted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.transcript.name.split('/')[-1])


class Transcript(models.Model):
    """
    L??u l???ch s??? b???ng ??i???m c???a ng?????i d??ng v???i id use, stt b???ng ??i???m v?? c??c ??i???m (student ??nh x??? t???i profileID).
    """
    transcriptID = models.AutoField(primary_key=True)
    student = models.ForeignKey(Profiles, on_delete=models.CASCADE)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semesters, on_delete=models.CASCADE)
    grade = models.FloatField()

    def __str__(self):
        return self.grade


class TrainData(models.Model):
    trainDataID = models.AutoField(primary_key=True)
    dataPath = models.FileField(storage=TRAIN_DATA_STORAGE)
    major = models.ForeignKey(Majors, on_delete=models.DO_NOTHING, null=True)
    updateTime = models.DateTimeField('date_published', auto_now=True)

    def __str__(self):
        return str(self.major_id) + ": " + self.dataPath.name


class PredictHistory(models.Model):
    PredictHistoryID = models.AutoField(primary_key=True)
    student = models.ForeignKey(Profiles, on_delete=models.DO_NOTHING)
    course = models.ForeignKey(Courses, on_delete=models.DO_NOTHING)
    grade = models.FloatField()
    semester = models.ForeignKey(Semesters, on_delete=models.DO_NOTHING)
    predictTime = models.DateTimeField(auto_now_add=True)


class GradePredicted(models.Model):
    """
    L??u l???ch s??? d??? ??o??n ??i???m v???i id b???ng ??i???m ng?????i d??ng n???u th???i ??i???m trong l???n d??? ??o??n cu???i s???m h??n scoreUpdateTime
    th?? s??? th???c hi???n d??? ??o??n l???i.
    """
    predictID = models.AutoField(primary_key=True)
    student = models.ForeignKey(Profiles, on_delete=models.CASCADE)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    grade = models.FloatField()
    predictTime = models.DateTimeField(auto_now_add=True)


class GPA(models.Model):
    """
    L??u ??i???m gpa c???a sinh vi??n
    """
    gpaID = models.AutoField(primary_key=True)
    student = models.ForeignKey(Profiles, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semesters, on_delete=models.DO_NOTHING)
    semesterRank = models.IntegerField(null=True)
    semesterGpa = models.FloatField()
    currentGpa = models.FloatField()


class DumpModel(models.Model):
    dumpModelID = models.AutoField(primary_key=True)
    dumpFile = models.FileField(unique=True, storage=DUMPED_MODEL_STORAGE)
    modelName = models.CharField(max_length=254, null=True)
    param = models.CharField(max_length=1000, null=True)
    updateTime = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=False)
    args = models.CharField(max_length=254, null=True)

    def __str__(self):
        return self.modelName


class Logs(models.Model):
    """
    Ghi nh???t k?? s??? d???ng log t???t c??? c??c t??i kho???n t????ng t??c v???i h??? th???ng
    """
    logID = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    # user = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    action = models.CharField(max_length=50)
    content = models.CharField(max_length=100)
    time = models.DateTimeField(auto_now_add=True)
