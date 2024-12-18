import json
from django.http import JsonResponse
from django.views import View
from .forms import RobotForm, Robot
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from orders.models import Order
from django.core.mail import send_mail

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

        # Проверка на наличие модели в БД
        if form.is_valid():
            message = "Robot created successfully!"
            if Robot.objects.filter(model=form.cleaned_data.get('model')).exists():
                message = f"Robot with model {form.cleaned_data['model']} already exists! " + message
            # Сохраняем запись в БД
            robot = form.save()

            robot_serial = robot.serial
            orders = Order.objects.filter(robot_serial=robot_serial)
            if orders.exists():
                for order in orders:
                    self.notify_customer(order.customer.email, robot_serial)

            return JsonResponse(
                {"message": message,
                 "robot": {"serial": robot.serial, "model": robot.model, "version": robot.version, "created": robot.created}},
                status=201
            )
        else:
            # Возвращаем ошибки валидации
            return JsonResponse({"errors": form.errors}, status=400)


    @staticmethod
    def notify_customer(email, robot_serial):
        subject = "Робот теперь доступен"
        message = (
            f"Добрый день!\n"
            f"Недавно вы интересовались нашим роботом с серийным номером {robot_serial}. "
            f"Этот робот теперь в наличии. Если вам подходит этот вариант - пожалуйста, свяжитесь с нами."
        )
        from_email = None  # Используется DEFAULT_FROM_EMAIL из настроек

        try:
            send_mail(
                subject,
                message,
                from_email,
                [email],
                fail_silently=False,  # Если ошибка, выбрасывается исключение
            )
            print(f"Письмо успешно отправлено на {email}")
        except Exception as e:
            print(f"Ошибка при отправке письма на {email}: {e}")

        Order.objects.filter(customer__email=email, robot_serial=robot_serial).delete()
