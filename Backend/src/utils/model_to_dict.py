from sqlalchemy.orm import class_mapper
# just a function to convert the tasks retrieved into a dictionary because the direct function is not working
def model_to_dict(model):
    return {c.key: getattr(model, c.key) 
            for c in class_mapper(model.__class__).columns}