from django.utils import timezone
from openpyxl import Workbook
from django.http import FileResponse, HttpResponse
from .models import Robot
from django.db.models import Count
import os
from django.conf import settings

def generate_production_summary_excel():
    # Получаем данные за последнюю неделю
    one_week_ago = timezone.now() - timezone.timedelta(days=7)
    data = (
        Robot.objects.filter(created__gte=one_week_ago)
        .values("model", "version")  # Группировка по полям
        .annotate(total_count=Count("id"))  # Подсчёт количества записей
    )

    # Группируем данные по моделям
    grouped_data = {}
    for record in data:
        model = record["model"]
        if model not in grouped_data:
            grouped_data[model] = []
        grouped_data[model].append(record)

    # Создаем Excel-файл
    workbook = Workbook()

    # Удаляем стандартный пустой лист
    if workbook.active:
        workbook.remove(workbook.active)

    # Создаем листы для каждой модели
    for model, records in grouped_data.items():
        sheet = workbook.create_sheet(title=model)
        sheet.append(['Model', 'Version', 'Total Count'])

        for record in records:
            sheet.append([record["model"], record["version"], record["total_count"]])

    # Сохраняем файл в MEDIA_ROOT
    directory = getattr(settings, 'MEDIA_ROOT', '/tmp')
    filename = f'robot_production_summary_{timezone.now().strftime("%Y%m%d")}.xlsx'
    full_path = os.path.join(directory, filename)

    try:
        workbook.save(full_path)
    except Exception as e:
        print(f"Error saving file: {e}")
        return None

    return full_path


def download_production_summary(request):
    file_path = generate_production_summary_excel()
    if not file_path:
        return HttpResponse("Error generating file", status=500)

    response = FileResponse(
        open(file_path, 'rb'),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'
    return response
