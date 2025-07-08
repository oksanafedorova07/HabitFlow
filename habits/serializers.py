from rest_framework import serializers

from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = "__all__"
        read_only_fields = ("user",)

    def validate(self, data):
        # related_habit и reward не могут быть заполнены одновременно
        if data.get("related_habit") and data.get("reward"):
            raise serializers.ValidationError(
                "Нельзя одновременно указывать связанную привычку и вознаграждение."
            )
        # Время выполнения должно быть не больше 120 секунд
        if data.get("duration", 0) > 120:
            raise serializers.ValidationError(
                "Время выполнения не может превышать 120 секунд."
            )
        # В связанные привычки могут попадать только привычки с признаком приятной привычки
        if data.get("related_habit") and not data["related_habit"].is_pleasant:
            raise serializers.ValidationError(
                "В связанные привычки могут попадать только приятные привычки."
            )
        # У приятной привычки не может быть вознаграждения или связанной привычки
        if data.get("is_pleasant") and (
            data.get("reward") or data.get("related_habit")
        ):
            raise serializers.ValidationError(
                "У приятной привычки не может быть вознаграждения или связанной привычки."
            )
        # Нельзя выполнять привычку реже, чем 1 раз в 7 дней
        if not (1 <= data.get("period", 1) <= 7):
            raise serializers.ValidationError(
                "Периодичность должна быть от 1 до 7 дней."
            )
        return data
