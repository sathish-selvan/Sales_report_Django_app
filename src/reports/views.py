from django.shortcuts import render,get_object_or_404
from profiles.models import Profile
from django.http import JsonResponse
from .utlis import get_report_image
from .models import Report
from django.views.generic import ListView,DetailView

from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
#o Create your views here.

class ReportListView(LoginRequiredMixin,ListView):
    model = Report
    template_name = "reports/main.html"


class ReportDetailView(LoginRequiredMixin, DetailView):
    model = Report
    template_name = "reports/detail.html"


@login_required
def create_report_veiw(request):
    if request.is_ajax:
        name = request.POST.get('name')
        remarks = request.POST.get('remarks')
        image = request.POST.get("image") 
        author = Profile.objects.get(user=request.user )
        img = get_report_image(image)
        Report.objects.create(name=name, remarks=remarks, image=img,author=author,)
        return JsonResponse({'msg':"send"})
    return JsonResponse({})

@login_required
def render_pdf_view(request,pk):
    template_path = 'reports/pdf.html'
    obj = get_object_or_404(Report,pk=pk)
    context = {'obj': obj}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    # if download
    # response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    # if display
    response['Content-Disposition'] = 'filename="report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
        html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response
