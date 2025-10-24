from app.extensions import ma
from app.models import PartDescriptions, Parts

class PartDescriptionsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PartDescriptions

part_description_schema = PartDescriptionsSchema()
part_descriptions_schema = PartDescriptionsSchema(many=True)

class PartsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Parts
        include_fk=True

part_schema = PartsSchema()
parts_schema = PartsSchema(many=True)