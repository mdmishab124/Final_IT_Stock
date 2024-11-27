from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class Department(models.Model):
    name = models.CharField(
        max_length=100, 
        unique=True, 
        verbose_name=_("Department Name"),
        help_text=_("Name of the department")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Department")
        verbose_name_plural = _("Departments")
        ordering = ['name']

    def __str__(self):
        return self.name


class Account(models.Model):
    ROLE_CHOICES = [
        ('admin', _('Admin')),
        ('staff', _('Staff')),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='account',
        verbose_name=_("User"),
        help_text=_("Associated user account")
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        related_name='accounts',
        null=True,
        blank=True,
        verbose_name=_("Department"),
        help_text=_("Department this account belongs to")
    )
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='staff',
        verbose_name=_("Role"),
        help_text=_("Account role determines permissions")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_("Designates whether this account should be treated as active")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Account")
        verbose_name_plural = _("Accounts")
        ordering = ['user__username']

    def __str__(self):
        return f"{self.user.username} - {self.role.title()}"


class Category(models.Model):
    category = models.CharField(
        max_length=100, 
        unique=True, 
        verbose_name=_("Category"),
        help_text=_("Item category name")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ['category']

    def __str__(self):
        return self.category


class AvailableStock(models.Model):
    STATUS_CHOICES = [
        ('available', _('Available')),
        # ('assigned', _('Assigned')),
        ('maintenance', _('Under Maintenance')),
        ('retired', _('Retired')),
        ('inuse', _('In Use')),
    ]

    item_id = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name=_("Item ID"),
        help_text=_("Unique identifier for the item")
    )
    item_name = models.CharField(
        max_length=100, 
        verbose_name=_("Item Name"),
        help_text=_("Name of the item")
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name=_("Category"),
        help_text=_("Item category")
    )
    serial_no = models.CharField(
        max_length=100, 
        unique=True, 
        verbose_name=_("Serial Number"),
        help_text=_("Unique serial number of the item")
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='stocks',
        verbose_name=_("Department"),
        help_text=_("Department owning this item")
    )
    status = models.CharField(
        max_length=100,
        choices=STATUS_CHOICES,
        default='available',
        verbose_name=_("Status"),
        help_text=_("Current status of the item")
    )
    location = models.CharField(
        max_length=200, 
        verbose_name=_("Location"),
        help_text=_("Physical location of the item")
    )
    assigned_to = models.CharField(
        max_length=100, 
        null=True, 
        blank=True, 
        verbose_name=_("Assigned To"),
        help_text=_("Person to whom the item is assigned")
    )
    date = models.DateField(
        verbose_name=_("Date Added"),
        auto_now_add=True,
        help_text=_("Date when the item was added to inventory")
    )
    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Purchase Price"),
        help_text=_("Price at which the item was purchased")
    )
    purchase_date = models.DateField(
        verbose_name=_("Purchase Date"),
        help_text=_("Date when the item was purchased")
    )
    shop_or_platform = models.CharField(
        max_length=200,
        verbose_name=_("Shop/Platform"),
        help_text=_("Shop or online platform where the item was purchased")
    )
    invoice_number = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("Invoice Number"),
        help_text=_("Optional invoice number for the purchase")
    )
    description = models.TextField(
        max_length=500, 
        blank=True, 
        verbose_name=_("Description"),
        help_text=_("Additional details about the item")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Available Stock")
        verbose_name_plural = _("Available Stocks")
        ordering = ['-date']
        indexes = [
            models.Index(fields=['status', 'department']),
            models.Index(fields=['item_id']),
            models.Index(fields=['serial_no']),
        ]

    def __str__(self):
        return f"{self.item_name} - {self.item_id}"

    def clean(self):
        if self.status == 'assigned' and not self.assigned_to:
            raise ValidationError({
                'assigned_to': _('Assigned To is required when status is Assigned')
            })
        
        if self.status != 'assigned' and self.assigned_to:
            # Instead of validation error, automatically clear assigned_to
            self.assigned_to = None

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)



class Complaint(models.Model):
    PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('in_progress', _('In Progress')),
        ('resolved', _('Resolved')),
        ('closed', _('Closed')),
    ]

    title = models.CharField(
        max_length=200,
        verbose_name=_("Title"),
        help_text=_("Brief title of the complaint")
    )
    description = models.TextField(
        verbose_name=_("Description"),
        help_text=_("Detailed description of the complaint")
    )
    submitted_by = models.ForeignKey(
        'Account',
        on_delete=models.CASCADE,
        related_name='complaints',
        verbose_name=_("Submitted By"),
        help_text=_("Staff member who submitted the complaint")
    )
    department = models.ForeignKey(
        'Department',
        on_delete=models.CASCADE,
        related_name='department_complaints',
        verbose_name=_("Department"),
        help_text=_("Department related to the complaint")
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name=_("Priority"),
        help_text=_("Priority level of the complaint")
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_("Status"),
        help_text=_("Current status of the complaint")
    )
    assigned_to = models.ForeignKey(
        'Account',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_complaints',
        verbose_name=_("Assigned To"),
        help_text=_("Admin assigned to handle this complaint")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolution_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Resolution Date"),
        help_text=_("Date when the complaint was resolved")
    )
    resolution_notes = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Resolution Notes"),
        help_text=_("Notes about how the complaint was resolved")
    )

    class Meta:
        verbose_name = _("Complaint")
        verbose_name_plural = _("Complaints")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['submitted_by']),
            models.Index(fields=['department']),
        ]

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

    def clean(self):
        if self.status in ['resolved', 'closed'] and not self.resolution_notes:
            raise ValidationError({
                'resolution_notes': _('Resolution notes are required when marking as resolved or closed')
            })
        
        if self.status == 'in_progress' and not self.assigned_to:
            raise ValidationError({
                'assigned_to': _('Assigned To is required when status is In Progress')
            })

    def save(self, *args, **kwargs):
        self.clean()
        # Set resolution date when status changes to resolved
        if self.status == 'resolved' and not self.resolution_date:
            self.resolution_date = timezone.now()
        super().save(*args, **kwargs)

