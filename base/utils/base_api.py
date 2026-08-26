from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT


class CrudApi(APIView):
    serializer_class = None
    queryset = None

    def get_object(self, request, *args, **kwargs):
        return get_object_or_404(self.queryset, pk=kwargs['pk'])

    def get(self, request, *args, **kwargs):
        if 'pk' in kwargs:
            queryset = self.get_object(request, *args, **kwargs)
            serializer = self.serializer_class(queryset)
            return Response(serializer.data, status=HTTP_200_OK)
        queryset = self.queryset.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        if 'pk' in kwargs:
            queryset = self.get_object(request, *args, **kwargs)
            serializer = self.serializer_class(queryset, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        if 'pk' in kwargs:
            queryset = self.get_object(request, *args, **kwargs)
            serializer = self.serializer_class(queryset, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        if 'pk' in kwargs:
            queryset = self.get_object(request, *args, **kwargs)
            queryset.delete()
            return Response(status=HTTP_204_NO_CONTENT)
