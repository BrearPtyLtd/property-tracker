from django.contrib import admin
from .models import Project, Stakeholder, ProjectStakeholder, ChecklistItem, Document

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('project_number', 'name', 'stage', 'start_date')
    search_fields = ('name', 'project_number', 'address')

@admin.register(Stakeholder)
class StakeholderAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'email', 'phone')
    list_filter = ('role',)
    search_fields = ('name', 'email')

@admin.register(ProjectStakeholder)
class ProjectStakeholderAdmin(admin.ModelAdmin):
    list_display = ('project', 'stakeholder', 'role_description')

@admin.register(ChecklistItem)
class ChecklistItemAdmin(admin.ModelAdmin):
    list_display = ('project', 'item', 'status', 'updated_at')
    list_filter = ('status',)
    search_fields = ('item', 'notes')

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('project', 'filename', 'doc_type', 'uploaded_at')
    list_filter = ('doc_type',)
    search_fields = ('filename',)

