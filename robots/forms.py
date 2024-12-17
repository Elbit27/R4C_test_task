from django import forms
from .models import Robot


class RobotForm(forms.ModelForm):
    class Meta:
        model = Robot
        fields = ('model', 'version', 'created')

    # Дополнительная валидация
    def clean_model(self):
        model = self.cleaned_data.get('model')
        if not model.isalnum():  # Пример: модель должна быть буквенно-цифровой
            raise forms.ValidationError("Model name should only contain letters and numbers.")
        return model
