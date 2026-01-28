from django.http import HttpResponseForbidden
from django.db.models.functions import TruncDate

from django.shortcuts import render
from .models import Product
from decimal import Decimal
from .models import Sale, SaleItem


from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def product_list(request):
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {'products': products})


from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('product_list')
        else:
            return render(request, 'store/login.html', {'error': 'Invalid credentials'})

    return render(request, 'store/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

from django.shortcuts import render
from .models import Product

def add_product(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Access Denied")

    if request.method == 'POST':
        name = request.POST['name']
        category = request.POST['category']
        price = request.POST['price']
        quantity = request.POST['quantity']

        Product.objects.create(
            name=name,
            category=category,
            price=price,
            quantity=quantity
        )
        return redirect('product_list')

    return render(request, 'store/add_product.html')

def billing(request):
    products = Product.objects.all()

    if request.method == 'POST':
        product_id = request.POST['product']
        quantity = int(request.POST['quantity'])

        # 1. Fetch the product first so we can check its stock
        product = Product.objects.get(id=product_id)

        # 2. VALIDATION CHECKS (Put them here!)
        if quantity <= 0:
            return render(request, 'store/billing.html', {
                'products': products,
                'error': 'Invalid quantity: Please enter a number greater than 0.'
            })

        if quantity > product.quantity:
            return render(request, 'store/billing.html', {
                'products': products,
                'error': f'Insufficient stock: Only {product.quantity} items left.'
            })

        # 3. Everything is valid, so proceed with the sale
        total_price = product.price * quantity

        # create sale
        sale = Sale.objects.create(total_amount=total_price)

        # create sale item
        SaleItem.objects.create(
            sale=sale,
            product=product,
            quantity=quantity,
            price=product.price
        )

        # update stock
        product.quantity -= quantity
        product.save()

        return render(request, 'store/bill_success.html', {
            'sale': sale,
            'product': product,
            'quantity': quantity,
            'total': total_price
        })

    return render(request, 'store/billing.html', {'products': products})
from .models import Sale

from django.db.models import Sum
from django.utils.timezone import now
from datetime import date

from django.db.models import Sum
from datetime import datetime, date

def sales_report(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Access Denied")

    sales = Sale.objects.all().order_by('-date')

    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if from_date and to_date:
        sales = sales.filter(
            date__date__range=[from_date, to_date]
        )

    total_sales_amount = sales.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_bills = sales.count()

    chart_data = (
        Sale.objects
        .annotate(day=TruncDate('date'))
        .values('day')
        .annotate(total=Sum('total_amount'))
        .order_by('day')
    )

    chart_labels = [str(item['day']) for item in chart_data]
    chart_values = [float(item['total']) for item in chart_data]

    context = {
        'sales': sales,
        'total_sales_amount': total_sales_amount,
        'total_bills': total_bills,
        'from_date': from_date,
        'to_date': to_date,
        'chart_labels': chart_labels,
'chart_values': chart_values,
    }

    return render(request, 'store/sales_report.html', context)

from reportlab.pdfgen import canvas
from django.http import HttpResponse

def export_sales_pdf(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Access Denied")

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'

    p = canvas.Canvas(response)
    p.setFont("Helvetica", 12)

    y = 800
    p.drawString(200, y, "AutoMart Sales Report")
    y -= 40

    sales = Sale.objects.all().order_by('-date')

    for sale in sales:
        line = f"Sale ID: {sale.id} | Date: {sale.date.date()} | Amount: ₹{sale.total_amount}"
        p.drawString(50, y, line)
        y -= 20
        if y < 50:
            p.showPage()
            y = 800

    p.showPage()
    p.save()
    return response

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import date

@login_required(login_url='login')
def dashboard(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Access Denied")

    total_products = Product.objects.count()
    total_sales = Sale.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_bills = Sale.objects.count()

    today = date.today()
    todays_sales = Sale.objects.filter(date__date=today)
    todays_amount = todays_sales.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    context = {
        'total_products': total_products,
        'total_sales': total_sales,
        'total_bills': total_bills,
        'todays_amount': todays_amount,
    }

    return render(request, 'store/dashboard.html', context)
