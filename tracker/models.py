from django.db import models

class Project(models.Model):
    name = models.CharField(max_length=200)
    project_number = models.CharField(max_length=100, unique=True)
    address = models.TextField()
    start_date = models.DateField()
    stage = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.project_number} - {self.name}"

class Stakeholder(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('certifier', 'Certifier'),
        ('surveyor', 'Surveyor'),
        ('architect', 'Architect'),
        ('builder', 'Builder'),
    ]
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.name} ({self.role})"

class ProjectStakeholder(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    stakeholder = models.ForeignKey(Stakeholder, on_delete=models.CASCADE)
    role_description = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.project} ↔ {self.stakeholder}"

class ChecklistItem(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('complete', 'Complete'),
        ('failed', 'Failed'),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    item = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.item} - {self.project} ({self.status})"

class Document(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    filename = models.CharField(max_length=255)
    doc_type = models.CharField(max_length=100)
    file = models.FileField(upload_to='documents/', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.filename} ({self.doc_type}) - {self.project}"