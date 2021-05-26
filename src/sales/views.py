from django.shortcuts import render
from django.views.generic import ListView,DetailView,TemplateView
from .models import Sale,Position,CSV
from .forms import SalesSearchForm
from reports.forms import ReportForm
import pandas as pd
from .utilis import get_customer_from_id,get_salesman_from_id,get_chart
from django.http import HttpResponse
from products.models import Product
from customers.models import Customer 
import csv
from django.utils.dateparse import parse_date
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
@login_required
def home_view(request):
    sales_df = None
    positions_df = None
    merged_df = None
    df = None
    chart = None
    no_data = None
    search_form = SalesSearchForm(request.POST or None)
    report_form = ReportForm()
    if request.method == "POST":
        date_from = request.POST.get("date_from")
        date_to = request.POST.get("date_to")
        chart_type = request.POST.get("chart_type")
        results_by = request.POST.get("results_by")
        print(date_from,date_to,chart_type)

        sale_qs = Sale.objects.filter(created__date__lte=date_to, created__date__gte=date_from)
        if len(sale_qs) > 0:
            sales_df = pd.DataFrame(sale_qs.values())
            
            sales_df['customer_id'] = sales_df["customer_id"].apply(get_customer_from_id)
            sales_df["salesman_id"] = sales_df["salesman_id"].apply(get_salesman_from_id)
            sales_df["created"] = sales_df["created"].apply(lambda x: x.strftime('%Y-%m-%d'))
            sales_df.rename({'customer_id':"customer","salesman_id":"salesman",'id':"sales_id"}, axis =1,inplace=True)
            
            position_data = []
            for sale in sale_qs:
                sale_id = sale.id
                for pos in sale.get_positions():
                    obj = {
                        "positon_id" : pos.id,
                        "product" : pos.product.name,
                        'quantity' : pos.quantity,
                        "price" : pos.price,
                        "sales_id" : sale_id,
                    }
                    position_data.append(obj)
            
            positions_df = pd.DataFrame(position_data)
            merged_df = pd.merge(sales_df, positions_df, on="sales_id")
            df = merged_df.groupby("transaction_id",as_index=False)["price"].agg("sum")

            chart = get_chart(chart_type, sales_df, results_by)
            positions_df = positions_df.to_html()
            sales_df = sales_df.to_html()
            merged_df = merged_df.to_html()
            df =df.to_html()
        else:
            no_data = "No data available"
    context ={
        "search_form" : search_form,
        "report_form" : report_form,
        "sales_df": sales_df,
        "position_df":positions_df,
        "merged_df" : merged_df,
        "df" : df,
        'chart' : chart, 
        "no_data" : no_data,
    }
    return render(request,"sales/home.html",context)

@login_required
def csv_upload(request):
    if request.method == "POST":
        csv_file_name = request.FILES.get('file').name
        csv_file = request.FILES.get('file')
        obj,created = CSV.objects.create(file_name=csv_file_name)

        if created:
            obj.csv_file = csv_file
            obj.save()
            with open(obj.csv_file.path, 'r') as f:
                reader = csv.reader(f)
                reader.__next__()
                for row in reader:
                    data = "".join(row)
                    data = data.split(";")
                    data.pop()

                    transaction_id = data[1]
                    product = data[2]
                    quantity = int(data[3])
                    customer = data[4]
                    data = parse_date( data[5] )

                    try:
                        product_obj = Product.objects.get(name__iexact=product)
                        
                        if product_obj is not None:
                            customer_obj, _ = Customer.objects.get_or_create(name=customer)
                            salesman_obj = Profile.Objects.get(user=requeste.user)
                            position_obj = Position.objects.create(products=product_obj, quantity = quantity, created=data)

                            sales_obj, _ = Sale.objects.get_or_create(transaction_id=transaction_id,customer = customer_obj, salesman=salesman_obj,created=date)
                            sales_obj.positions.add(position_obj)
                            sales_obj.save()

                    except Product.DoesNotExist:
                        product_obj = None
                return JsonResponse({'ex':False})
        else:
            return JsonResponse({'ex':True})


    return render(request, "sales/from_file.html")

class SaleListView(LoginRequiredMixin,ListView):
    model = Sale
    template_name = "sales/main.html"


class SaleDetailView(LoginRequiredMixin, DetailView):
    model = Sale
    template_name = "sales/detail.html"


class UploadTemplateView(LoginRequiredMixin, TemplateView):
    template_name = "sales/from_file.html"
