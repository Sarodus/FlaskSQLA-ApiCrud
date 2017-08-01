from flask import request, current_app

from flask_restful import Api, Resource

from flask_sqlalchemy import Model
from sqlalchemy.orm.attributes import set_attribute
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import joinedload

from .utils import custom_json_output


class APIManager(Api):
    def __init__(self, app, db_session=None, **kwargs):
        self.db_session = db_session
        super(APIManager, self).__init__(app, **kwargs)

    def init_app(self, app, db_session=None):
        super(APIManager, self).init_app(app)
        self.db_session = db_session or self.db_session
        if self.db_session is None:
            raise TypeError('APIManager: db_session parameter is required!')
        self.representations.update({
            'application/json': custom_json_output
        })

    def register(self, model, route_name=None, **kwargs):
        route_name = route_name or model.__tablename__

        kwargs['model'] = model
        kwargs['db_session'] = self.db_session
        resource = type('ResourceCRUD_%s' % route_name, (ResourceCRUD,), kwargs)
        resource_item = type('ResourceCRUDItem_%s' % route_name, (ResourceCRUDItem,), kwargs)

        self.add_resource(
            resource,
            '/%s/' % route_name,
            endpoint='api.%s' % route_name
        )
    
        self.add_resource(
            resource_item,
            '/%s/<int:id_item>' % route_name,
            endpoint='api.item_%s' % route_name
        )
    
        self.add_resource(
            resource_item,
            '/%s/<int:id_item>/<string:relation>/' % route_name,
            endpoint='api.item_relation_%s' % route_name
        )


class ResourceNotFound(Exception):
    """Raised when looking for an item and is not found!

    Implement your flask custom error handler!
    As example:
    @app.errorhandler(ResourceNotFound)
    def resourcenotfound_handler(e):
        return jsonify(
            id_item=e.message,
            error="Not found",
            code=404
        ), 404
    """


class CRUD:
    """
    :param model: SQLAlchemy model.
    :param db_session: SQLAlchemy db session.
    :param fields: Field names of the table you want to retrieve,
        can be columns or relationships, for customize relationship fields see
        `relations_fields` param.
        The fields default value is the model's Columns without relationships.
        The default result from the relationship fields is also it's columns
        without inner relationships.

    :param extra_fields: Used to extend the param `fields`.
    :joined_load_models: relationships to load the list with joins
    :param relations_fields: dict with the key as tablename,
        and the value as fields list|tuple|set,
        also you can set multiple relationships/sub-relationsips
    """
    model = None
    db_session = None
    fields = None
    extra_fields = None
    relations_fields = None
    joined_load_models = None

    def __init__(self):
        if self.model is None:
            raise TypeError('arg model is required')

        if self.db_session is None:
            raise TypeError('arg db_session is required')

        if self.joined_load_models is None:
            self.joined_load_models = {}

        self.table_fields = set(self.model.__table__.columns.keys())

        if self.fields is None:
            self.fields = self.table_fields
        else:
            self.fields = set(self.fields)

        if self.extra_fields is not None:
            self.fields = self.fields | set(self.extra_fields)

    def get_query_list(self):
        """Used in the ResourceCRUD for getting the list query"""
        query = self.model.query
        filters = self._get_args()
        if filters:
            query = query.filter_by(**filters)
        if self.joined_load_models:
            query = query.options(*map(joinedload, self.joined_load_models))
        return query

    def _process_row(self, row, fields):
        return {field: self._getattr(row, field) for field in fields}

    def _out(self, query, fields):
        result = []
        for row in query:
            result.append(self._process_row(row, fields))
        return result

    def _getattr(self, row, field):
        if '.' in field:
            field, more = field.split('.', 1)
            attr = getattr(row, field)
            return self._getattr(attr, more)
        attr = getattr(row, field)
        if isinstance(attr, list):
            if attr:
                table = attr[0].__table__
                fields = self.relations_fields.get(table.name, table.columns.keys())
                return self._out(attr, fields)
            return []
        elif isinstance(attr, Model):
            table = attr.__table__
            fields = self.relations_fields.get(table.name, table.columns.keys())
            return {f: self._getattr(attr, f) for f in fields}
        return attr

    def _get_query_pk(self, id_item):
        # TODO, support multiple PK
        pk = [key.name for key in inspect(self.model).primary_key][0]
        return self.model.query.filter_by(**{pk: id_item})

    def _get_item(self, id_item):
        item = self.model.query.get(id_item)
        if not item:
            raise ResourceNotFound(id_item)
        return item

    def _get_payload(self):
        json = dict(request.json or {})
        return self._filter_with_table(json)

    def _get_args(self):
        json = dict(request.args or {})
        return self._filter_with_table(json)

    def _filter_with_table(self, json, fields=None):
        # TODO, TYPE filters, true/false, int, ... with Table typing
        for key in json.viewkeys() - (fields or self.table_fields):
            current_app.logger.warning(
                'Unwanted KEY[%s]=%s for table[%s] METHOD[%s]',
                key,
                json[key],
                self.model.__name__,
                request.method
            )
            del json[key]
        return json


class ResourceCRUDItem(CRUD, Resource):
    """flask_restful with id_item routes implementation"""
    
    def get(self, id_item, relation=None):
        """Get item"""
        item = self._get_item(id_item)
        if relation:
            return self._getattr(item, relation)
        return self._process_row(item, self.fields)

    def put(self, id_item):
        """Update"""
        payload = self._get_payload()
        # Validate?
        result = self._get_query_pk(id_item).update(payload)
        self.db_session.commit()
        return self.get(id_item)

    def delete(self, id_item):
        """Delete id_item"""
        n = self._get_query_pk(id_item).delete()
        self.db_session.commit()
        return dict(success=bool(n), items_deleted=n)

    def post(self, id_item, relation):
        """Custom method for updating many-to-many relations"""
        item = self._get_item(id_item)
        rel = inspect(self.model).relationships.get(relation)

        if not rel:
            raise Exception('Model %s has no relation %s' % (self.model, relation))

        if not rel.uselist:
            raise Exception('Method post(id_item, relation) is only for many-to-many relations.')

        if not type(request.json) is list:
            raise Exception('You may provide an array value in request.json')

        cls = rel.mapper.class_
        json = list(request.json)
        fields = rel.mapper.columns.keys()

        # Delete current items
        for r in getattr(item, relation):
            self.db_session.delete(r)

        items_to_set = [cls(**self._filter_with_table(d, fields)) for d in json]
        for r in items_to_set:
            self.db_session.add(r)
        set_attribute(item, relation, items_to_set)
        self.db_session.commit()
        return self.get(id_item)


class  ResourceCRUD(CRUD, Resource):
    """flask_restful with no id_item routes implementation"""

    def get(self):
        """Get list"""
        print 'DAFUQ', self.model, self.fields
        return self._out(self.get_query_list(), self.fields)

    def post(self):
        """Create"""
        payload = self._get_payload()
        # Validate?
        item = self.model(**payload)
        self.db_session.add(item)
        self.db_session.commit()
        return self._process_row(self._get_item(item.id), self.fields)
