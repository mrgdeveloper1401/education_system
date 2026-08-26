from treebeard.mp_tree import MP_NodeManager, MP_NodeQuerySet
from django.utils import timezone


class SoftTreeQuerySet(MP_NodeQuerySet):
    def delete(self, *args, **kwargs):
        return super().update(is_deleted=True, deleted_at=timezone.now())


class PublishTreeManager(MP_NodeManager):
    def get_queryset(self):
        return SoftTreeQuerySet(self.model, using=self._db).filter(is_deleted=False)
