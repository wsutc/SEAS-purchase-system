# from django.shortcuts import render

from django.contrib import messages
from django.views.generic import (  # DeleteView,; UpdateView,
    CreateView,
    DetailView,
    ListView,
)

from web_project.helpers import PaginatedListMixin

from .form import CreateProjectForm
from .models import Project, ProjectPurchaseRequest


# Create your views here.
class ProjectListView(PaginatedListMixin, ListView):
    context_object_name = "projects"
    queryset = Project.objects.all()


class ProjectDetailView(DetailView):
    template_name = "projects/project_detail.html"
    model = Project
    query_pk_and_slug = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # trackers = []
        # object = self.get_object()

        # prs = object.purchase_requests.all()

        # for request in prs:
        #     for tracker in request.tracker_set.all():
        #         trackers.append(tracker)

        # context["trackers"] = trackers

        return context


class ProjectCreateView(CreateView):
    form_class = CreateProjectForm
    template_name = "projects/project_create.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)

        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user

        self.object.save()

        for request in self.object.purchase_requests.all():
            print(f"Request: {request}")

        # context = self.get_context_data()

        for request in form.cleaned_data["purchase_requests"]:
            ppr = ProjectPurchaseRequest.objects.create(
                purchase_request=request, project=self.object
            )

            form.instance.projectpurchaserequest_set.add(ppr)

        if hasattr(form, "message"):
            messages.info(self.request, form.message)

        return super().form_valid(form)

    # def get_initial(self):
    #     initial = super().get_initial().copy()

    #     created_by = self.request.user
    #     updated_by = self.request.user
    #     initial.update(
    #         {
    #             "created_by": created_by,
    #             "updated_by": updated_by,
    #         }
    #     )
    #     return initial

    # def post(self, request, *args: str, **kwargs):
    #     self.created_by = request.user
    #     self.updated_by = request.user

    #     post_data = super().post(request, *args, **kwargs)

    #     return post_data
