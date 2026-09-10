from rest_framework import serializers
from django.contrib.auth.models import User


class UsuarioSerializer(serializers.ModelSerializer):
    rol = serializers.SerializerMethodField()
    docente_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'rol', 'docente_id']

    def get_rol(self, obj):
        grupo = obj.groups.first()
        return grupo.name if grupo else None

    def get_docente_id(self, obj):
        return obj.docente.id if hasattr(obj, 'docente') else None