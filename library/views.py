from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger


# Create your views here.


def index(request):
    return render(request, 'library/index.html')


def books(request):
    if request.method != 'POST':
        re_book = LibraryStock.objects.all()
    else:
        re_book = LibraryStock.objects.filter(name__contains=request.POST.get("name"))

    paginator = Paginator(re_book, 4)
    page = request.GET.get('page')
    try:
        books = paginator.page(page)  # 获取前端请求的页数
    except PageNotAnInteger:
        books = paginator.page(1)  # 如果前端输入的不是数字,就返回第一页
    except EmptyPage:
        books = paginator.page(paginator.num_pages)
    context = {'books': books, 'msg': "So Cool!" }

    return render(request, 'library/books.html', context)


def book_info(request, stock_id):
    try:
        book_stock = LibraryStock.objects.get(id=stock_id)
    except LibraryStock.DoesNotExist:
        book_stock = None

    reviews = book_stock.libraryreview_set.all()

    context = {'stock_id': stock_id, 'stock': book_stock, 'reviews': reviews}
    return render(request, 'library/book_info.html', context)


@login_required
def borrow_guidance(request, stock_id):
    user = request.user
    reader = LibraryReader.objects.get(user_id=user.id)

    book_stock = LibraryStock.objects.get(id=stock_id)
    # 检查是否为重复借阅/已经预约
    user_book = LibraryLoan.objects.filter(user_id=user.id)
    borrowing_book = user_book.filter(flag__gt=0)
    if borrowing_book.exists():
        this_books = borrowing_book.filter(isbn=book_stock.isbn)
        if this_books.exists():
            this_book = this_books.first()
        else:
            this_book = None
    else:
        this_book = None

    if this_book is not None:
        if this_book.flag == 1:
            msg = "这本书你已经借走啦，续约请到个人信息界面完成续约"
            return HttpResponseRedirect(reverse('library:errormsg', args=[msg]))
        else:
            res_book = LibraryLoan.objects.filter(user_id=user.id).filter(isbn=book_stock.isbn).filter(flag=2)
            if res_book.exists():
                rb = res_book[0]
                book_id = rb.book
                return HttpResponseRedirect(reverse('library:reserve_handle', args=[book_id, 1]))
            else:
                return HttpResponseRedirect(reverse('library:books'))

    if reader.borrowing_times > reader.limitation:
        errmeg = '抱歉，您所接书籍数目超过限制，请归还不用的书后再继续借阅其他数目'
        return HttpResponseRedirect(reverse('library:errormsg', args=[errmeg]))

    try:
        book_stock = LibraryStock.objects.get(id=stock_id)
    except LibraryStock.DoesNotExist:
        book_stock = None

    context = {'stock_id': stock_id, 'stock': book_stock, }
    return render(request, 'library/borrow_guidance.html', context)


@login_required
def borrow_book(request, stock_id):
    # find the book and dec remain
    global loan_time
    if request.method != 'POST':
        pass
    else:
        loan_time = request.POST.get('days')
    print(request.user)
    book_stock = LibraryStock.objects.get(id=stock_id)
    if book_stock is None:
        msg = '没有找到这本书，请确认书籍信息或联系管理员处理该问题。'
        return HttpResponseRedirect(reverse('library:errormsg', args=[msg]))

    if book_stock.remain <= 0:
        errmsg = "这本书太火了，都被借走了，试着预约一下？"
        HttpResponseRedirect(reverse('library:errormsg', args=[errmsg]))

    books2loan = book_stock.librarybook_set.all().filter(flag=0)
    if books2loan.exists():
        # 更新Stock
        book_stock.remain -= 1

        # update Book
        logbook = books2loan[0]
        logbook.flag = 1

        # log loaning info
        emp = LibraryEmployee.objects.filter(work='loan')[0]
        user = request.user

        loan_log = LibraryLoan.objects.create(loan_time=loan_time, book=logbook, isbn=book_stock.isbn, employee=emp,
                                              user_id=user.id)

        # save all updating
        book_stock.save()
        logbook.save()
        loan_log.save()

    else:
        errmsg = "程序BUG:Stock 和 Book 不同步 on remain"
        HttpResponseRedirect(reverse('library:errormsg', args=[errmsg]))

    msg = '借书成功'
    return HttpResponseRedirect(reverse('library:message', args=[msg]))


