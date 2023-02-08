from django.contrib import admin

from .models import Project, ProjectPurchaseRequest


# Register your models here.
class UpdateUsersAdminModel(admin.ModelAdmin):
    class Meta:
        abstract = True

    def save_model(self, request, obj, form, change) -> None:
        if not change:
            obj.created_by = request.user

        obj.updated_by = request.user
        return super().save_model(request, obj, form, change)


class PurchaseRequestInline(admin.TabularInline):
    model = ProjectPurchaseRequest
    # fields = ("purchase_request",)
    extra = 1


@admin.register(Project)
class ProjectAdmin(UpdateUsersAdminModel):
    list_display = ["name", "manager", "created_date", "updated_date"]
    list_filter = ["manager"]
    date_hierarchy = "created_date"
    search_fields = ["name", "manager__user__first_name", "manager__user__last_name"]
    inlines = [PurchaseRequestInline]


@admin.register(ProjectPurchaseRequest)
class ProjectPurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ["project", "purchase_request", "rank"]
