# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


""""
class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'
"""


class LibraryStock(models.Model):
    isbn = models.CharField(max_length=20)
    total = models.PositiveIntegerField()
    remain = models.PositiveIntegerField()
    reserving = models.PositiveIntegerField()
    name = models.CharField(max_length=100)
    author = models.CharField(max_length=50)
    version = models.PositiveIntegerField()
    publisher = models.CharField(max_length=200)
    publish_date = models.DateField(default='2018/5/21')
    price = models.PositiveIntegerField()
    category = models.CharField(max_length=20)
    review_rate = models.DecimalField(max_digits=3, decimal_places=2,)
    review_number = models.PositiveIntegerField()
    introduction = models.TextField(blank=True, null=True)
    modify_date = models.DateTimeField(blank=True, null=True, auto_now=True)

    class Meta:
        managed = False
        db_table = 'library_stock'

    def __str__(self):
        return self.name


class LibraryBook(models.Model):
    add_date = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=20)
    # sub_date = models.DateTimeField(blank=True, null=True, auto_now=True)
    flag = models.PositiveIntegerField()
    # flag: 0--再架上 1--借出
    # （2--被预约，预约数量是（flag-1）个）
    isbn = models.CharField(max_length=20)
    stock = models.ForeignKey('LibraryStock', models.CASCADE)

    class Meta:
        managed = False
        db_table = 'library_book'

    def __str__(self):
        return str(self.id) + ":" + self.isbn[10:]


class LibraryBreak(models.Model):
    reason = models.CharField(max_length=30)
    break_date = models.DateTimeField()
    punishment = models.CharField(max_length=30)
    user = models.ForeignKey(User, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'library_break'


class LibraryEmployee(models.Model):
    empno = models.CharField(max_length=6)
    name = models.CharField(max_length=20)
    sex = models.CharField(max_length=5)
    age = models.PositiveIntegerField()
    certificate = models.CharField(max_length=18)
    work = models.CharField(max_length=10)
    salary = models.IntegerField()
    entery_date = models.DateField()

    class Meta:
        managed = False
        db_table = 'library_employee'

    def __str__(self):
        return self.name + ':' + self.work


class LibraryFine(models.Model):
    fine = models.FloatField()
    pay_date = models.DateTimeField(blank=True, null=True)
    break_id = models.ForeignKey(LibraryBreak, models.CASCADE)
    employee = models.ForeignKey(LibraryEmployee, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'library_fine'


class LibraryLoan(models.Model):
    loan_date = models.DateTimeField(default=timezone.now())
    loan_time = models.PositiveIntegerField(default=30)
    flag = models.IntegerField(default=1)
    # flag 0: 已还记录 1：未还记录； >2：预约记录
    # flag <0 已换且 为违约状态  -1：逾期违约记录； -2：损坏违约记录；
    return_time = models.DateTimeField(blank=True, null=True)
    renew_times = models.PositiveIntegerField(default=0)
    book = models.ForeignKey(LibraryBook, models.DO_NOTHING)
    isbn = models.CharField(max_length=20)
    employee = models.ForeignKey(LibraryEmployee, models.DO_NOTHING)
    user = models.ForeignKey(User, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'library_loan'

    def __str__(self):
        return str(self.flag) + ' : ' + str(self.book)


class LibraryPurchase(models.Model):
    isbn = models.CharField(db_column='ISBN', max_length=20)  # Field name made lowercase.
    name = models.CharField(max_length=100)
    author = models.CharField(max_length=50)
    version = models.PositiveIntegerField()
    publisher = models.CharField(max_length=200)
    publish_date = models.DateField()
    price = models.PositiveIntegerField()
    category = models.CharField(max_length=20)
    amount = models.PositiveIntegerField()
    purchase_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'library_purchase'


class LibraryReader(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    limitation = models.PositiveIntegerField(default=10)

    borrowing_times = models.PositiveIntegerField(default=0)
    breaking_times = models.PositiveIntegerField(default=0)
    fining_times = models.PositiveIntegerField(default=0)
    borrow_number = models.PositiveIntegerField(default=0)
    reserve_number = models.PositiveIntegerField(default=0)
    suggestion_number = models.PositiveIntegerField(default=0)
    rank = models.PositiveIntegerField(default=10)

    class Meta:
        managed = False
        db_table = 'library_reader'

    def __str__(self):
        return str(self.user)


class LibraryReserve(models.Model):
    reserve_date = models.DateTimeField()
    book = models.ForeignKey(LibraryBook, models.DO_NOTHING)
    user = models.ForeignKey(User, models.DO_NOTHING)
    isbn = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'library_reserve'


class LibraryReview(models.Model):
    user = models.ForeignKey(User, models.DO_NOTHING)
    username = models.CharField(max_length=20)
    text = models.TextField()
    rate = models.PositiveIntegerField()
    review_date = models.DateTimeField(default=timezone.now())
    stock = models.ForeignKey(LibraryStock, models.CASCADE)

    class Meta:
        managed = False
        db_table = 'library_review'

    def __str__(self):
        return self.user + " : " + self.review[:50]


class LibrarySuggestion(models.Model):
    isbn = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    publisher = models.CharField(max_length=200)
    author = models.CharField(max_length=50)
    user = models.ForeignKey(User, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'library_suggestion'

    def __str__(self):
        return self.isbn


class LibraryNotification(models.Model):
    user = models.ForeignKey(User, models.DO_NOTHING)
    message = models.TextField()
    type = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)
    flag = models.PositiveIntegerField(default=0)
    index = models.PositiveIntegerField()
    # type=1 ：预约通知：
    # flag: 0：创建  1：已通知  2：已完成  3：预期未完成  4：预约被取消

    class Meta:
        managed = False
        db_table = 'library_notification'

    def __str__(self):
        return self.message[:20]

