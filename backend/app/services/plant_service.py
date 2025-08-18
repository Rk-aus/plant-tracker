import psycopg2 as pg2

class PlantService:
    def __init__(self, conn, plant_dao):
        self.conn = conn
        self.plant_dao = plant_dao

    def add_plant_with_related(self, plant_name_id, family_id, location_id, image_path, plant_date=None):
        try:
            plant_id = self.plant_dao.insert(
                self.conn, plant_name_id, family_id, location_id, image_path, plant_date
            )
            self.conn.commit()
            return plant_id
        except pg2.Error as e:
            self.conn.rollback()  
            raise