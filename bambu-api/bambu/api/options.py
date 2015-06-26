"""
An API consists of a number of endpoints. Typically a model in a database has one API with two endpoints.
The API handles the CRUD operations for that model. The first endpoint is used to list a model's objects, the
second returns a specific object by ID.

The first endpoint (the list endpoint) allows for its results to be filtered by specifying querystring
parameters that map to field names. When calling the API endpoint via an HTTP request, developers can prefix a
field name with a - (minus) symbol to exlucde, rather than filter by that value. So for example, the URL
``/polls/question.json?-id=1`` would do this::

    Poll.objects.exclude(id = 1)

Submitting a 'POST' request to the first endpoint creates a new object, populated by the data submitted in
the POST.

The second endpoint (the object endpoint) takes a single required argument: the object ID, unless it has a
parent API, in which case it also requires the ID of the parent object. Submitting a 'PUT' request to this
endpoint will update the current object, and a 'DELETE' request will delete the object.

APIs are defined almost exactly likt ``ModelAdmin`` classes, complete with inlines for foreign key
relationships.

User restrictions
-----------------

By default there are no restrictions placed on endpoints, so it's completely up to you to determine whether a
particular user is permitted to update, delete or even access certain objects. You can limit access easily by
overriding the ``get_query_set()`` function within your API, but it's your responsibility to lock down the
rest.
"""

from django.conf.urls import patterns, url, include
from django.utils.functional import curry
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db import models, transaction
from django.forms import Form, ModelForm
from django.forms.models import modelform_factory
from django.http import Http404
from bambu.api import helpers
from bambu.api import decorators
from bambu.api.transformers import library
from bambu.api.exceptions import APIException

class API(object):
    """
    Defines a standard API, where the developer must specify all the URLs that make up each endpoint.
    The class is instantiated by ``bambu.api.site.register``.
    """

    parent = None
    """The parent ``API`` object (default is ``None``)"""

    form = Form
    """The ``Form`` class used to interact with this API"""

    def __init__(self, api_site):
        self.api_site = api_site

    def get_urls():
        """
        Returns a list of URL patterns, where each view is a method of this class.
        """
        return patterns('')

    @property
    def urls(self):
        return self.get_urls()

    def get_form(self, request, **kwargs):
        """
        Return an instance of a ``Form`` class that can be used to supply data to the API.
        """
        return self.form()

