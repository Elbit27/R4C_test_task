import json
from django.http import JsonResponse
from django.views import View
from .forms import RobotForm, Robot
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


@method_decorator(csrf_exempt, name='dispatch')
class RobotCreateView(View):
    def post(self, request):
        # Парсим JSON из тела запроса
        try:
            data = json.loads(request.body)
        except ValueError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

        # Валидируем данные через форму
        form = RobotForm(data)

        # Проверка на уникальность модели
        if form.is_valid():
            if Robot.objects.filter(model=form.cleaned_data['model']).exists():
                return JsonResponse({"error": "Model already exists"}, status=400)
            # Сохраняем запись в БД
            robot = form.save()
            return JsonResponse(
                {"message": "Robot created successfully!",
                 "robot": {"model": robot.model, "version": robot.version, "created": robot.created}},
                status=201
            )
        else:
            # Возвращаем ошибки валидации
            return JsonResponse({"errors": form.errors}, status=400)