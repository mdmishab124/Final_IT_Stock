from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from .models import Account, Department, AvailableStock, Category


class AccountAdmin(ModelAdmin):
    list_display = ['get_username', 'get_department', 'role', 'is_active']
    list_filter = ['role', 'department', 'is_active', 'created_at']
    search_fields = ['user__username', 'department__name', 'role']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 10
    ordering = ['-created_at']

    fieldsets = [
        (
            _("User Information"),
            {
                "fields": ['user', 'department', 'role', 'is_active'],
                "description": _("Manage user accounts and their department details."),
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": ['created_at', 'updated_at'],
                "classes": ['collapse'],
            },
        ),
    ]

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = _('Username')
    get_username.admin_order_field = 'user__username'

    def get_department(self, obj):
        return obj.department.name if obj.department else _('No Department')
    get_department.short_description = _('Department')
    get_department.admin_order_field = 'department__name'

    actions = ['make_staff', 'make_admin', 'activate_accounts', 'deactivate_accounts']

    def make_staff(self, request, queryset):
        queryset.update(role='staff')
    make_staff.short_description = _("Set selected accounts as staff")

    def make_admin(self, request, queryset):
        queryset.update(role='admin')
    make_admin.short_description = _("Set selected accounts as admin")

    def activate_accounts(self, request, queryset):
        queryset.update(is_active=True)
    activate_accounts.short_description = _("Activate selected accounts")

    def deactivate_accounts(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_accounts.short_description = _("Deactivate selected accounts")


class DepartmentAdmin(ModelAdmin):
    list_display = ['name', 'get_accounts_count', 'get_stocks_count']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = [
        (
            _("Department Details"),
            {
                "fields": ['name'],
                "description": _("Manage department information."),
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": ['created_at', 'updated_at'],
                "classes": ['collapse'],
            },
        ),
    ]

    def get_accounts_count(self, obj):
        return obj.accounts.count()
    get_accounts_count.short_description = _('Number of Accounts')

    def get_stocks_count(self, obj):
        return obj.stocks.count()
    get_stocks_count.short_description = _('Number of Stocks')


class CategoryAdmin(ModelAdmin):
    list_display = ['category', 'created_at']
    search_fields = ['category']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = [
        (
            _("Category Details"),
            {
                "fields": ['category'],
                "description": _("Manage category information."),
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": ['created_at', 'updated_at'],
                "classes": ['collapse'],
            },
        ),
    ]


@admin.register(AvailableStock)
class AvailableStockAdmin(ModelAdmin):
    list_display = [
        'item_id', 'item_name', 'category', 'serial_no',
        'status', 'location', 'date', 'department', 
        'purchase_price', 'purchase_date'
    ]
    list_filter = [
        'status', 'department', 'category', 'date', 
        'purchase_date', 'shop_or_platform'  # Changed from 'purchase_platform' to 'shop_or_platform'
    ]
    search_fields = [
        'item_id', 'item_name', 'serial_no', 'assigned_to', 'status',
        'location', 'description', 
        'invoice_number', 'shop_or_platform'  # Changed from 'purchase_platform' to 'shop_or_platform'
    ]
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status', 'location', 'purchase_price']  # Optional: added purchase_price
    date_hierarchy = 'purchase_date'  # Changed from 'date' to support new field
    ordering = ['-date']
    list_per_page = 20

    def get_fieldsets(self, request, obj=None):
        # Common fieldsets for both add and change forms
        common_fieldsets = [
            (
                _("Basic Information"),
                {
                    "fields": ['item_id', 'item_name', 'category', 'serial_no'],
                    "description": _("Basic item information."),
                },
            ),
            (
                _("Purchase Details"),  # New fieldset for purchase information
                {
                    "fields": ['purchase_price', 'purchase_date', 'shop_or_platform', 'invoice_number'],  # Changed purchase_platform to shop_or_platform
                    "description": _("Purchase and procurement details."),
                    "classes": ['collapse'],
                },
            ),
            (
                _("Additional Details"),
                {
                    "fields": ['description'],  
                    "classes": ['collapse'],
                },
            ),
            (
                _("Timestamps"),
                {
                    "fields": ['created_at', 'updated_at'],
                    "classes": ['collapse'],
                },
            ),
        ]

        # If this is an add form (obj is None)
        if obj is None:
            # Add form: exclude assigned_to
            status_fieldset = (
                _("Status and Location"),
                {
                    "fields": ['department', 'status', 'location'],
                    "description": _("Current status and location information."),
                },
            )
        else:
            # Change form: include assigned_to
            status_fieldset = (
                _("Status and Location"),
                {
                    "fields": ['department', 'status', 'location', 'assigned_to'],
                    "description": _("Current status and location information."),
                },
            )

        # Insert the status fieldset at the appropriate position
        fieldsets = list(common_fieldsets)
        fieldsets.insert(1, status_fieldset)
        return fieldsets

    actions = [
        'mark_as_available', 'mark_as_maintenance', 'mark_as_retired',
        'export_purchase_details'  # Optional: new action for exporting
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        
        try:
            account = request.user.account
            if account.role == 'admin':
                return qs
            elif account.role == 'staff' and account.department:
                return qs.filter(department=account.department)
            return qs.none()
        except Account.DoesNotExist:
            return qs.none()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "department" and not request.user.is_superuser:
            try:
                account = request.user.account
                if account.role == 'staff' and account.department:
                    kwargs["queryset"] = Department.objects.filter(id=account.department.id)
            except Account.DoesNotExist:
                kwargs["queryset"] = Department.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_change_permission(self, request, obj=None):
        if not request.user.is_superuser:
            if obj and obj.department != request.user.account.department:
                return False
        return super().has_change_permission(request, obj)

    def mark_as_available(self, request, queryset):
        queryset.update(status='available', assigned_to=None)
    mark_as_available.short_description = _("Mark selected items as available")

    def mark_as_maintenance(self, request, queryset):
        queryset.update(status='maintenance', assigned_to=None)
    mark_as_maintenance.short_description = _("Mark selected items as under maintenance")

    def mark_as_retired(self, request, queryset):
        queryset.update(status='retired', assigned_to=None)
    mark_as_retired.short_description = _("Mark selected items as retired")

    def export_purchase_details(self, request, queryset):
        """
        Optional action to export purchase details 
        (You might want to implement this using a library like 'django-import-export')
        """
        pass
    export_purchase_details.short_description = _("Export purchase details")

    

# Unregister and register User and Group with custom admin
admin.site.unregister(User)
admin.site.unregister(Group)

@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    pass

@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass

# Register the custom admins
admin.site.register(Account, AccountAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Category, CategoryAdmin)




from django.utils import timezone
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Complaint


# class ComplaintCommentInline(admin.TabularInline):
#     model = ComplaintComment
#     extra = 1
#     readonly_fields = ['author', 'created_at']
    
#     def has_delete_permission(self, request, obj=None):
#         return request.user.is_superuser
    
#     def save_model(self, request, obj, form, change):
#         if not obj.author_id:
#             obj.author = request.user.account
#         super().save_model(request, obj, form, change)


@admin.register(Complaint)
class ComplaintAdmin(ModelAdmin):
    list_display = [
        'title', 'priority', 'status', 'department',
        'submitted_by', 'assigned_to', 'created_at'
    ]  # Removed get_comments_count since it's not being used
    list_filter = ['status', 'priority', 'department', 'created_at']
    search_fields = ['title', 'description', 'submitted_by__user__username']
    readonly_fields = ['created_at', 'updated_at', 'submitted_by']
    date_hierarchy = 'created_at'
    list_per_page = 20

    def get_fieldsets(self, request, obj=None):
        # Base fieldsets that all users can see
        base_fieldsets = [
            (
                _("Complaint Information"),
                {
                    "fields": ['title', 'description', 'department', 'priority'],
                },
            ),
            (
                _("Timestamps"),
                {
                    "fields": ['created_at', 'updated_at'],
                    "classes": ['collapse'],
                },
            ),
        ]
        
        # Only add Status & Assignment fieldset for admin and superuser
        if request.user.is_superuser or (hasattr(request.user, 'account') and request.user.account.role == 'admin'):
            base_fieldsets.insert(1, (
                _("Status & Assignment"),
                {
                    "fields": ['status', 'assigned_to', 'resolution_notes', 'resolution_date'],
                },
            ))
        
        return base_fieldsets

    def get_list_display(self, request):
        # Modify list display based on user role
        if request.user.is_superuser or (hasattr(request.user, 'account') and request.user.account.role == 'admin'):
            return self.list_display
        return ['title', 'priority', 'department', 'created_at']

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.readonly_fields
        
        try:
            account = request.user.account
            if account.role == 'admin':
                return self.readonly_fields
            elif account.role == 'staff':
                if obj:  # Existing complaint
                    return [f.name for f in self.model._meta.fields]
                # New complaint - staff can only edit basic fields
                return ['created_at', 'updated_at', 'submitted_by', 
                       'status', 'assigned_to', 'resolution_notes', 
                       'resolution_date']
        except Account.DoesNotExist:
            pass
        
        return self.readonly_fields

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        
        try:
            account = request.user.account
            if account.role == 'admin':
                return qs
            elif account.role == 'staff':
                return qs.filter(submitted_by=account)
            return qs.none()
        except Account.DoesNotExist:
            return qs.none()

    def save_model(self, request, obj, form, change):
        if not change:  # New complaint
            obj.submitted_by = request.user.account
        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        if not obj:
            return True
        
        if request.user.is_superuser:
            return True
            
        try:
            account = request.user.account
            if account.role == 'admin':
                return True
            elif account.role == 'staff':
                return obj.submitted_by == account and obj.status == 'pending'
        except Account.DoesNotExist:
            pass
        
        return False

    actions = ['mark_in_progress', 'mark_resolved', 'mark_closed', 'assign_to_me']

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not (request.user.is_superuser or 
                (hasattr(request.user, 'account') and request.user.account.role == 'admin')):
            return []
        return actions

    def mark_in_progress(self, request, queryset):
        queryset.update(
            status='in_progress',
            assigned_to=request.user.account,
            updated_at=timezone.now()
        )
    mark_in_progress.short_description = _("Mark selected complaints as in progress")

    def mark_resolved(self, request, queryset):
        queryset.update(
            status='resolved',
            resolution_date=timezone.now(),
            updated_at=timezone.now()
        )
    mark_resolved.short_description = _("Mark selected complaints as resolved")

    def mark_closed(self, request, queryset):
        queryset.update(
            status='closed',
            updated_at=timezone.now()
        )
    mark_closed.short_description = _("Mark selected complaints as closed")

    def assign_to_me(self, request, queryset):
        queryset.update(
            assigned_to=request.user.account,
            updated_at=timezone.now()
        )
    assign_to_me.short_description = _("Assign selected complaints to me")

