from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'to_complete_at', 'priority', 'completed']
        widgets = {
            'to_complete_at': forms.DateTimeInput(attrs={
                'type': 'text',
                'class': 'flatpickr-input',
                'placeholder': 'Select date and time'
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Enter task description (optional)'
            }),
            'title': forms.TextInput(attrs={
                'placeholder': 'What needs to be done?'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['priority'].required = False
        self.fields['to_complete_at'].required = False
        self.fields['description'].required = False
        
        # Only show completed field when editing an existing task
        if self.instance and self.instance.pk:
            self.fields['completed'].widget.attrs.update({
                'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'
            })
        else:
            # Hide completed field for new tasks
            self.fields['completed'].widget = forms.HiddenInput()