@login_required
def renew_confirmation(request, book_id):
    ren_book = LibraryBook.objects.get(id=book_id)
    renew_stock = LibraryStock.objects.get(id=ren_book.stock_id)

    context = {'name': renew_stock.name, 'isbn': renew_stock.isbn, 'author': renew_stock.author, 'book_id': book_id}
    return render(request, 'library/renew_confirmation.html', context)


@login_required
def renew_book(request, book_id):
    user = request.user
    reader = LibraryReader.objects.get(user_id=user.id)
    book_loan = LibraryLoan.objects.filter(user_id=user.id).filter(flag=1).get(book=book_id)
    if book_loan is None:
        errmsg = '您还没有接过这本书，请先借阅再说。'
        return HttpResponseRedirect(reverse('library:errormsg', args=[errmsg]))

    if request.method == 'POST':
        renew_time = int(request.POST.get('days'))
    else:
        renew_time = 30

    # 检查续约权限：
    # 若有人在预约，则不允许续约
    # stock_id = LibraryBook.objects.get(id=book_id).stock_id
    # book_stock = LibraryStock.objects.get(id=stock_id)
    reserving_log = LibraryLoan.objects.filter(book=book_id).filter(flag=2)
    if reserving_log.exists():
        msg = '抱歉，有' + str(reserving_log.count()) + '个用户正在预约这本书，请把机会让给其他人\n 但是您还可以选择预约，等待下一本书归还'
        return HttpResponseRedirect(reverse('library:message', args=[msg]))
    # 若续约大于等于2次，则不允许续约
    if book_loan.renew_times >= 2:
        msg = '您已经对这本书续约两次了，请三天后再重新借阅'
        return HttpResponseRedirect(reverse('library:message', args=[msg]))
    if reader.fining_times > 3:
        msg = '抱歉，您的违约记录太多，不允许续约'
        return HttpResponseRedirect(reverse('library:message', args=[msg]))

    book_loan.renew_times += 1
    time_slag = (timezone.now() - book_loan.loan_date).days
    if book_loan.loan_time < renew_time + time_slag:
        book_loan.loan_time = renew_time + time_slag

    book_loan.save()

    return HttpResponseRedirect(reverse('users:records', args=[user.id]))


@login_required()
def return_book(request, book_id):
    borrow_logs = LibraryLoan.objects.filter(user_id=request.user.id).filter(flag=1)
    borrow_log = borrow_logs.get(book=book_id)

    # 修改 loan 表
    if borrow_log is None:
        msg = '没结果这本书，请先借阅'
        return HttpResponseRedirect(reverse('library:errormsg', args=[msg]))

    time_now = timezone.now()
    time_lag = time_now - borrow_log.loan_date
    print(time_lag)
    print(time_lag.days)
    if time_lag.days > borrow_log.loan_time:
        borrow_log.flag = -1
        # 违约记录一下
        break_log = LibraryBreak.objects.create(reson='逾期未还', break_date=time_now,
                                                punishment='上小本本', user_id=request.user.id)
        if LibraryReader.objects.get(user_id=request.user.id).breaking_times > 3:
            fine_money = (LibraryReader.breaking_times - 3) * 10
            break_log.punishment = '罚款' + str(fine_money)
            fine_log = LibraryFine.objects.create(fine=fine_money, break_id=break_log.id)
            fine_log.save()
        LibraryReader.objects.get(user_id=request.user.id).breaking_times += 1
        break_log.save()
    else:
        borrow_log.flag = 0
    borrow_log.return_time = time_now

    # update Book table
    r_book = LibraryBook.objects.get(id=book_id)
    r_book.flag = 0
    # update Stock table
    r_stock = LibraryStock.objects.get(id=r_book.stock_id)
    if r_stock.reserving > 0:
        # 通知第一个预约的人可以去借预约的书了，存储预约通知表，在表里记录
        # 在loan表里寻找最早预约了这本书的人
        reserving_logs = LibraryLoan.objects.filter(flag=2).filter(book=book_id).order_by('loan_date')
        if reserving_logs.exists():
            reserving_log = reserving_logs[0]
            reserving_user = User.objects.get(id=reserving_log.user_id)
            notify_message = reserving_user.username + 'Hello!' + 'Your reserving book' + r_stock.name + '(with isbn:' + \
                             r_stock.isbn + ')can be borrowed now, please go to your personal page to get it!'
            # 通知Ta来取书
            notify_log = LibraryNotification.objects.create(user_id=reserving_log.user_id, message=notify_message,
                                                            flag=0,
                                                            index=reserving_log.id, type=1)
            notify_log.save()
    else:
        r_stock.remain += 1

    borrow_log.save()
    r_book.save()
    r_stock.save()

    return HttpResponseRedirect(reverse('users:records', args=[request.user.id]))


