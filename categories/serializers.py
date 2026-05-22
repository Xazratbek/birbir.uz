from rest_framework import serializers
from .models import Category
from rest_framework.response import Response
from rest_framework import status

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id','name','slug','parent','icon','children']

    def get_children(self, obj):
        if obj.categories.exists():
            children_queryset = obj.categories.all()
            serializer = CategorySerializer(children_queryset, many=True, context=self.context)
            return serializer.data