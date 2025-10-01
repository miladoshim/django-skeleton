from django.db.models import Manager, Q

class PostManager(Manager):
    def search_posts(self, query):
        lookup = Q(title__icontains=query) | Q(body__icontains=query)
        return self.get_queryset().filter(lookup)