@login_required
def reserve_confirmation(request, stock_id):
    book_stock = LibraryStock.objects.get(id=stock_id)
    if book_stock is None:
        return Http404
    user = request.user
    user_loan = LibraryLoan.objects.filter(user_id=user.id).filter(flag__gt=0)
    print(user.id)
    user_this_loan = user_loan.filter(isbn=book_stock.isbn)
    print(user_this_loan)
    # 查看预约是否合法：
    # 已经借了或已经预约了
    if user_this_loan.exists():
        errmsg = '您已经借过这本书或者正在预约，请前往个人信息界面查询处理'
        return HttpResponseRedirect(reverse('library:errormsg', args=[errmsg]))

    # 查询Stock表 看是否有余量
    # 有余量：请直接借阅
    if book_stock.remain > 0:
        msg = '此书目前还有余量，请直接前往借阅！'
        return HttpResponseRedirect(reverse('library:message', args=[msg]))
    # 无余量：开始预约
    # 查询Loan 表，导出预约表，选出预约此书的记录，返回给用户参考
    book_loans = LibraryLoan.objects.filter(isbn=book_stock.isbn).filter(flag=2).order_by('loan_date') \
        .values('user', 'loan_date')
    book_ = LibraryLoan.objects.filter(isbn=book_stock.isbn).filter(flag__gt=0).order_by('-flag', 'loan_date')
    if book_.exists():
        book_id = book_[0].book_id
    else:
        book_id = 1
    context = {'reserving_logs': book_loans, 'stock': book_stock, 'book_id': book_id}

    return render(request, 'library/reserve_confirmation.html', context)


@login_required
def reserve_book(request, book_id):
    stock_book = LibraryBook.objects.get(id=book_id)
    stock_id = stock_book.stock_id
    stock = LibraryStock.objects.get(id=stock_id)
    # Loan创建新的预约记录；
    new_loan = LibraryLoan.objects.create(flag=2, isbn=stock.isbn, employee_id=1, book_id=book_id,
                                          user_id=request.user.id)
    # 更改Stock表，增加预约记录
    stock.reserving += 1
    stock_book.flag += 1

    new_loan.save()
    stock.save()
    stock_book.save()

    return HttpResponseRedirect(reverse('users:records', args=[request.user.id]))


@login_required
def reserve_handle(request, book_id, sign):
    # 查询Loan表，找到预约记录
    user = request.user
    loan_logs = LibraryLoan.objects.filter(user_id=user.id).filter(flag=2).filter(book=book_id)
    book_handle = LibraryBook.objects.get(id=book_id)
    stock_handle = LibraryStock.objects.get(id=book_handle.stock_id)
    if loan_logs.exists():
        loan_log = loan_logs[0]
    else:
        errmsg = '找不到预约记录，请确认是否预约过此书'
        return HttpResponseRedirect(reverse('library:errormsg', args=[errmsg]))

    # sign: 0:取消预约 1:完成借阅
    # 取消预约：
    # 删除loan记录，
    # 修改Stock表（reserving-1），
    # （修改Book表，flag-1）
    # 修改Notification表（如果有，标记位flag = 4）
    # 若为通知状态，则通知下一个人。///
    if sign == 0:
        stock_handle.reserving -= 1
        book_handle.flag = 1

        notifications = LibraryNotification.objects.filter(user_id=user.id).filter(type=1).filter(index=loan_log.id)
        if notifications.exists():
            notification = notifications[0]
            notification.flag = 4

            notification.save()
            book_handle.save()
            stock_handle.save()
            loan_log.delete()
            # 通知下一个人（若果有人在预约的话）
            reserving_logs = LibraryLoan.objects.filter(flag=2).filter(book=book_id).order_by('loan_date')
            if reserving_logs.exists():
                reserving_log = reserving_logs[0]
                reserving_user = User.objects.get(id=reserving_log.user_id)
                notify_message = reserving_user.username + 'Hello!' + 'Your reserving book' + stock_handle.name + \
                                 '(with isbn:' + stock_handle.isbn + \
                                 ')can be borrowed now, please go to your personal page to get it!'
                # 通知Ta来取书
                notify_log = LibraryNotification.objects.create(user_id=reserving_log.user_id, message=notify_message,
                                                                flag=0,
                                                                index=reserving_log.id, type=1)
                notify_log.save()

        else:
            book_handle.save()
            stock_handle.save()
            loan_log.delete()

        msg = '预约取消成功'
        return HttpResponseRedirect(reverse('library:message', args=[msg]))

    # 完成预约：前提是被通知
    # 修改loan（flag，loan_date,loan_time,employee）；
    # 修改Stock（reserving -1 ）；
    # 修改Book（flag - 1）
    # 修改notification（标记完成, flag=2）
    notifications = LibraryNotification.objects.filter(user_id=user.id).filter(type=1).filter(index=loan_log.id)
    if notifications.exists():
        notification = notifications[0]
    else:
        msg = '目前没有剩余，请继续等待。'
        return HttpResponseRedirect(reverse('library:message', args=[msg]))

    if request.method == 'POST':
        loan_log.flag = 1
        loan_log.loan_date = timezone.now()
        loan_log.loan_time = request.POST.get('days')
        loan_log.employee_id = 1

        stock_handle.reserving -= 1
        book_handle.flag = 1

        notification.flag = 2
        notification.save()

        stock_handle.save()
        book_handle.save()
        loan_log.save()

        return HttpResponseRedirect(reverse('users:records', args=[user.id]))

    context = {'stock': stock_handle, 'log': loan_log, 'book_id': book_id}

    return render(request, 'library/reserve_handle.html', context)


