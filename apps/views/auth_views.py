from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import UpdateView, ListView, CreateView, TemplateView

from apps.forms import UserAuthenticatedForm, UserSettingsForm, UserChangePasswordForm, OperatorUpdateForm, \
    OperatorOrderCreateForm
from apps.mixins import GetObjectMixins
from apps.models import User, Region, Product, Order, SiteSettings, District


class UserLoginView(LoginView):
    template_name = 'apps/auth/login.html'
    redirect_authenticated_user = True
    form_class = UserAuthenticatedForm

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        return redirect('main_base')


class UserLogautView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        logout(request)

        return redirect('main_base')


class UserChangeImageView(GetObjectMixins, UpdateView):
    queryset = User.objects.values('image')
    template_name = 'apps/auth/settings.html'
    success_url = reverse_lazy('settings_page')
    fields = 'image',


class UserSettingsView(GetObjectMixins, UpdateView):
    queryset = User.objects.all()
    template_name = 'apps/auth/settings.html'
    success_url = reverse_lazy('settings_page')
    form_class = UserSettingsForm

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['regions'] = Region.objects.all()
        return context


class UserChangePasswordView(GetObjectMixins, UpdateView):
    queryset = User.objects.all()
    template_name = 'apps/auth/settings.html'
    success_url = reverse_lazy('settings_page')
    form_class = UserChangePasswordForm

    def form_valid(self, form):
        user = form.save(commit=False)
        login(self.request, user=user.save())
        return redirect(self.success_url)


class OperatorOrderListView(ListView):
    queryset = Order.objects.all()
    template_name = 'apps/operators/operator_list.html'
    context_object_name = 'orders'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        status = self.kwargs.get('status') or self.request.path.split('/')[-2]
        return qs if not status else qs.filter(Q(operator=self.request.user.id) | Q(operator__isnull=True)).filter(
            status=status)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['regions'] = Region.objects.all()
        context['districts'] = District.objects.all()
        context['products'] = Product.objects.all()
        return context


class OperatorDetailView(UpdateView):
    queryset = Order.objects.all()
    template_name = 'apps/operators/operator_detail.html'
    context_object_name = 'order'
    form_class = OperatorUpdateForm
    success_url = reverse_lazy('operator_page')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['regions'] = Region.objects.all()
        context['site_settings'] = SiteSettings.objects.all()
        return context

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        session_operator = self.request.user
        if obj.operator is None:
            obj.operator = session_operator
            obj.save()
        return obj


class OperatorCreateOrderView(CreateView):
    queryset = Order.objects.all()
    template_name = 'apps/operators/operator_add_product.html'
    form_class = OperatorOrderCreateForm
    success_url = reverse_lazy('operator_page')

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['regions'] = Region.objects.all()
        ctx['products'] = Product.objects.all()
        return ctx


class CurrierOrderListView(TemplateView):
    template_name = 'apps/couriers/currier_order_list.html'


class CurrierOrderDetailView(TemplateView):
    template_name = 'apps/couriers/currier_detail.html'


class CurrierListView(TemplateView):
    template_name = 'apps/couriers/currier_list.html'
