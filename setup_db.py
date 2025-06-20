from src.database.db import get_db
from app import create_app

app = create_app()

with app.app_context():
    db = get_db()
    from src.models.users import UserModel
    from src.models.apiary import ApiaryModel
    from src.models.beehive import BeehiveModel
    from src.models.inspection import InspectionModel
    from src.models.apiary_access import ApiaryAccessModel
    from src.models.questions import QuestionModel
    from src.models.inventory import InventoryModel

    UserModel.init_db(db)
    ApiaryModel.init_db(db)
    QuestionModel.init_db(db)
    InventoryModel.init_db(db)
    BeehiveModel.init_db(db)
    InspectionModel.init_db(db)
    ApiaryAccessModel.init_db(db)
    db.commit()
    print("Base de datos inicializada")
