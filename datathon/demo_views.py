
import enum
import random

from django.shortcuts import render

from datathon.views import CommodityType
from datathon.models import get_db_connection


class DemoWeather(enum.Enum):
    RAINY = 'RAINY'
    SUNNY = 'SUNNY'

    @classmethod
    def get_weather_by_string(cls, weather_string):
        if weather_string.lower() == 'sunny':
            return cls.SUNNY

        if weather_string.lower() == 'rainy':
            return cls.RAINY

        return cls.SUNNY


def demo_commodity_recommendation_service_view(request):
    if request.method == 'POST':
        commodity = request.POST.get('Commodity')
        weather_string = request.POST.get('Weather')
        weather = DemoWeather.get_weather_by_string(weather_string)

        commodity_type = CommodityType.get_type_from_string(commodity)
        score_list = make_recommendation(commodity_type, weather)

        return render(request, 'datathon/demo_recommendation_result.html', {'score_list': score_list,
                                                                            'commodity': commodity})

    return render(request, 'datathon/recommendation.html')


def demo_commodity_recommendation_service(commodity_name, weather):
    commodity_type = CommodityType.get_type_from_string(commodity_name)
    pass


def make_recommendation(commodity_type, weather):
    if weather == DemoWeather.RAINY:
        query = " SELECT frequency_lt, member_serial from drink_bad_rfm "

    if weather == DemoWeather.SUNNY:
        query = " SELECT frequency_lt, member_serial from drink_good_rfm "

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query)

    freq_member_list = list(cursor)
    freq_member_list = sorted(freq_member_list,
                              key=lambda item: item[0],
                              reverse=True)
    freq_member_count = len(freq_member_list)

    recommendation_list = freq_member_list[:10]

    def _make_score_object(idx, member_uuid):
        return {
            'member_uuid': member_uuid,
            'commodity_type': commodity_type,
            'percent_to_win': 100 - round(( idx / freq_member_count ) * 100, 2),
            'phone': '09' + ''.join(str(random.randint(0, 9)) for _ in range(8))
        }

    score_list = []
    for idx, (_, member_uuid) in enumerate(recommendation_list):
        score_list.append(
            _make_score_object(idx, member_uuid)
        )

    return score_list
