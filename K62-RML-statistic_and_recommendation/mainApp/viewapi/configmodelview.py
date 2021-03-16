
from django.shortcuts import render, redirect
from django.contrib import messages
from mainApp.forms import DumpModelForm
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseRedirect
from mainApp import models as mainModel
from django.template.response import TemplateResponse
from mainApp.middlewares import checkInUrl
from django.urls import reverse
from django.http import HttpResponseRedirect
from mainApp.viewapi.logs import createLog
from django.contrib import messages


@require_http_methods(["GET"])
def get_config_model(request):
    if checkInUrl(request, 'configmodel') is False:
        listFunction = request.user.list_function()
        return HttpResponseRedirect(reverse(listFunction[0]))
    forms = []
    dump_models = mainModel.DumpModel.objects.all().order_by('pk')
    for record in dump_models:
        forms.append(DumpModelForm(instance=record))
    return TemplateResponse(request, 'adminuet/configmodel.html', {'forms': forms})


@require_http_methods(["POST"])
def post_config_model(request, model_id=None):
    if checkInUrl(request, 'configmodel') is False:
        listFunction = request.user.list_function()
        return HttpResponseRedirect(reverse(listFunction[0]))
    if model_id is not None:
        dump_model = None
        try:
            dump_model = mainModel.DumpModel.objects.get(dumpModelID=model_id)
        except mainModel.DumpModel.DoesNotExist:
            messages.add_message(request, messages.INFO, "Model id don't exist.")
        form = DumpModelForm(instance=dump_model, data=request.POST)
        if form.is_valid():
            form.save()
            createLog(request, 'CHOICE - Lựa chọn mô hình', '')
            messages.success(request, "Cập nhật thành công.")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
