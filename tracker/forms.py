from django import forms
from .models import Project, Stakeholder, ChecklistItem

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'project_number', 'address', 'start_date', 'stage']
        labels = {
            'name': 'Project Name',
            'project_number': 'Project Number',
            'address': 'Address',
            'start_date': 'Start Date',
            'stage': 'Stage',
        }

class StakeholderForm(forms.ModelForm):
    class Meta:
        model = Stakeholder
        fields = ['name', 'role', 'email', 'phone']

class ChecklistItemForm(forms.ModelForm):
    class Meta:
        model = ChecklistItem
        fields = ['item', 'status', 'notes']

from .models import ProjectStakeholder

class ProjectStakeholderForm(forms.ModelForm):
    class Meta:
        model = ProjectStakeholder
        fields = ['stakeholder', 'role_description']
        
from .models import Document

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['doc_type', 'filename', 'file']