class ModelAPI(API):
    """
    Defines an API that derives its endpoints' URLs and functionality from a particular Django model.
    Like ``API``, it's instantiated by ``bambu.api.site.register``.
    """

    form = ModelForm
    exclude = ()
    """A tuple of field names not to expose to the API consumer"""

    fields = ()
    """A tuple of field names to expose to the API consumer"""

    inlines = []
    """A list of classes deriving from ``ModelInline`` that specify child models in foreign key relationships"""

    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    """A list of permitted HTTP verbs"""

    allowed_formats = ('xml', 'json')
    """A list of permitted data formats"""

    raw_id_fields = ()
    readonly_fields = ()
    """A tuple of fieldnames whose data cannot be modified by API consumers"""

    return_values = {}

    def __init__(self, model, api_site):
        super(ModelAPI, self).__init__(api_site)
        self.model = model
        self.inline_instances = []

        for inline_class in self.inlines:
            fks_to_parent = [
                f for f in inline_class.model._meta.fields
                if isinstance(f, models.ForeignKey) and (
                    f.rel.to == self.model
                    or f.rel.to in self.model._meta.get_parent_list()
                )
            ]

            if len(fks_to_parent) == 1:
                fk = fks_to_parent[0]
                rel_name = fk.rel.related_name or '%s_set' % (
                    inline_class.model._meta.module_name
                )

                self.inline_instances.append(
                    inline_class(
                        inline_class.model, self, fk,
                        rel_name, self.api_site
                    )
                )
            elif len(fks_to_parent) == 0:
                raise Exception(
                    '%s has no ForeignKey to %s' % (
                        inline_class.model, self.model
                    )
                )
            else:
                raise Exception(
                    '%s has more than 1 ForeignKey to %s' % (
                        inline_class.model, self.model
                    )
                )

    @property
    def list_allowed_methods(self):
        """Returns a list of the allowed HTTP verbs for object list endpoints"""
        return [m for m in self.allowed_methods if m in ('GET', 'POST')]

    @property
    def object_allowed_methods(self):
        """Returns a list of the allowed HTTP verbs for single object endpoints"""
        return [m for m in self.allowed_methods if m in ('GET', 'PUT', 'DELETE')]

    def example_object(self, index = 0):
        """Provides a dictionary of sample data used for documentation"""
        return {}

    def example_list_response(self, count = 3):
        """Provides a list of sample dictionaries by calling ``example_object`` ``count`` number of times"""
        """:param count: The number of sample objects to return"""
        return [self.example_object(i) for i in range(0, count)]

    def example_object_response(self):
        """An alias for ``example_object``"""
        return self.example_object()

    def get_urls(self):
        """
        Automatically creates URL patterns for the model the class is registered to, and then runs
        through each ``ModelInline`` specified in ``inlines`` to add its URL patterns to this list.

        It automatically provides basic descriptions for each argument, and creates required arguments
        for each inline API. For example, the 1 in the URL ``/api/polls/question/1/choices.json`` is a
        required argument for ``ChoiceInline.get_query_set()``. The relationship between the ``Choice``
        and ``Question`` models is automatically discovered and the correct name given to the argument.
        For now, the argument is always considered to be an integer (the primary key of the parent
        object).
        """

        info = self.model._meta.app_label, self.model._meta.module_name
        singular = unicode(self.model._meta.verbose_name)
        plural = unicode(self.model._meta.verbose_name_plural)

        if singular.islower():
            singular = singular.capitalize()

        if plural.islower():
            plural = plural.capitalize()

        this = self
        while this.parent:
            parent_singular = unicode(this.parent.model._meta.verbose_name)

            if parent_singular.islower():
                parent_singular = parent_singular.capitalize()

            singular = '%s: %s' % (parent_singular, singular)
            plural = '%s: %s' % (parent_singular, plural)
            this = this.parent

        plural = '%s: %s' % (self.model._meta.app_label.capitalize(), plural)
        singular = '%s: %s' % (self.model._meta.app_label.capitalize(), singular)

        plural_view = helpers.wrap_api_function(
            self.api_site, self.list_view, 1,
            self.list_allowed_methods, self.prepare_output_data,
            plural
        )

        single_view = helpers.wrap_api_function(
            self.api_site, self.object_view, 2,
            self.object_allowed_methods, self.prepare_output_data,
            singular
        )

        single_view = decorators.argument('object_id', 'id', u'The ID of the %s to return' % self.model._meta.verbose_name)(single_view)
        single_view = decorators.argument('format', 'str', u'The data format to return')(single_view)
        plural_view = decorators.argument('format', 'str', u'The data format to return')(plural_view)

        if self.fields is None or not any(self.fields):
            fields = []
        else:
            fields = list(self.fields)

        if self.exclude is None:
            exclude = []
        else:
            exclude = list(self.exclude)

        returns = {}
        for f in self.model._meta.local_fields:
            if f.name in exclude:
                continue

            if any(fields) and not f.name in fields:
                continue

            ft = 'str'
            if isinstance(f, models.IntegerField):
                ft = 'int'
            elif isinstance(f, models.DecimalField):
                ft = 'float'
            elif isinstance(f, models.BooleanField):
                ft = 'bool'
            elif isinstance(f, models.ForeignKey):
                ft = 'int'
            elif isinstance(f, models.ManyToManyField):
                ft = 'list'

            description = self.return_values.get(f.name,
                f.help_text or (u'The %s\'s %s' % (self.model._meta.verbose_name, f.verbose_name))
            )

            returns[f.name] = (ft, description)

        single_view = decorators.returns(returns)(single_view)
        plural_view = decorators.returns(returns)(plural_view)

        urlpatterns = patterns('',
            url(r'^\.(?P<format>' + '|'.join(self.allowed_formats) + ')$',
                plural_view,
                name = '%s_%s_list' % info
            ),
            url(r'^/(?P<object_id>\d+)\.(?P<format>' + '|'.join(self.allowed_formats) + ')$',
                single_view,
                name = '%s_%s_single' % info
            )
        )

        for inline in self.inline_instances:
            vn = inline.rel_field.rel.to._meta.verbose_name

            urlpatterns += patterns('',
                decorators.argument(
                    inline.rel_field.name, 'int', u'The ID of the parent %s' % vn
                )(
                    url(
                        r'^/(?P<' + inline.rel_field.name + '>\d+)/' + inline.rel_name,
                        include(inline.get_urls())
                    )
                )
            )

        return urlpatterns

    def get_form(self, request, obj = None, **kwargs):
        if self.fields is None or not any(self.fields):
            fields = None
        else:
            fields = list(self.fields)

        if self.exclude is None:
            exclude = []
        else:
            exclude = list(self.exclude)

        exclude.extend(kwargs.get("exclude", []))
        exclude.extend(self.readonly_fields)
        exclude = exclude or None

        defaults = {
            'form': self.form,
            'fields': fields,
            'exclude': exclude,
            'formfield_callback': curry(
                self.formfield_for_dbfield,
                request = request
            )
        }

        defaults.update(kwargs)
        return modelform_factory(self.model, **defaults)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """
        Works in the same way as ``django.contrib.admin.ModelAdmin`` instances.
        """

        if db_field.choices:
            return self.formfield_for_choice_field(db_field, request, **kwargs)

        if isinstance(db_field, models.ForeignKey):
            return self.formfield_for_foreignkey(db_field, request, **kwargs)

        if isinstance(db_field, models.ManyToManyField):
            return self.formfield_for_manytomany(db_field, request, **kwargs)

        return db_field.formfield(**kwargs)

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        """
        Works in the same way as ``django.contrib.admin.ModelAdmin`` instances.
        """
        return db_field.formfield(**kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Works in the same way as ``django.contrib.admin.ModelAdmin`` instances.
        """
        return db_field.formfield(**kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        Works in the same way as ``django.contrib.admin.ModelAdmin`` instances.
        """
        if not db_field.rel.through._meta.auto_created:
            return None

        return db_field.formfield(**kwargs)

    def save_form(self, request, form, obj = None):
        """Save the data from the ``Form`` instance in memory, but not to the database"""
        return form.save(commit = False)

    def save_object(self, request, obj):
        """Save the data from the object to the database"""
        obj.save()

    def prepare_initial_data(self, form_class, obj = None, **kwargs):
        """Populates the model's form with data from the specified object"""
        return helpers.form_initial_data(form_class, obj, **kwargs)

    def get_query_set(self, request, **kwargs):
        """
        Filter the API's model manager queryset using the specified kwargs. Override this function
        to limit the results returned (ie: only showing data relating to the authenticated user)
        """
        return self.model.objects.filter(**kwargs)

    def prepare_output_data(self, request, obj, max_detail_level = 1):
        """
        Transform the data from a ``Model`` instance found by ``get_query_set()`` into a dict so it
        can be serialised
        """
        return library.transform(
            obj, max_detail_level,
            fields = self.fields,
            exclude = self.exclude
        )

    def add_field_to_include_filter(self, queryset, field, value):
        """
        Filters a queryset where the value of the ``field`` column is set to that of ``value``.
        If ``value`` is a list, the query filters out any row where ``field`` contains a value
        found within the ``value`` list.
        """
        if len(value) > 1:
            return queryset.filter(
                **{
                    '%s__in' % field: value
                }
            )
        else:
            return queryset.filter(
                **{
                    field: value[0]
                }
            )

    def add_field_to_exclude_filter(self, queryset, field, value):
        """
        Excludes rows from a query where the value of the ``field`` column is set to that of ``value``.
        If ``value`` is a list, each row wherein ``field`` contains a value found in the ``value`` list
        is excluded.
        """
        if len(value) > 1:
            return queryset.exclude(
                **{
                    '%s__in' % field: value
                }
            )
        else:
            return queryset.exclude(
                **{
                    field: value[0]
                }
            )

    def list_view(self, request, **kwargs):
        """
        The main view for the first (list) endpoint. This typically accepts the 'GET' and 'POST'
        HTTP verbs.

        Where 'GET' is the verb, a queryset is generated by comgining the specified kwargs with the
        querystring, and a list of matching objects is returned.

        Where 'PUT' is the verb, a ``Form`` class is instantiated and the data from the POST added to it.
        The form is saved, and if successful, the saved object is returned. If not, an ``APIException``
        is raised, with the descriptions of the offending fields' validation exceptions contained within.
        """
        if request.method == 'GET':
            include = {}
            exclude = {}
            fields = [f.name for f in self.model._meta.local_fields]
            order_by = []
            qs = self.get_query_set(request, **kwargs)

            for key, value in request.GET.items():
                values = request.GET.getlist(key)

                if key == 'order':
                    order_by = values
                elif key.startswith('-'):
                    if not key[1:] in fields:
                        continue

                    qs = self.add_field_to_exclude_filter(qs, key[1:], values)
                else:
                    if key.startswith('+'):
                        key = key[1:]

                    if not key in fields:
                        continue

                    qs = self.add_field_to_include_filter(qs, key, values)

            if hasattr(qs.query, 'select_fields'):
                fields = [f.name for f in qs.query.select_fields] + list(qs.query.aggregate_select.keys())
            else:
                fields = [f.field.name for f in qs.query.select] + list(qs.query.aggregate_select.keys())

            if not any(fields):
                fields = [f.name for f in self.model._meta.local_fields]

            if any(include):
                qs = qs.filter(**include)

            if any(exclude):
                qs = qs.exclude(**exclude)

            if any(order_by):
                orders = []

                for order in order_by:
                    direction = ''

                    while order.startswith('-'):
                        if direction == '':
                            direction = '-'
                        else:
                            direction = ''

                        order = order[1:]

                    if order in fields or order == '?':
                        if order == '?' and direction == '-':
                            raise APIException(u'Cannot order negatively by random')
                        if any(orders):
                            raise APIException(u'Cannot order by random when already ordering by other fields')
                    else:
                        raise APIException(u'Cannot order by %s' % order)

                    if '?' in orders:
                        raise APIException(u'Cannot order by random when already ordering by other fields')

                    orders.append(direction + order)

                qs = qs.order_by(*orders)

            return qs
        elif request.method == 'POST':
            form_class = self.get_form(request)
            data = self.prepare_initial_data(form_class, **kwargs)

            for key, value in request.POST.items():
                data[key] = value

            form = form_class(data, request.FILES)
            if form.is_valid():
                obj = self.save_form(request, form)
                self.save_object(request, obj)
                return obj

            errors = []
            for error in form.non_field_errors():
                errors.append(error)

            for field in form:
                if field.errors and any(field.errors):
                    inline_errors = list([e for e in field.errors])

                    errors.append(
                        {
                            field.name: ', '.join(inline_errors)
                        }
                    )

            raise APIException(errors)

    def get_object(self, request, object_id, **kwargs):
        """
        Returns a single object by ID, with the specified kwargs also added to the query. Kwargs are most
        commonly specified where the API is a child of another.
        """
        try:
            return self.get_query_set(request, **kwargs).get(pk = object_id)
        except self.model.DoesNotExist:
            raise Http404('Object not found.')

    def object_view(self, request, object_id, **kwargs):
        """
        The view for the second (object) endpoint, wherein a 'GET' request returns an object matching the
        given ID and kwargs, a 'PUT' updates the object and a 'DELETE' removes it.

        When a 'PUT' request is given, the values of the posted data are given to a newly-instantiated
        ``Form``. If the data is correct, the updated object is returned. If invalid, an ``APIException`` is
        raised, with the descriptions of the offending fields' validation exceptions contained within.

        When a 'DELETE' request is given and the operation successful, the value 'OK' is returned.
        """
        obj = self.get_object(request, object_id, **kwargs)

        if request.method == 'DELETE':
            with transaction.commit_on_success():
                obj.delete()
                return ['OK']
        elif request.method == 'PUT':
            request.method = 'POST'
            request._load_post_and_files()
            request.method = 'PUT'

            form_class = self.get_form(request, obj)
            data = self.prepare_initial_data(form_class, obj)

            for key, value in request.POST.items():
                data[key] = value

            form = form_class(data, request.FILES, instance = obj)

            if form.is_valid():
                obj = self.save_form(request, form, obj)
                self.save_object(request, obj)
                return obj

            errors = []
            for error in form.non_field_errors():
                errors.append(error)

            for field in form:
                if field.errors and any(field.errors):
                    inline_errors = list([e for e in field.errors])

                    errors.append(
                        {
                            field.name: inline_errors
                        }
                    )

            raise Exception(errors)

        return obj

class ModelInline(ModelAPI):
    """
    A child API. This does not need to be registered with an API site; instead it should be referenced in the
    ``inlines`` property of the parent ``ModelAPI`` class.
    """

    def __init__(self, model, parent, rel_field, rel_name, api_site):
        super(ModelInline, self).__init__(model, api_site)
        self.parent = parent
        self.rel_field = rel_field
        self.rel_name = rel_name

    def prepare_initial_data(self, form_class, obj = None, **kwargs):
        data = helpers.form_initial_data(form_class, obj)
        if not obj:
            data[self.rel_field.name] = kwargs.get(self.rel_field.name)

        return data