@login_required
def suggest_book(request):

    if request.method != 'POST':
        form = SuggestionForm()
    else:
        form = SuggestionForm(data=request.POST)
        if form.is_valid():
            new_suggestion = form.save(commit=False)
            new_suggestion.user_id = request.user.id
            new_suggestion.save()
            return HttpResponseRedirect(reverse('users:records', args=[request.user.id]))

    context = {'form': form}
    return render(request, 'library/suggestion.html', context)


@login_required
def new_review(request, stock_id):
    stock = LibraryStock.objects.get(id=stock_id)
    if request.method != 'POST':
        form = ReviewForm()
    else:
        form = ReviewForm(data=request.POST)
        if form.is_valid():
            new_review = form.save(commit=False)
            new_review.stock = stock
            new_review.user = request.user
            new_review.username = request.user.username
            new_review.save()
            return HttpResponseRedirect(reverse('library:bookinfo', args=[stock_id]))

    context = {'stock': stock, 'form': form}
    return render(request, 'library/new_review.html', context)
    pass


@login_required
def edit_review(request, review_id):
    review = LibraryReview.objects.get(id=review_id)
    stock = review.stock
    # 确认用户，保护edit
    if review.user != request.user:
        raise Http404

    if request.method != "POST":
        form = ReviewForm(instance=review)
    else:
        form = ReviewForm(instance=review, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('library:bookinfo', args=[stock.id]))

    context = {'review': review, 'stock': stock, 'form': form}

    return render(request, 'library/edit_review.html', context)


@login_required
def error_msg(request, msg):
    return render(request, 'library/error_msg.html', {'msg': msg})
    pass


@login_required
def message(request, msg):
    return render(request, 'library/message.html', {'msg': msg})
    pass


@login_required
def add_book(request):
    if request.method == 'POST':
        book_name = request.POST.get('book_name')
        book_author = request.POST.get('book_author')
        book_isbn = request.POST.get('book_isbn')
        book_version = request.POST.get('book_version')
        book_publisher = request.POST.get('book_publisher')
        book_publish_date = request.POST.get('book_publish_date')
        book_location = request.POST.get('book_location')
        book_category = request.POST.get('book_category')
        book_price = request.POST.get('book_price')

        stock_check = LibraryStock.objects.filter(isbn=book_isbn)
        if stock_check.exists():
            stock_check[0].total += 1
            stock_check[0].remain += 1
            new_book = LibraryBook.objects.create(add_date=timezone.now(), location=book_location, flag=0,
                                                  stock=stock_check[0], isbn=book_isbn)
            new_book.save()
        else:
            new_stock = LibraryStock.objects.create(name=book_name, isbn=book_isbn, author=book_author,
                                                    version=book_version,
                                                    publisher=book_publisher, publish_date=book_publish_date,
                                                    category=book_category, price=book_price, total=1, remain=1,
                                                    reserving=0, review_number=0, review_rate=0)
            new_stock.save()
            new_book = LibraryBook.objects.create(add_date=timezone.now(), location=book_loacation, flag=0,
                                                    stock=new_stock, isbn=book_isbn)
            new_book.save()

        return HttpResponseRedirect(reverse('library:books'))

    return render(request,'library/add_book.html', context={ })
