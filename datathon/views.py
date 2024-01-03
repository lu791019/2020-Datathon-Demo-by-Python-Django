import uuid
import enum
import random

import scipy.stats

from django.shortcuts import render

class CommodityType(enum.Enum):
    FOOD = 'FOOD'
    DRINK = 'DRINK'

    @classmethod
    def get_type_from_string(cls, commodity_name):
        return CommodityType.DRINK


class Weather:

    weather_series = {
        'hot_day': (1, 0.5, 0.5, 1, 0),
        'rainy_day': (0, 1, 1, 0, 1),
        'good_day': (0.5, 0.5, 0.5, 0.5, 0)
    }

    def __init__(self, weather_string):
        for key in self.weather_series:
            if weather_string == key:
                self.weather_type = key
                self.weather_indexes = self.weather_series[key]


        self.temperature = self.weather_indexes[0]
        self.humidity = self.weather_indexes[1]
        self.relative_humidity = self.weather_indexes[2]
        self.sunshine_coef = self.weather_indexes[3]
        self.rainfall = self.weather_indexes[4]

    def __dict__(self):
        return {
            'type': self.weather_type,

            'temperature': self.temperature,
            'humidity': self.humidity,
            'relative_humidity': self.relative_humidity,
            'sunshine_coef': self.sunshine_coef,
            'rainfall': self.rainfall,
        }


def make_recommendation_by_commodity_and_weather(commodity_type:str, weather):

    return [uuid.uuid4() for _ in range(random.randint(7, 13))]


def query_score_for_each_weather_coef_by_commodity_type(commodity_type, member_uuid):

    def _mock_normal_value(mean, sigma):
        # TODO this should be replace by z-score
        value = random.normalvariate(mean, sigma)
        return round(value, 2)

    def _mock_phone():
        return '09' + ''.join(str(random.randint(0, 9)) for _ in range(8))

    return {
        'member_uuid': member_uuid,
        'commodity_type': commodity_type,
        'phone': _mock_phone(),
        'temperature': _mock_normal_value(2, 0.3),
        'humidity': _mock_normal_value(2, 0.3),
        'relative_humidity': _mock_normal_value(2, 0.3),
        'sunshine_coef': _mock_normal_value(2, 0.3),
        'rainfall': _mock_normal_value(2, 0.3),
    }


def commodity_recommendation_service_view(request):
    if request.method == 'POST':
        commodity = request.POST.get('Commodity')
        weather_string = request.POST.get('Weather')
        weather = Weather(weather_string)

        score_list = commodity_recommendation_service(commodity, weather)
        score_list = calculate_chance_to_buy_by_z_score(score_list, weather)
        score_list = sorted(score_list, key=lambda item: item['mean_z_score'], reverse=True)
        return render(request, 'datathon/recommended_member_result.html', {'score_list': score_list,
                                                                           'commodity': commodity,
                                                                           'weather': weather.__dict__()})

    return render(request, 'datathon/recommendation.html')


def commodity_recommendation_service(commodity_name, weather):

    commodity_type = CommodityType.get_type_from_string(commodity_name)

    member_uuids = make_recommendation_by_commodity_and_weather(commodity_type, weather)
    score_list = [
        query_score_for_each_weather_coef_by_commodity_type(commodity_type, member_uuid)
        for member_uuid in member_uuids
    ]

    return score_list


def calculate_chance_to_buy_by_z_score(score_list, weather):
    for item_of_score_list in score_list:
        cross_z_score = 0

        item_of_score_list['temperature'] *= weather.temperature
        cross_z_score += item_of_score_list['temperature']

        item_of_score_list['humidity'] *= weather.humidity
        cross_z_score += item_of_score_list['humidity']

        item_of_score_list['relative_humidity'] *= weather.relative_humidity
        cross_z_score += item_of_score_list['relative_humidity']

        item_of_score_list['sunshine_coef'] *= weather.sunshine_coef
        cross_z_score += item_of_score_list['sunshine_coef']

        item_of_score_list['rainfall'] *= weather.rainfall
        cross_z_score += item_of_score_list['rainfall']


        mean_z_score = cross_z_score / sum(weather.weather_indexes)
        mean_z_score = round(mean_z_score, 2)

        chance_to_buy_over_total_members \
            = 1 - scipy.stats.norm.sf(abs(mean_z_score))

        item_of_score_list['mean_z_score'] = mean_z_score
        item_of_score_list['chance_to_buy_over_total_members'] \
            = round(chance_to_buy_over_total_members * 100, 2)

    return score_list
